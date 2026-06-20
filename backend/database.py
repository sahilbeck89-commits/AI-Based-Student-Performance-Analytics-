"""
Backend — Database Module
==========================
Handles all SQLite database operations:
- Creating tables (students, marks, teachers, uploads, dataset_records)
- Helper functions for DB connections
- Seeding sample data for new students
"""

import sqlite3
import os

# Database file lives inside the backend folder
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def get_db():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """
    Initialize the database with required tables.
    Called once when the app starts for the first time.
    """
    conn = get_db()
    cursor = conn.cursor()

    # ── Students Table (existing — kept for student login flow) ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            attendance INTEGER DEFAULT 0
        )
    ''')

    # ── Marks Table (existing — kept for student login flow) ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            student_name TEXT,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL,
            max_marks INTEGER DEFAULT 100,
            study_hours INTEGER DEFAULT 0,
            attendance INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    # ── Uploads Table (tracks each CSV upload per student session) ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            row_count INTEGER DEFAULT 0,
            column_mapping TEXT,
            warnings TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')

    # ── Dataset Records Table (NEW — normalized CSV data per upload) ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataset_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER NOT NULL,
            student_name TEXT,
            usn TEXT,
            subject TEXT,
            marks REAL,
            max_marks REAL DEFAULT 100,
            attendance REAL,
            study_hours REAL DEFAULT 0,
            grade TEXT,
            FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()

    # ── Migrations for existing databases ──
    _run_migrations(cursor, conn)

    conn.close()


def _run_migrations(cursor, conn):
    """Add columns/tables that may be missing in older databases."""
    # Ensure attendance column in marks
    try:
        cursor.execute("SELECT attendance FROM marks LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE marks ADD COLUMN attendance INTEGER DEFAULT 0")
        conn.commit()


def get_or_create_student(name, roll_number=None, email=None, conn=None):
    """Find a student by name/email or create a new one."""
    close_conn = False
    if conn is None:
        conn = get_db()
        close_conn = True

    cursor = conn.cursor()

    # Try finding by name first
    cursor.execute('SELECT id FROM students WHERE name = ?', (name,))
    row = cursor.fetchone()
    if row:
        if close_conn: conn.close()
        return row['id']

    # Generate defaults if not provided
    if not roll_number:
        import uuid
        roll_number = f"AUTO-{uuid.uuid4().hex[:6].upper()}"
    if not email:
        email = f"{name.lower().replace(' ', '.')}@gmail.com"
        cursor.execute('SELECT id FROM students WHERE email = ?', (email,))
        if cursor.fetchone():
            import uuid
            email = f"{name.lower().replace(' ', '.')}.{uuid.uuid4().hex[:4]}@gmail.com"

    cursor.execute(
        'INSERT INTO students (name, roll_number, department, semester, email, password) VALUES (?, ?, ?, ?, ?, ?)',
        (name, roll_number, 'General', 1, email, 'hashed_password_123')
    )
    student_id = cursor.lastrowid
    conn.commit()
    if close_conn: conn.close()
    return student_id


def seed_sample_data(student_id):
    """
    Add sample marks data for a newly registered student.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Sample subjects with marks and study hours
    subjects_marks = [
        ('Mathematics', 85, 100, 5),
        ('Physics', 72, 100, 4),
        ('Chemistry', 68, 100, 3),
        ('English', 90, 100, 2),
        ('Computer Science', 95, 100, 6),
        ('Electronics', 60, 100, 2),
    ]

    for subject, marks, max_marks, study_hours in subjects_marks:
        cursor.execute(
            'INSERT INTO marks (student_id, subject, marks, max_marks, study_hours) VALUES (?, ?, ?, ?, ?)',
            (student_id, subject, marks, max_marks, study_hours)
        )

    conn.commit()
    conn.close()


# ── Upload / Dataset helpers ──────────────────────────────────────────────

def create_upload(session_id, filename):
    """Create an upload record and return its ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO uploads (session_id, filename) VALUES (?, ?)',
        (session_id, filename)
    )
    upload_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return upload_id


def update_upload_meta(upload_id, row_count, column_mapping, warnings):
    """Update an upload record with parse results."""
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE uploads SET row_count=?, column_mapping=?, warnings=? WHERE id=?',
        (row_count, json.dumps(column_mapping), json.dumps(warnings), upload_id)
    )
    conn.commit()
    conn.close()


def insert_dataset_records(upload_id, records):
    """Batch insert parsed CSV records for an upload."""
    conn = get_db()
    cursor = conn.cursor()
    for r in records:
        cursor.execute(
            '''INSERT INTO dataset_records
               (upload_id, student_name, usn, subject, marks, max_marks, attendance, study_hours, grade)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (upload_id, r.get('student_name'), r.get('usn'), r.get('subject'),
             r.get('marks'), r.get('max_marks', 100), r.get('attendance'),
             r.get('study_hours', 0), r.get('grade'))
        )
    conn.commit()
    conn.close()


def get_uploads_for_session(session_id):
    """Get all uploads for a session."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM uploads WHERE session_id = ? AND status = ? ORDER BY upload_time DESC',
        (session_id, 'active')
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_dataset_records(upload_id):
    """Get all records for a dataset upload."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dataset_records WHERE upload_id = ?', (upload_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def delete_upload(upload_id):
    """Delete an upload and all its records."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM dataset_records WHERE upload_id = ?', (upload_id,))
    cursor.execute('DELETE FROM uploads WHERE id = ?', (upload_id,))
    conn.commit()
    conn.close()


def cleanup_session_uploads(session_id):
    """Remove all uploads for a session (called on logout)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM uploads WHERE session_id = ?', (session_id,))
    upload_ids = [r['id'] for r in cursor.fetchall()]
    for uid in upload_ids:
        cursor.execute('DELETE FROM dataset_records WHERE upload_id = ?', (uid,))
    cursor.execute('DELETE FROM uploads WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()
