"""
Analytics Engine
================
Pure-Python analytics engine that generates all insights from a DataFrame.
No database dependency — works directly with parsed CSV data.
"""

import json
import numpy as np
import pandas as pd


def _safe(val):
    """Convert numpy types to native Python for JSON serialization."""
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        f = float(val)
        if np.isnan(f): return None
        return f
    if isinstance(val, np.ndarray):
        return val.tolist()
    if isinstance(val, dict):
        return {k: _safe(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_safe(v) for v in val]
    return val


def compute_class_stats(df):
    """Overall class statistics."""
    if df.empty: return {}
    total_students = df["student_name"].nunique()
    total_subjects = df["subject"].nunique()
    avg_marks = round(df["marks"].mean(), 1) if "marks" in df.columns else 0
    avg_pct = 0
    if "marks" in df.columns and "max_marks" in df.columns:
        df_valid = df[df["max_marks"] > 0]
        if not df_valid.empty:
            avg_pct = round((df_valid["marks"] / df_valid["max_marks"] * 100).mean(), 1)
    pass_count = 0
    fail_count = 0
    if "marks" in df.columns and "max_marks" in df.columns:
        pcts = df["marks"] / df["max_marks"].replace(0, 1) * 100
        pass_count = int((pcts >= 40).sum())
        fail_count = int((pcts < 40).sum())
    avg_att = None
    if "attendance" in df.columns:
        att_valid = df["attendance"].dropna()
        if len(att_valid): avg_att = round(att_valid.mean(), 1)
    return {
        "total_students": total_students, "total_subjects": total_subjects,
        "total_records": len(df), "avg_marks": avg_marks, "avg_percentage": avg_pct,
        "pass_count": pass_count, "fail_count": fail_count,
        "pass_rate": round(pass_count/(pass_count+fail_count)*100,1) if (pass_count+fail_count) else 0,
        "avg_attendance": avg_att,
    }


def subject_wise_stats(df):
    """Per-subject statistics."""
    if df.empty or "subject" not in df.columns: return []
    results = []
    for subj, grp in df.groupby("subject"):
        avg = round(grp["marks"].mean(), 1)
        mx = grp["max_marks"].iloc[0] if "max_marks" in grp.columns else 100
        pct = round(avg / mx * 100, 1) if mx else 0
        att = None
        if "attendance" in grp.columns:
            av = grp["attendance"].dropna()
            if len(av): att = round(av.mean(), 1)
        pcts = grp["marks"] / grp["max_marks"].replace(0,1) * 100
        results.append({
            "subject": subj, "avg_marks": avg, "max_marks": mx,
            "avg_percentage": pct, "student_count": len(grp),
            "highest": round(grp["marks"].max(),1), "lowest": round(grp["marks"].min(),1),
            "pass_count": int((pcts>=40).sum()), "fail_count": int((pcts<40).sum()),
            "avg_attendance": att,
        })
    return sorted(results, key=lambda x: x["avg_percentage"], reverse=True)


def find_toppers(df, n=10):
    """Top N students by average percentage."""
    if df.empty: return []
    student_stats = []
    for name, grp in df.groupby("student_name"):
        pcts = grp["marks"] / grp["max_marks"].replace(0,1) * 100
        avg_pct = round(pcts.mean(), 1)
        subjects = grp["subject"].tolist()
        marks_list = [{
            "subject": r["subject"], "marks": r["marks"],
            "max_marks": r.get("max_marks",100),
            "percentage": round(r["marks"]/max(r.get("max_marks",100),1)*100,1)
        } for _, r in grp.iterrows()]
        att = None
        if "attendance" in grp.columns:
            av = grp["attendance"].dropna()
            if len(av): att = round(av.mean(),1)
        student_stats.append({
            "name": name, "avg_percentage": avg_pct,
            "subjects_count": len(subjects), "avg_attendance": att,
            "marks_detail": marks_list,
        })
    student_stats.sort(key=lambda x: x["avg_percentage"], reverse=True)
    for i, s in enumerate(student_stats[:n]): s["rank"] = i + 1
    return student_stats[:n]


def find_weak_students(df, threshold=40):
    """Students with avg below threshold."""
    if df.empty: return []
    weak = []
    for name, grp in df.groupby("student_name"):
        pcts = grp["marks"] / grp["max_marks"].replace(0,1) * 100
        avg_pct = round(pcts.mean(), 1)
        if avg_pct < threshold:
            weak_subjs = []
            for _, r in grp.iterrows():
                p = round(r["marks"]/max(r.get("max_marks",100),1)*100,1)
                if p < threshold:
                    weak_subjs.append({"subject": r["subject"], "percentage": p})
            att = None
            if "attendance" in grp.columns:
                av = grp["attendance"].dropna()
                if len(av): att = round(av.mean(),1)
            severity = "critical" if avg_pct < 25 else "warning" if avg_pct < 35 else "watch"
            weak.append({
                "name": name, "avg_percentage": avg_pct, "severity": severity,
                "weak_subjects": weak_subjs, "avg_attendance": att,
            })
    return sorted(weak, key=lambda x: x["avg_percentage"])


def attendance_vs_marks(df):
    """Attendance vs marks correlation data for scatter plot."""
    if df.empty or "attendance" not in df.columns: return {"correlation": None, "data": []}
    valid = df.dropna(subset=["attendance","marks"])
    if len(valid) < 3: return {"correlation": None, "data": []}
    corr = round(valid["attendance"].corr(valid["marks"]), 3)
    data = [{"name": r.get("student_name",""), "subject": r.get("subject",""),
             "attendance": r["attendance"], "marks": r["marks"]}
            for _, r in valid.iterrows()]
    return {"correlation": corr, "data": data[:200]}


def grade_distribution(df):
    """Grade counts per subject."""
    if df.empty or "grade" not in df.columns: return {}
    result = {}
    for subj, grp in df.groupby("subject"):
        counts = grp["grade"].value_counts().to_dict()
        result[subj] = {str(k): int(v) for k, v in counts.items()}
    return result


def student_risk_assessment(df):
    """Combine marks + attendance to flag at-risk students."""
    if df.empty: return []
    risks = []
    for name, grp in df.groupby("student_name"):
        pcts = grp["marks"] / grp["max_marks"].replace(0,1) * 100
        avg_pct = round(pcts.mean(), 1)
        att = None
        if "attendance" in grp.columns:
            av = grp["attendance"].dropna()
            if len(av): att = round(av.mean(),1)
        risk = "safe"
        reasons = []
        if avg_pct < 30:
            risk = "critical"; reasons.append("Very low marks")
        elif avg_pct < 45:
            risk = "warning"; reasons.append("Below passing threshold")
        elif avg_pct < 60:
            risk = "watch"; reasons.append("Below average performance")
        if att is not None and att < 50:
            if risk == "safe": risk = "warning"
            elif risk == "watch": risk = "warning"
            reasons.append("Very low attendance")
        elif att is not None and att < 75:
            if risk == "safe": risk = "watch"
            reasons.append("Low attendance")
        if att is not None and att >= 80 and avg_pct < 40:
            reasons.append("High attendance but low marks — may need academic support")
        risks.append({
            "name": name, "avg_percentage": avg_pct, "avg_attendance": att,
            "risk_level": risk, "reasons": reasons,
        })
    order = {"critical":0, "warning":1, "watch":2, "safe":3}
    return sorted(risks, key=lambda x: (order.get(x["risk_level"],3), x["avg_percentage"]))


def generate_recommendations(df):
    """Generate actionable recommendations."""
    if df.empty: return []
    recs = []
    stats = compute_class_stats(df)
    if stats.get("avg_percentage",0) < 50:
        recs.append({"type":"danger","title":"🚨 Class Average Below 50%",
            "text":f"Overall average is {stats['avg_percentage']}%. Consider reviewing teaching methods and providing extra support."})
    elif stats.get("avg_percentage",0) < 65:
        recs.append({"type":"warning","title":"📊 Class Average Needs Improvement",
            "text":f"Overall average is {stats['avg_percentage']}%. Focus on weak areas."})
    else:
        recs.append({"type":"success","title":"✅ Good Class Performance",
            "text":f"Overall average is {stats['avg_percentage']}%. Keep up the good work!"})
    subj_stats = subject_wise_stats(df)
    for s in subj_stats:
        if s["avg_percentage"] < 40:
            recs.append({"type":"danger","title":f"⚠️ Critical: {s['subject']} — {s['avg_percentage']}%",
                "text":f"{s['subject']} has very low scores. {s['fail_count']} students failing."})
        elif s["avg_percentage"] < 55:
            recs.append({"type":"warning","title":f"📋 Needs Work: {s['subject']} — {s['avg_percentage']}%",
                "text":f"Below average in {s['subject']}. Consider remedial sessions."})
    weak = find_weak_students(df)
    if weak:
        recs.append({"type":"warning","title":f"👥 {len(weak)} Students At Risk",
            "text":"These students need immediate attention: " + ", ".join(w["name"] for w in weak[:5])})
    if stats.get("avg_attendance") and stats["avg_attendance"] < 70:
        recs.append({"type":"warning","title":"📅 Low Overall Attendance",
            "text":f"Average attendance is {stats['avg_attendance']}%. Consider engagement strategies."})
    corr = attendance_vs_marks(df)
    if corr["correlation"] is not None and corr["correlation"] > 0.3:
        recs.append({"type":"success","title":"📈 Attendance-Marks Correlation",
            "text":f"Positive correlation of {corr['correlation']} between attendance and marks. Encourage attendance."})
    return recs


def get_full_analytics(df):
    """Generate complete analytics package from a DataFrame."""
    result = {
        "class_stats": compute_class_stats(df),
        "subject_stats": subject_wise_stats(df),
        "toppers": find_toppers(df),
        "weak_students": find_weak_students(df),
        "attendance_correlation": attendance_vs_marks(df),
        "grade_distribution": grade_distribution(df),
        "risk_assessment": student_risk_assessment(df),
        "recommendations": generate_recommendations(df),
    }
    return _safe(result)
