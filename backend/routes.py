"""
Backend — Routes Module
========================
Contains all Flask routes organised into three Blueprints:

1. page_routes       — serves HTML pages (templates)
2. api_routes        — REST API endpoints returning JSON
"""

import hashlib
import sqlite3
import uuid

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from backend.database import get_db, seed_sample_data, get_or_create_student, cleanup_session_uploads
from backend.ai_model import predict_student_performance


# ─────────────────────────────────────────────────────────────────────────────
# Helper — password hashing
# ─────────────────────────────────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    """Return a SHA-256 hex digest of *plain*."""
    return hashlib.sha256(plain.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Blueprint 1 — HTML page routes
# ─────────────────────────────────────────────────────────────────────────────
page_routes = Blueprint('pages', __name__)


@page_routes.route('/')
def home():
    """Home page with project introduction."""
    return render_template('index.html')


@page_routes.route('/login', methods=['GET'])
def login_page():
    """Render the login page."""
    return render_template('login.html')


@page_routes.route('/register', methods=['GET'])
def register_page():
    """Render the registration page."""
    return render_template('register.html')


@page_routes.route('/dashboard')
def dashboard_page():
    """Render the dashboard (must be logged in)."""
    if 'student_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('pages.login_page'))
    return render_template('dashboard.html')


@page_routes.route('/analysis')
def analysis_page():
    """Render the analysis page (must be logged in)."""
    if 'student_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('pages.login_page'))
    return render_template('analysis.html')


@page_routes.route('/recommendation')
def recommendation_page():
    """Render the recommendation page (must be logged in)."""
    if 'student_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('pages.login_page'))
    return render_template('recommendation.html')


@page_routes.route('/students')
def students_page():
    """Render a page that shows all students with their marks in a searchable table."""
    return render_template('students.html')


@page_routes.route('/objectives')
def objectives_page():
    """Render the project objectives page."""
    return render_template('objectives.html')



@page_routes.route('/logout')
def logout():
    """Clear session, cleanup uploads, and logout."""
    sess_id = session.get('upload_session_id')
    if sess_id:
        try:
            cleanup_session_uploads(sess_id)
        except Exception:
            pass
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('pages.home'))


# ─────────────────────────────────────────────────────────────────────────────
# Blueprint 2 — REST API routes
# ─────────────────────────────────────────────────────────────────────────────
api_routes = Blueprint('api', __name__, url_prefix='/api')


@api_routes.route('/register', methods=['POST'])
def register():
    """
    Register a new student.
    Expects form data: name, roll_number, department, semester, email, password
    """
    name        = request.form.get('name',        '').strip()
    roll_number = request.form.get('roll_number', '').strip()
    department  = request.form.get('department',  '').strip()
    semester    = request.form.get('semester',    '')
    email       = request.form.get('email',       '').strip()
    password    = request.form.get('password',    '').strip()

    # ── Basic validation ──
    if not all([name, roll_number, department, semester, email, password]):
        flash('All fields are required!', 'error')
        return redirect(url_for('pages.register_page'))

    if not email.lower().endswith('@gmail.com'):
        flash('Only @gmail.com addresses are allowed!', 'error')
        return redirect(url_for('pages.register_page'))

    if len(password) < 8:
        flash('Password must be at least 8 characters long!', 'error')
        return redirect(url_for('pages.register_page'))

    hashed_pw = _hash_password(password)

    conn   = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''INSERT INTO students (name, roll_number, department, semester, email, password)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (name, roll_number, department, int(semester), email, hashed_pw)
        )
        conn.commit()
        student_id = cursor.lastrowid

        # ── Seed sample marks for new student ──
        seed_sample_data(student_id)

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('pages.login_page'))

    except sqlite3.IntegrityError:
        flash('Roll number or email already exists!', 'error')
        return redirect(url_for('pages.register_page'))

    finally:
        conn.close()


@api_routes.route('/login', methods=['POST'])
def login():
    """
    Authenticate a student.
    Expects form data: email, password
    """
    email    = request.form.get('email',    '').strip()
    password = request.form.get('password', '').strip()

    if not email or not password:
        flash('Email and password are required!', 'error')
        return redirect(url_for('pages.login_page'))

    hashed_pw = _hash_password(password)

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM students WHERE email = ? AND password = ?',
        (email, hashed_pw)
    )
    student = cursor.fetchone()
    conn.close()

    if student:
        session['student_id']    = student['id']
        session['student_name']  = student['name']
        session['student_email'] = student['email']
        session['upload_session_id'] = uuid.uuid4().hex
        flash(f'Welcome back, {student["name"]}!', 'success')
        return redirect(url_for('pages.dashboard_page'))
    else:
        flash('Invalid email or password!', 'error')
        return redirect(url_for('pages.login_page'))


@api_routes.route('/student', methods=['GET'])
def get_student():
    """Get the logged-in student's profile data."""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, name, roll_number, department, semester, email, attendance FROM students WHERE id = ?',
        (session['student_id'],)
    )
    student = cursor.fetchone()
    conn.close()

    if student:
        return jsonify(dict(student))
    return jsonify({'error': 'Student not found'}), 404


@api_routes.route('/student/attendance', methods=['POST'])
def update_attendance():
    """Update the logged-in student's attendance percentage."""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    attendance = data.get('attendance')

    if attendance is None:
        return jsonify({'error': 'Attendance value is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE students SET attendance = ? WHERE id = ?',
        (int(attendance), session['student_id'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Attendance updated successfully'})


@api_routes.route('/marks', methods=['GET'])
def get_marks():
    """Get all marks for the logged-in student."""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT subject, marks, max_marks, study_hours, attendance FROM marks WHERE student_id = ?',
        (session['student_id'],)
    )
    marks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(marks)


@api_routes.route('/marks', methods=['POST'])
def submit_marks():
    """
    Add or update marks for the logged-in student.
    Expects JSON: { "subject": "...", "marks": 85, "max_marks": 100 }
    """
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data        = request.get_json()
    subject     = data.get('subject', '').strip()
    marks       = data.get('marks')
    max_marks   = data.get('max_marks', 100)
    study_hours = data.get('study_hours', 0)
    attendance  = data.get('attendance', 0)

    if not subject or marks is None:
        return jsonify({'error': 'Subject and marks are required'}), 400

    conn   = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id FROM marks WHERE student_id = ? AND subject = ?',
        (session['student_id'], subject)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            'UPDATE marks SET marks = ?, max_marks = ?, study_hours = ?, attendance = ? WHERE id = ?',
            (int(marks), int(max_marks), int(study_hours), int(attendance), existing['id'])
        )
    else:
        cursor.execute(
            'INSERT INTO marks (student_id, subject, marks, max_marks, study_hours, attendance) VALUES (?, ?, ?, ?, ?, ?)',
            (session['student_id'], subject, int(marks), int(max_marks), int(study_hours), int(attendance))
        )

    conn.commit()
    conn.close()
    return jsonify({'message': 'Marks saved successfully'})


@api_routes.route('/marks/<string:subject>', methods=['DELETE'])
def delete_marks(subject):
    """Delete a specific subject and its marks for the logged-in student."""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    subject = subject.strip()
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM marks WHERE student_id = ? AND subject = ?',
        (session['student_id'], subject)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Subject deleted successfully'})


@api_routes.route('/marks/batch', methods=['POST'])
def batch_upload_marks():
    """
    Batch upload marks from a CSV file.
    Expects a file in request.files['file']
    CSV columns: subject, marks, max_marks, study_hours, attendance
    """
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        import pandas as pd
        import io
        import numpy as np
        
        # Read CSV file
        content = file.stream.read().decode("UTF-8", errors="ignore")
        df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
        
        # Standardize column names
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]

        # Ensure required columns are present
        if 'subject' not in df.columns or 'marks' not in df.columns:
            return jsonify({'error': 'CSV must contain "subject" and "marks" columns'}), 400

        # Resolve name column — CSV may use 'name' or 'student_name'
        name_col = None
        for candidate in ('name', 'student_name'):
            if candidate in df.columns:
                name_col = candidate
                break
        
        conn = get_db()
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            # Get student name from whichever column exists
            student_name_val = row.get(name_col) if name_col else None
            student_name = None
            if pd.notna(student_name_val):
                student_name = str(student_name_val).strip()
                if not student_name:
                    student_name = None

            # Determine student_id
            curr_student_id = None
            if student_name:
                curr_student_id = get_or_create_student(student_name, conn=conn)
            else:
                curr_student_id = session.get('student_id')
            
            if not curr_student_id:
                continue 

            # Safely extract attendance — default to 0 if column missing or null
            att = 0
            if 'attendance' in df.columns and pd.notna(row.get('attendance')):
                try:
                    att = int(row['attendance'])
                except (ValueError, TypeError):
                    att = 0

            # Update student-level attendance
            if att:
                try:
                    cursor.execute('UPDATE students SET attendance = ? WHERE id = ?', (att, curr_student_id))
                except Exception:
                    pass
            
            # Extract values with defaults and NaN handling
            try:
                subj = str(row['subject']).strip()
                mk = int(row['marks'])
                mx = int(row.get('max_marks', 100)) if pd.notna(row.get('max_marks')) else 100
                sh = int(row.get('study_hours', 0)) if pd.notna(row.get('study_hours')) else 0
                
                if not subj: continue

                # Check if entry exists
                cursor.execute('SELECT id FROM marks WHERE student_id = ? AND subject = ?', (curr_student_id, subj))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute(
                        'UPDATE marks SET marks = ?, max_marks = ?, study_hours = ?, student_name = ?, attendance = ? WHERE id = ?',
                        (mk, mx, sh, student_name, att, existing['id'])
                    )
                else:
                    cursor.execute(
                        'INSERT INTO marks (student_id, student_name, subject, marks, max_marks, study_hours, attendance) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (curr_student_id, student_name, subj, mk, mx, sh, att)
                    )
                count += 1
            except (ValueError, TypeError):
                continue # Skip rows with invalid numbers
        
        conn.commit()
        conn.close()
        return jsonify({'message': f'Successfully processed {count} records'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_routes.route('/all-students', methods=['GET'])
def get_all_students():
    """
    Get all students and their marks.
    Open in browser: http://127.0.0.1:5000/api/all-students
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, roll_number, department, semester, email, attendance FROM students ORDER BY name')
    students = [dict(row) for row in cursor.fetchall()]

    for student in students:
        cursor.execute(
            'SELECT subject, marks, max_marks, study_hours, attendance FROM marks WHERE student_id = ?',
            (student['id'],)
        )
        student['marks'] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return jsonify(students)


@api_routes.route('/search', methods=['GET'])
def search_student():
    """
    Search for a student by name or roll number.
    Query param: ?q=search_term
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, name, roll_number, department, semester, email
           FROM students
           WHERE name LIKE ? OR roll_number LIKE ?''',
        (f'%{query}%', f'%{query}%')
    )
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)


@api_routes.route('/predict', methods=['GET'])
def get_prediction():
    """
    Calculates AI prediction for the logged-in student based on their marks.
    """
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute('SELECT attendance FROM students WHERE id = ?', (session['student_id'],))
    student = cursor.fetchone()
    
    # Get marks info (average across subjects)
    cursor.execute('SELECT AVG(marks) as avg_marks, AVG(study_hours) as avg_study FROM marks WHERE student_id = ?', (session['student_id'],))
    marks_data = cursor.fetchone()
    
    conn.close()

    if not marks_data or marks_data['avg_marks'] is None:
        return jsonify({'prediction': None, 'message': 'Add some marks first to get a prediction.'})

    # Prepare input for AI model
    # Features: attendance, prev_sem_marks (using current avg as proxy), internal_marks (proxy), study_hours
    input_data = {
        "attendance": student['attendance'] or 85,
        "prev_sem_marks": marks_data['avg_marks'],
        "internal_marks": marks_data['avg_marks'] * 0.3, # Heuristic
        "study_hours": marks_data['avg_study'] or 4
    }

    try:
        prediction = predict_student_performance(input_data)
        return jsonify({
            'prediction': round(float(prediction), 2),
            'input_used': input_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

