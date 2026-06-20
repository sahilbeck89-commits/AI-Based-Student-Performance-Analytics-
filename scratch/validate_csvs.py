import pandas as pd

files = [
    'datasets/single_student.csv',
    'datasets/fifty_students.csv',
    'datasets/three_hundred_students.csv',
]
for f in files:
    df = pd.read_csv(f)
    violations = int((df['marks'] > df['max_marks']).sum())
    students = df['student_id'].nunique()
    att_min = int(df['attendance'].min())
    att_max = int(df['attendance'].max())
    print(f"{f}: {len(df)} rows | {students} students | violations={violations} | attendance={att_min}-{att_max}")
