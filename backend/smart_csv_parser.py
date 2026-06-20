"""
Smart CSV Parser
================
Intelligently parses uploaded CSV files by:
- Fuzzy-matching column names to standard fields
- Supporting wide-form CSVs (one column per subject)
- Validating data and filling missing values
- Returning structured results with warnings
"""

import io, re
import pandas as pd
import numpy as np

# Column name aliases for fuzzy matching
COLUMN_ALIASES = {
    "student_name": ["name","student_name","student","full_name","learner","std_name","candidate"],
    "usn": ["usn","roll_number","roll_no","roll","enrollment","id_number","reg_no","registration","prn","seat_no"],
    "subject": ["subject","course","subject_name","paper","module","course_name","sub"],
    "marks": ["marks","score","obtained","marks_obtained","marks_scored","obtained_marks","scored"],
    "max_marks": ["max_marks","maximum","out_of","maximum_marks","full_marks","max_score"],
    "attendance": ["attendance","attendance_%","attendance_percent","attendance_percentage","present_%","att","attend"],
    "study_hours": ["study_hours","hours","self_study","study_time","study_hrs","hours_studied"],
    "grade": ["grade","letter_grade","result","grade_letter","grading","final_grade"],
}

# Extra columns preserved as-is (not renamed, but kept in output)
EXTRA_COLUMNS = [
    "assignment_score", "internal_marks", "semester", "section",
    "performance_status", "prev_sem_marks", "final_marks",
]

class ParseResult:
    def __init__(self):
        self.df = None
        self.column_mapping = {}
        self.warnings = []
        self.errors = []
        self.row_count = 0
        self.student_count = 0
        self.subject_count = 0
        self.is_wide_form = False
        self.detected_subjects = []
        self.records = []

    @property
    def success(self):
        return self.df is not None and len(self.errors) == 0

    def to_dict(self):
        return {
            "success": self.success, "row_count": self.row_count,
            "student_count": self.student_count, "subject_count": self.subject_count,
            "is_wide_form": self.is_wide_form, "column_mapping": self.column_mapping,
            "detected_subjects": self.detected_subjects,
            "warnings": self.warnings, "errors": self.errors,
        }

def _normalize_col(c):
    return re.sub(r'\s+', '_', str(c).strip().lower())

def _detect_columns(columns):
    """Map CSV columns to standard fields. Exact matches first, then fuzzy."""
    mapping = {}
    used = set()
    # Pass 1: exact matches (column name equals field name)
    for col in columns:
        if col in COLUMN_ALIASES and col not in used:
            mapping[col] = col
            used.add(col)
    # Pass 2: alias matching for unmapped columns
    for col in columns:
        if col in mapping: continue
        for field, aliases in COLUMN_ALIASES.items():
            if field in used: continue
            if col in aliases or col.replace("_","") in [a.replace("_","") for a in aliases]:
                mapping[col] = field
                used.add(field)
                break
    return mapping

def _get_mapped(mapping, field):
    for k,v in mapping.items():
        if v == field: return k
    return None

def _is_numeric(series):
    try:
        n = pd.to_numeric(series, errors="coerce")
        return n.notna().sum() / max(len(series),1) > 0.5
    except: return False

def _compute_grade(marks, max_marks):
    if marks is None or max_marks is None or max_marks == 0: return "N/A"
    try: pct = float(marks)/float(max_marks)*100
    except: return "N/A"
    if pct>=90: return "A+"
    if pct>=80: return "A"
    if pct>=70: return "B+"
    if pct>=60: return "B"
    if pct>=50: return "C"
    if pct>=40: return "D"
    return "F"

def _clean_df(df, result):
    if "marks" in df.columns:
        df["marks"] = pd.to_numeric(df["marks"], errors="coerce")
        bad = df["marks"].isna().sum()
        if bad: result.warnings.append(f"{bad} rows had non-numeric marks (set to 0).")
        df["marks"] = df["marks"].fillna(0)
    if "max_marks" in df.columns:
        df["max_marks"] = pd.to_numeric(df["max_marks"], errors="coerce").fillna(100)
    else:
        df["max_marks"] = 100
    if "marks" in df.columns and "max_marks" in df.columns:
        over = (df["marks"]>df["max_marks"]).sum()
        if over: result.warnings.append(f"{over} rows have marks > max_marks (capped).")
        df["marks"] = df[["marks","max_marks"]].min(axis=1)
    if "attendance" in df.columns:
        df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce")
        miss = df["attendance"].isna().sum()
        if miss: result.warnings.append(f"{miss} rows missing attendance (shows N/A).")
    else:
        df["attendance"] = np.nan
        result.warnings.append("No attendance column. Shows as N/A.")
    if "study_hours" in df.columns:
        df["study_hours"] = pd.to_numeric(df["study_hours"], errors="coerce").fillna(0)
    else:
        df["study_hours"] = 0
    if "student_name" in df.columns:
        df["student_name"] = df["student_name"].astype(str).str.strip()
        mask = df["student_name"].isin(["","nan","None"])
        if mask.sum(): 
            result.warnings.append(f"{mask.sum()} empty student names auto-filled.")
            df.loc[mask,"student_name"] = [f"Unknown_{i}" for i in range(mask.sum())]
    if "subject" in df.columns:
        df["subject"] = df["subject"].astype(str).str.strip()
    if "usn" in df.columns:
        # Guard: ensure it's a Series not DataFrame (duplicate col protection)
        if isinstance(df["usn"], pd.DataFrame):
            df = df.loc[:, ~df.columns.duplicated(keep='first')]
        if "usn" in df.columns:
            df["usn"] = df["usn"].astype(str).str.strip()
            df.loc[df["usn"].isin(["","nan","None"]),"usn"] = None
    if "grade" not in df.columns: df["grade"] = None
    df = df.dropna(subset=["student_name","subject"], how="all")
    if "student_name" in df.columns and "subject" in df.columns:
        dupes = df.duplicated(subset=["student_name","subject"], keep="last").sum()
        if dupes: result.warnings.append(f"{dupes} duplicate entries (keeping latest).")
        df = df.drop_duplicates(subset=["student_name","subject"], keep="last")
    return df.reset_index(drop=True)

def parse_csv(file_content, filename="upload.csv"):
    result = ParseResult()
    try:
        df = pd.read_csv(io.StringIO(file_content), sep=None, engine="python")
    except Exception as e:
        result.errors.append(f"Could not parse CSV: {e}")
        return result
    if df.empty:
        result.errors.append("CSV file is empty.")
        return result
    df.columns = [_normalize_col(c) for c in df.columns]
    mapping = _detect_columns(df.columns.tolist())
    result.column_mapping = mapping
    has_subj = "subject" in mapping.values()
    has_marks = "marks" in mapping.values()
    if has_subj and has_marks:
        result.is_wide_form = False
        rename = {k:v for k,v in mapping.items()}
        df = df.rename(columns=rename)
        if "student_name" not in df.columns:
            result.warnings.append("No name column; using row index.")
            df["student_name"] = [f"Student_{i+1}" for i in range(len(df))]
        df = _clean_df(df, result)
    else:
        name_col = _get_mapped(mapping, "student_name")
        if name_col:
            mapped_cols = set(mapping.keys())
            pot_subjs = [c for c in df.columns if c not in mapped_cols and _is_numeric(df[c])]
            if pot_subjs:
                result.is_wide_form = True
                result.detected_subjects = pot_subjs
                rename = {k:v for k,v in mapping.items()}
                df = df.rename(columns=rename)
                id_cols = [c for c in df.columns if c not in pot_subjs]
                result.warnings.append(f"Wide-form CSV: {len(pot_subjs)} subject columns detected.")
                df = df.melt(id_vars=id_cols, value_vars=pot_subjs, var_name="subject", value_name="marks")
                df["subject"] = df["subject"].str.replace("_"," ").str.title()
                if "max_marks" not in df.columns: df["max_marks"] = 100
                df = df.dropna(subset=["marks"])
                if "student_name" not in df.columns:
                    df["student_name"] = [f"Student_{i+1}" for i in range(len(df))]
                df = _clean_df(df, result)
            else:
                result.errors.append("Cannot detect format. Need 'subject'+'marks' or numeric subject columns.")
                return result
        else:
            result.errors.append("No student name column found.")
            return result
    if df is None or df.empty:
        result.errors.append("No valid records after parsing.")
        return result
    if "grade" not in df.columns or df["grade"].isna().all():
        df["grade"] = df.apply(lambda r: _compute_grade(r.get("marks"), r.get("max_marks",100)), axis=1)
    result.df = df
    result.row_count = len(df)
    result.student_count = df["student_name"].nunique() if "student_name" in df.columns else 0
    result.subject_count = df["subject"].nunique() if "subject" in df.columns else 0
    if not result.detected_subjects and "subject" in df.columns:
        result.detected_subjects = df["subject"].dropna().unique().tolist()
    result.records = df.where(df.notna(), None).to_dict(orient="records")
    return result
