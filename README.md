# 📊 AI-Based Student Performance Analysis System (SPAS)

A scalable, real-time analytics platform dedicated to evaluating and predicting student performance through AI. Built specifically for a **Student-Centered Experience**, it allows students to dynamically upload CSV performance datasets and instantly receive comprehensive visual analytics, AI-powered predictions, and personalized recommendations.

---

## ✨ Features

- **🎓 Student-Centric Dashboard:** Secure, session-based authentication for individual students.
- **📂 Dynamic CSV Upload:** Upload any CSV file with 100-500+ records and instantly parse it in real-time.
- **🧠 AI Prediction Engine:** Uses a Random Forest Regressor to project final semester scores based on attendance, study hours, and historical marks.
- **📈 Real-Time Visual Analytics:** Dynamic charts powered by Chart.js (Radar, Bar, Doughnut, Scatter) for Subject-wise Performance, Attendance vs. Marks correlation, and Risk Assessments.
- **⚡ Smart Data Processing:** Automatically handles missing data, detects variations in column headers, and safeguards against duplicate records.
- **💡 Actionable Insights:** Auto-generates personalized study recommendations based on computed risk-levels.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3 (Glassmorphism UI), JavaScript (Vanilla)
- **Backend:** Python, Flask, SQLite
- **Data Science:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn, Joblib
- **Visualization:** Chart.js

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Git

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd AI-Based-Student-Performance-Analytics--main
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python run.py
```
The server will start at `http://127.0.0.1:5000/`.

---

## 🐙 GitHub Commands for Pushing Changes

Below is a detailed, step-by-step guide on how to save and push your local changes to the GitHub repository.

### 1. Initialize Git (If starting a new repository)
If you haven't already initialized Git in your project folder, run this once:
```bash
git init
```

### 2. Check the Status of Your Files
Before adding files, it's good practice to see which files have been modified, added, or deleted.
```bash
git status
```
*(Red files are untracked/modified, green files are staged for commit).*

### 3. Add Changes to the Staging Area
You must "stage" your files before committing them. This tells Git which changes you want to include in the next commit.
```bash
# To add a specific file:
git add filename.ext

# To add ALL modified and new files in the current directory:
git add .
```

### 4. Commit Your Changes
A commit acts as a snapshot of your project at this point in time. Always use a clear, descriptive message so you (and others) know what was changed.
```bash
git commit -m "Add descriptive commit message here (e.g., Fixed login bug)"
```

### 5. Link to Your Remote Repository (If not already linked)
If you just created a new repository on GitHub and need to connect your local folder to it:
```bash
git remote add origin <your-github-repo-url>
```

### 6. Rename the Default Branch (Optional, but recommended)
GitHub uses `main` as the default branch name. If your local branch is still named `master`, rename it:
```bash
git branch -M main
```

### 7. Push Your Changes to GitHub
Finally, upload your committed changes to the remote GitHub repository.
```bash
# If pushing for the very first time, set the upstream branch:
git push -u origin main

# For all subsequent pushes on this branch, you can simply use:
git push
```

---

## 📝 How to Use (CSV Upload Instructions)

1. **Register/Login:** Create a student account from the homepage.
2. **Navigate to Dashboard:** Upon login, navigate to the Dashboard.
3. **Upload Dataset:** Drag and drop your `.csv` file into the upload zone.
   - *Tip:* Use `sample_100_students.csv` included in the repository to test the platform.
4. **View Analytics:** The dashboard will instantly populate with summary stats, subject-wise comparisons, risk assessments, and AI recommendations.

### Supported CSV Format
The smart CSV parser supports flexible headers. However, for optimal processing, include the following data:
- `Student Name` / `Name`
- `USN` / `Roll Number`
- `Subject`
- `Marks Obtained`
- `Maximum Marks`
- `Attendance %`
- `Study Hours`

---

## 📁 Folder Structure

```
├── backend/
│   ├── ai_model.py            # Random Forest training and inference
│   ├── analytics_engine.py    # Generates dashboard metrics and insights
│   ├── csv_upload_route.py    # Handles file ingestion
│   ├── database.py            # SQLite schema and operations
│   ├── routes.py              # Auth and API endpoints
│   ├── smart_csv_parser.py    # Flexible CSV mapping and cleaning
│   └── student_model.pkl      # Pre-trained ML weights
├── frontend/
│   ├── static/
│   │   ├── css/style.css      # Core styles and animations
│   │   └── js/
│   │       ├── script.js            # General UI logic
│   │       └── student_analytics.js # Real-time CSV dashboard logic
│   └── templates/             # Jinja2 HTML Templates
├── generate_sample_csv.py     # Script to generate realistic mock data
├── run.py                     # Entry point for Flask
├── sample_100_students.csv    # Example dataset for testing
└── requirements.txt           # Project dependencies
```

---

## 🧠 AI Model Explanation

The system incorporates a **Random Forest Regressor** trained on historical student performance metrics.
- **Inputs:** `Attendance (%)`, `Previous Semester Marks`, `Internal Marks`, `Study Hours`.
- **Output:** Predicted `Final Marks`.
- **Why Random Forest?** It efficiently handles non-linear relationships and is highly robust against overfitting, making it ideal for the multifaceted nature of educational data.

---

## 🔮 Future Improvements

- **Cloud Database Integration:** Migrate from SQLite to PostgreSQL/MongoDB for enterprise scaling.
- **Export to PDF:** Allow students to download full analytics reports in PDF format.
- **Teacher Portals (Plugin):** Re-introduce a distinct microservice for institutional bulk-management.
- **Advanced Deep Learning:** Transition to Neural Networks for longitudinal student performance tracking.

---

## 📸 Screenshots

*(Add your screenshots here)*
- Dashboard Overview
- Real-time Analytics Charts
- AI Prediction Panel

---

*Engineered for Student Success.*