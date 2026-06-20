"""
Generate a professional sample CSV dataset for the AI-Based Student Performance
Analysis platform. Creates 100 students × 2-5 subjects with realistic data.
"""

import csv
import random
import os

random.seed(42)

# ── Configuration ────────────────────────────────────────────────────────────
SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "English", "Computer Science",
    "Electronics", "Data Structures", "Database Systems", "Operating Systems",
    "Discrete Mathematics", "Digital Logic", "Software Engineering",
]
SECTIONS = ["A", "B", "C"]
SEMESTERS = [1, 2, 3, 4, 5, 6]
FIRST_NAMES = [
    "Aarav","Aditi","Aditya","Akash","Amara","Amit","Ananya","Aniket","Ankita","Arjun",
    "Bhavya","Chetan","Deepa","Dev","Dhruv","Divya","Ekta","Farhan","Gaurav","Harsh",
    "Isha","Jayesh","Kavya","Kiran","Kriti","Kunal","Lakshmi","Manish","Meera","Mohit",
    "Nandini","Naveen","Neha","Nikhil","Nisha","Omkar","Pallavi","Pankaj","Pooja","Pranav",
    "Priya","Rahul","Rajesh","Rakesh","Ramesh","Ravi","Ritika","Rohit","Sakshi","Sandeep",
    "Sanjay","Sapna","Shreya","Shubham","Simran","Sneha","Sonia","Sunil","Suresh","Tanvi",
    "Tushar","Uma","Varun","Vidya","Vikram","Vinay","Vinita","Vishal","Yash","Zara",
    "Abhishek","Ajay","Alok","Arun","Ashok","Chandra","Darshan","Dinesh","Ganesh","Girish",
    "Hemant","Hitesh","Jagdish","Jatin","Karthik","Madhav","Mayank","Nagesh","Prabhu","Sagar",
    "Sahil","Sameer","Satish","Tarun","Uday","Umesh","Vimal","Yogesh","Anand","Bharath",
]
LAST_NAMES = [
    "Sharma","Patel","Gupta","Singh","Kumar","Verma","Joshi","Mishra","Reddy","Nair",
    "Iyer","Menon","Das","Roy","Bose","Chopra","Malhotra","Kapoor","Sinha","Thakur",
    "Mehta","Shah","Desai","Rao","Patil","Kulkarni","Deshpande","Jain","Agarwal","Saxena",
]

# ── Student profiles ─────────────────────────────────────────────────────────
# Distribution: ~15% weak, ~50% average, ~25% good, ~10% top
PROFILES = {
    "weak":    {"marks_range": (15, 38), "att_range": (30, 60), "study_range": (0, 2), "weight": 15},
    "average": {"marks_range": (40, 65), "att_range": (55, 78), "study_range": (2, 5), "weight": 50},
    "good":    {"marks_range": (65, 82), "att_range": (72, 90), "study_range": (4, 7), "weight": 25},
    "top":     {"marks_range": (82, 98), "att_range": (85, 99), "study_range": (5, 10), "weight": 10},
}

def pick_profile():
    r = random.randint(1, 100)
    cumulative = 0
    for name, cfg in PROFILES.items():
        cumulative += cfg["weight"]
        if r <= cumulative:
            return name, cfg
    return "average", PROFILES["average"]

def compute_grade(pct):
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B+"
    if pct >= 60: return "B"
    if pct >= 50: return "C"
    if pct >= 40: return "D"
    return "F"

def compute_status(pct, att):
    if pct < 35 or att < 40: return "At Risk"
    if pct < 50 or att < 60: return "Needs Improvement"
    if pct < 70: return "Average"
    if pct < 85: return "Good"
    return "Excellent"

def generate_dataset(num_students=100):
    rows = []
    used_names = set()

    for i in range(1, num_students + 1):
        # Unique name
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f"{first} {last}"
            if full_name not in used_names:
                used_names.add(full_name)
                break

        student_id = f"STU{i:04d}"
        usn = f"1XX{random.choice(['CS','EC','ME','CV','IS'])}{random.randint(20,24)}{random.choice(SECTIONS)}{i:03d}"
        semester = random.choice(SEMESTERS)
        section = random.choice(SECTIONS)
        profile_name, profile = pick_profile()

        # Pick 2-5 subjects
        num_subj = random.randint(2, 5)
        student_subjects = random.sample(SUBJECTS, num_subj)

        for subj in student_subjects:
            max_marks = 100
            # Add variance per subject
            lo, hi = profile["marks_range"]
            marks = random.randint(lo, hi)
            # Subject-specific nudge (some students good at one, bad at another)
            marks = max(0, min(max_marks, marks + random.randint(-8, 8)))

            att_lo, att_hi = profile["att_range"]
            attendance = round(random.uniform(att_lo, att_hi), 1)
            # Cap attendance
            attendance = max(0, min(100, attendance))

            sh_lo, sh_hi = profile["study_range"]
            study_hours = round(random.uniform(sh_lo, sh_hi), 1)

            # Assignment score (out of 30)
            assignment_score = max(0, min(30, random.randint(
                int(lo * 0.3), int(hi * 0.3) + 2
            )))

            # Internal marks (out of 40)
            internal_marks = max(0, min(40, random.randint(
                int(lo * 0.4), int(hi * 0.4) + 3
            )))

            pct = (marks / max_marks) * 100
            grade = compute_grade(pct)
            status = compute_status(pct, attendance)

            rows.append({
                "student_id": student_id,
                "student_name": full_name,
                "usn": usn,
                "subject": subj,
                "marks_obtained": marks,
                "max_marks": max_marks,
                "attendance_percentage": attendance,
                "study_hours": study_hours,
                "assignment_score": assignment_score,
                "internal_marks": internal_marks,
                "semester": semester,
                "section": section,
                "grade": grade,
                "performance_status": status,
            })

    return rows


if __name__ == "__main__":
    rows = generate_dataset(100)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_100_students.csv")
    
    fieldnames = [
        "student_id", "student_name", "usn", "subject",
        "marks_obtained", "max_marks", "attendance_percentage",
        "study_hours", "assignment_score", "internal_marks",
        "semester", "section", "grade", "performance_status",
    ]
    
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Stats
    import collections
    statuses = collections.Counter(r["performance_status"] for r in rows)
    students = len(set(r["student_id"] for r in rows))
    subjects = len(set(r["subject"] for r in rows))
    
    print(f"[OK] Generated {out_path}")
    print(f"   {len(rows)} records | {students} students | {subjects} subjects")
    print(f"   Status distribution: {dict(statuses)}")
