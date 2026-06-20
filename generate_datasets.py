"""
Generate 3 Standard CSV Datasets for the Student Performance Analysis System.
Run: python generate_datasets.py
"""

import csv
import os
import random
import math

DATASETS_DIR = "datasets"
os.makedirs(DATASETS_DIR, exist_ok=True)

SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Computer Science", "English", "Statistics"]

def compute_grade(marks, max_marks):
    pct = (marks / max_marks) * 100 if max_marks > 0 else 0
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B+"
    if pct >= 60: return "B"
    if pct >= 50: return "C"
    if pct >= 40: return "D"
    return "F"

FIELDNAMES = ["student_id","student_name","subject","marks","max_marks","attendance","study_hours","grade"]


# ─────────────────────────────────────────────────────────────────────────────
# CSV 1 – Single Student (5 subjects)
# ─────────────────────────────────────────────────────────────────────────────
def gen_single_student():
    rows = []
    subjects_data = [
        ("Mathematics",     82, 100, 88, 5),
        ("Physics",         75, 100, 80, 4),
        ("Chemistry",       91, 100, 95, 6),
        ("Computer Science",88, 100, 92, 5),
        ("English",         70, 100, 75, 3),
    ]
    for subject, marks, max_marks, attendance, study_hours in subjects_data:
        rows.append({
            "student_id": "S001",
            "student_name": "Arjun Sharma",
            "subject": subject,
            "marks": marks,
            "max_marks": max_marks,
            "attendance": attendance,
            "study_hours": study_hours,
            "grade": compute_grade(marks, max_marks),
        })
    return rows

# ─────────────────────────────────────────────────────────────────────────────
# CSV 2 – 50 Students (5 subjects each = 250 rows)
# ─────────────────────────────────────────────────────────────────────────────
NAMES_50 = [
    "Aarav Patel","Bhavna Reddy","Chirag Mehta","Divya Iyer","Eshan Kapoor",
    "Farida Khan","Gaurav Nair","Hina Joshi","Ishaan Verma","Jaya Singh",
    "Karthik Rao","Lakshmi Pillai","Manish Kumar","Nandita Bose","Omkar Desai",
    "Priya Gupta","Qasim Ali","Riya Sharma","Suresh Menon","Tara Choudhary",
    "Uday Tiwari","Vani Agarwal","Waqar Ansari","Xena D'Souza","Yash Malhotra",
    "Zara Hussain","Abhinav Roy","Brinda Das","Chetan Patil","Disha Saxena",
    "Ekta Mishra","Farhan Sheikh","Gayatri Nath","Hemant Jain","Indira Chatterjee",
    "Jayant Soni","Kavita Pandey","Laxman Bhatt","Meera Trivedi","Nikhil Thakur",
    "Ojasvi Banerjee","Pallavi Kulkarni","Rahul Shetty","Shreya Ghosh","Tanmay More",
    "Uma Krishnamurthy","Vikram Dixit","Wahida Begum","Aishwarya Naik","Zubair Mirza",
]

def student_profile(idx):
    """Return (marks_mean, marks_std, attendance_mean, study_hrs_mean) for variety."""
    r = random.random()
    if idx < 10:        # Top students
        return (85, 8, 90, 6)
    elif idx < 30:      # Average students
        return (65, 12, 75, 4)
    else:               # Weak students
        return (45, 15, 60, 2)

def gen_fifty_students():
    rows = []
    random.seed(42)
    subjects = ["Mathematics", "Physics", "Chemistry", "Computer Science", "English"]
    for i, name in enumerate(NAMES_50):
        sid = f"S{str(i+1).zfill(3)}"
        mean_m, std_m, mean_a, mean_h = student_profile(i)
        for subject in subjects:
            marks = min(100, max(0, int(random.gauss(mean_m, std_m))))
            att   = min(100, max(30, int(random.gauss(mean_a, 8))))
            hrs   = max(1, int(random.gauss(mean_h, 1)))
            rows.append({
                "student_id": sid,
                "student_name": name,
                "subject": subject,
                "marks": marks,
                "max_marks": 100,
                "attendance": att,
                "study_hours": hrs,
                "grade": compute_grade(marks, 100),
            })
    return rows

# ─────────────────────────────────────────────────────────────────────────────
# CSV 3 – 300 Students (6 subjects each = 1800 rows)
# ─────────────────────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Aarav","Bhavna","Chirag","Divya","Eshan","Farida","Gaurav","Hina","Ishaan","Jaya",
    "Karthik","Lakshmi","Manish","Nandita","Omkar","Priya","Qasim","Riya","Suresh","Tara",
    "Uday","Vani","Waqar","Xena","Yash","Zara","Abhinav","Brinda","Chetan","Disha",
    "Ekta","Farhan","Gayatri","Hemant","Indira","Jayant","Kavita","Laxman","Meera","Nikhil",
    "Ojasvi","Pallavi","Rahul","Shreya","Tanmay","Uma","Vikram","Wahida","Aishwarya","Zubair",
]
LAST_NAMES = [
    "Patel","Reddy","Mehta","Iyer","Kapoor","Khan","Nair","Joshi","Verma","Singh",
    "Rao","Pillai","Kumar","Bose","Desai","Gupta","Ali","Sharma","Menon","Choudhary",
    "Tiwari","Agarwal","Ansari","D'Souza","Malhotra","Hussain","Roy","Das","Patil","Saxena",
]
ALL_SUBJECTS = ["Mathematics","Physics","Chemistry","Computer Science","English","Statistics"]

def gen_three_hundred_students():
    rows = []
    random.seed(99)
    used = set()
    for i in range(300):
        # Unique name
        while True:
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            name = f"{fn} {ln}"
            if name not in used:
                used.add(name)
                break
        sid = f"STU{str(i+1).zfill(4)}"

        # Tiered performance
        tier = random.choices(["top","avg","weak"], weights=[20,55,25])[0]
        if tier == "top":
            mean_m, std_m, mean_a, mean_h = 85, 7, 90, 6
        elif tier == "avg":
            mean_m, std_m, mean_a, mean_h = 64, 12, 74, 4
        else:
            mean_m, std_m, mean_a, mean_h = 40, 14, 58, 2

        # Randomly select 6 subjects (= full set)
        for subject in ALL_SUBJECTS:
            marks = min(100, max(0, int(random.gauss(mean_m, std_m))))
            att   = min(100, max(20, int(random.gauss(mean_a, 10))))
            hrs   = max(0, int(random.gauss(mean_h, 1.5)))
            rows.append({
                "student_id": sid,
                "student_name": name,
                "subject": subject,
                "marks": marks,
                "max_marks": 100,
                "attendance": att,
                "study_hours": hrs,
                "grade": compute_grade(marks, 100),
            })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Write CSVs
# ─────────────────────────────────────────────────────────────────────────────
def write_csv(filename, rows):
    path = os.path.join(DATASETS_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] {path}  ({len(rows)} rows)")


if __name__ == "__main__":
    write_csv("single_student.csv",          gen_single_student())
    write_csv("fifty_students.csv",          gen_fifty_students())
    write_csv("three_hundred_students.csv",  gen_three_hundred_students())
    print("\nAll 3 datasets generated successfully in datasets/")
