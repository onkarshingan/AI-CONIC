"""
setup.py – Run this ONCE before starting the app.
It creates attendance.xlsx with all course sheets and validates the environment.
"""

import os
import sys
import csv
import pandas as pd

COURSES          = ["AI", "ML", "DBMS", "Python", "Data Science"]
ATTENDANCE_EXCEL = "attendance.xlsx"
STUDENTS_CSV     = "students.csv"
DATASET_FOLDER   = "dataset"

def banner(text):
    print("\n" + "─" * 55)
    print(f"  {text}")
    print("─" * 55)

def check_python():
    banner("Checking Python version")
    v = sys.version_info
    print(f"  Python {v.major}.{v.minor}.{v.micro}")
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        print("  ⚠  Python 3.8+ required.")
        sys.exit(1)
    print("  ✅ OK")

def check_packages():
    banner("Checking required packages")
    required = {
        "flask"   : "Flask",
        "pandas"  : "pandas",
        "openpyxl": "openpyxl",
        "numpy"   : "numpy",
        "PIL"     : "Pillow",
    }
    optional = {
        "cv2"            : "opencv-python",
        "face_recognition": "face_recognition",
    }
    all_ok = True
    for mod, pkg in required.items():
        try:
            __import__(mod)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg}  →  pip install {pkg}")
            all_ok = False

    print()
    print("  Optional (for real face recognition):")
    for mod, pkg in optional.items():
        try:
            __import__(mod)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ⚠  {pkg} not installed – demo mode will be used")

    if not all_ok:
        print("\n  Install missing packages then re-run setup.py")
        sys.exit(1)

def create_excel():
    banner("Creating attendance.xlsx")
    if os.path.exists(ATTENDANCE_EXCEL):
        print(f"  ℹ  {ATTENDANCE_EXCEL} already exists – skipping.")
        return
    cols = ["Student_ID", "Name", "Date", "Time", "Status"]
    with pd.ExcelWriter(ATTENDANCE_EXCEL, engine="openpyxl") as writer:
        for course in COURSES:
            pd.DataFrame(columns=cols).to_excel(writer, sheet_name=course, index=False)
    print(f"  ✅ {ATTENDANCE_EXCEL} created with sheets: {', '.join(COURSES)}")

def create_csv():
    banner("Checking students.csv")
    if os.path.exists(STUDENTS_CSV):
        print(f"  ℹ  {STUDENTS_CSV} already exists – skipping.")
        return
    with open(STUDENTS_CSV, "w", newline="") as f:
        csv.writer(f).writerow(["Student_ID", "Name", "Parent_Email", "Courses"])
    print(f"  ✅ {STUDENTS_CSV} created.")

def create_folders():
    banner("Creating required folders")
    for folder in [DATASET_FOLDER, "static", "templates"]:
        os.makedirs(folder, exist_ok=True)
        print(f"  ✅ {folder}/")

def print_next_steps():
    banner("Setup complete! Next steps")
    print("""
  1. Set email credentials (for absence alerts):
       Windows : set EMAIL_ADDRESS=your@gmail.com
                 set EMAIL_PASSWORD=your_app_password
       Mac/Linux: export EMAIL_ADDRESS=your@gmail.com
                  export EMAIL_PASSWORD=your_app_password

  2. Start the server:
       python app.py

  3. Open in browser:
       http://127.0.0.1:5000

  4. Register students at:
       http://127.0.0.1:5000/register
""")

if __name__ == "__main__":
    print("\n  AI Smart Attendance System – Setup")
    check_python()
    check_packages()
    create_folders()
    create_csv()
    create_excel()
    print_next_steps()
