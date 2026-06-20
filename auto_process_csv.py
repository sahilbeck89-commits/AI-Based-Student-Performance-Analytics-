"""
auto_process_csv.py
-------------------
Standalone CLI script to import a CSV file directly into the database.

Usage:
    python auto_process_csv.py students_50.csv
    python auto_process_csv.py path/to/any_file.csv

CSV must have columns: name, subject, marks
Optional columns     : max_marks, study_hours, attendance
"""

import sys
import os
import pandas as pd
import sqlite3

# ── Locate the database ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "backend", "database.db")


def get_db():
    conn = sqlite3.connect(DATABASE, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def clear_and_reload(df: pd.DataFrame) -> dict:
    """Clear existing marks and AUTO-* students, then load new data from df.
    Returns a summary dict compatible with the CSV uploader UI.
    """
    conn = get_db()
    cursor = conn.cursor()

    # 1️⃣ Wipe previous imported data
    cursor.execute("DELETE FROM marks")
    cursor.execute("DELETE FROM students WHERE roll_number LIKE 'AUTO-%'")
    conn.commit()

    # 2️⃣ Resolve name column — CSV may use 'name' or 'student_name'
    name_col = None
    for candidate in ("name", "student_name"):
        if candidate in df.columns:
            name_col = candidate
            break

    count = 0
    skipped = 0

    for _, row in df.iterrows():
        # Resolve student name from whichever column exists
        raw_name = row.get(name_col) if name_col else None
        if not pd.notna(raw_name) or str(raw_name).strip() == "":
            skipped += 1
            continue
        student_name = str(raw_name).strip()

        # get or create student
        cursor.execute("SELECT id FROM students WHERE name = ?", (student_name,))
        existing_student = cursor.fetchone()
        if existing_student:
            student_id = existing_student["id"]
        else:
            import uuid
            roll_number = f"AUTO-{uuid.uuid4().hex[:6].upper()}"
            email = f"{student_name.lower().replace(' ', '.')}@gmail.com"
            cursor.execute("SELECT id FROM students WHERE email = ?", (email,))
            if cursor.fetchone():
                email = f"{student_name.lower().replace(' ', '.')}.{uuid.uuid4().hex[:4]}@gmail.com"
            cursor.execute(
                "INSERT INTO students (name, roll_number, department, semester, email, password) VALUES (?, ?, ?, ?, ?, ?)",
                (student_name, roll_number, "General", 1, email, "hashed_password_123"),
            )
            conn.commit()
            student_id = cursor.lastrowid

        subj = str(row["subject"]).strip()
        try:
            mk = int(row["marks"])
        except (ValueError, TypeError):
            skipped += 1
            continue

        mx = int(row.get("max_marks", 100)) if pd.notna(row.get("max_marks")) else 100
        sh = int(row.get("study_hours", 0)) if pd.notna(row.get("study_hours")) else 0

        # Safely extract attendance — default to 0 if column is absent or value is null
        att = 0
        if "attendance" in df.columns and pd.notna(row.get("attendance")):
            try:
                att = int(row["attendance"])
            except (ValueError, TypeError):
                att = 0

        # Update student-level attendance
        if att:
            try:
                cursor.execute(
                    "UPDATE students SET attendance = ? WHERE id = ?",
                    (att, student_id),
                )
            except Exception:
                pass

        # Insert into marks WITH attendance
        cursor.execute(
            "INSERT INTO marks (student_id, student_name, subject, marks, max_marks, study_hours, attendance) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (student_id, student_name, subj, mk, mx, sh, att),
        )
        count += 1

    conn.commit()

    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM marks")
    total_marks = cursor.fetchone()["total"]
    conn.close()

    return {
        "processed": count,
        "skipped": skipped,
        "total_students": total_students,
        "total_marks": total_marks,
    }


def get_or_create_student(name: str, cursor, conn) -> int:
    """Return the id of an existing student or create a new one."""
    cursor.execute("SELECT id FROM students WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row["id"]

    import uuid
    roll_number = f"AUTO-{uuid.uuid4().hex[:6].upper()}"
    email = f"{name.lower().replace(' ', '.')}@gmail.com"

    # Make email unique if already taken
    cursor.execute("SELECT id FROM students WHERE email = ?", (email,))
    if cursor.fetchone():
        email = f"{name.lower().replace(' ', '.')}.{uuid.uuid4().hex[:4]}@gmail.com"

    cursor.execute(
        "INSERT INTO students (name, roll_number, department, semester, email, password) VALUES (?, ?, ?, ?, ?, ?)",
        (name, roll_number, "General", 1, email, "hashed_password_123"),
    )
    conn.commit()
    return cursor.lastrowid


def process_csv(csv_path: str):
    """Main processing function."""
    if not os.path.isfile(csv_path):
        print(f"[ERROR] File not found: {csv_path}")
        return

    print(f"\n[INFO]  Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)

    # Normalise column names
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
    print(f"[INFO]  Columns found : {list(df.columns)}")
    print(f"[INFO]  Total rows    : {len(df)}")

    # Validate required columns
    if "subject" not in df.columns or "marks" not in df.columns:
        print('[ERROR] CSV must have "subject" and "marks" columns.')
        return

    # Resolve name column — CSV may use 'name' or 'student_name'
    name_col = None
    for candidate in ("name", "student_name"):
        if candidate in df.columns:
            name_col = candidate
            break
    if not name_col:
        print('[ERROR] CSV must have a "name" or "student_name" column.')
        return
    print(f"[INFO]  Using name column: '{name_col}'")

    conn = get_db()
    cursor = conn.cursor()
    count = 0
    skipped = 0

    for i, row in df.iterrows():
        # ── Resolve student ──────────────────────────────────────────────
        raw_name = row.get(name_col)
        if not pd.notna(raw_name) or str(raw_name).strip() == "":
            skipped += 1
            continue
        student_name = str(raw_name).strip()
        student_id = get_or_create_student(student_name, cursor, conn)

        # ── Extract fields ───────────────────────────────────────────────
        subj = str(row["subject"]).strip()
        try:
            mk = int(row["marks"])
        except (ValueError, TypeError):
            skipped += 1
            continue

        mx = int(row.get("max_marks", 100)) if pd.notna(row.get("max_marks")) else 100
        sh = int(row.get("study_hours", 0)) if pd.notna(row.get("study_hours")) else 0

        # Safely extract attendance — default to 0 if column missing or null
        att = 0
        if "attendance" in df.columns and pd.notna(row.get("attendance")):
            try:
                att = int(row["attendance"])
            except (ValueError, TypeError):
                att = 0

        # Update student-level attendance
        if att:
            try:
                cursor.execute(
                    "UPDATE students SET attendance = ? WHERE id = ?",
                    (att, student_id),
                )
            except Exception:
                pass

        # ── Insert or update marks (WITH attendance) ─────────────────────
        cursor.execute(
            "SELECT id FROM marks WHERE student_id = ? AND subject = ?",
            (student_id, subj),
        )
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                "UPDATE marks SET marks=?, max_marks=?, study_hours=?, student_name=?, attendance=? WHERE id=?",
                (mk, mx, sh, student_name, att, existing["id"]),
            )
        else:
            cursor.execute(
                "INSERT INTO marks (student_id, student_name, subject, marks, max_marks, study_hours, attendance) VALUES (?,?,?,?,?,?,?)",
                (student_id, student_name, subj, mk, mx, sh, att),
            )
        count += 1

    conn.commit()

    # ── Summary ──────────────────────────────────────────────────────────────
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM marks")
    total_marks = cursor.fetchone()["total"]
    conn.close()

    print(f"\n{'='*45}")
    print(f"  [OK]     Records processed : {count}")
    print(f"  [SKIP]   Rows skipped      : {skipped}")
    print(f"  [TOTAL]  Total students    : {total_students}")
    print(f"  [TOTAL]  Total marks rows  : {total_marks}")
    print(f"{'='*45}")
    print(f"\n  View results at: http://127.0.0.1:5000/api/all-students\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python auto_process_csv.py <path-to-csv>")
        sys.exit(1)
    process_csv(sys.argv[1])
