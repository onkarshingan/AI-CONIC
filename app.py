"""
AI-Powered Smart Attendance System using Computer Vision
Flask Backend - Main Application
"""

import os
import csv
import json
import base64
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np

# ── Try importing face_recognition (optional – falls back to mock) ──────────
try:
    import face_recognition
    import cv2
    FACE_RECOGNITION_AVAILABLE = True
    print("[INFO] face_recognition + OpenCV loaded successfully.")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("[WARN] face_recognition / OpenCV not installed – running in DEMO mode.")

app = Flask(__name__)

# Enable CORS for all routes
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# ── Configuration ─────────────────────────────────────────────────────────────
DATASET_FOLDER   = "dataset"
STUDENTS_CSV     = "students.csv"
ATTENDANCE_EXCEL = "attendance.xlsx"
COURSES          = ["AI", "ML", "DBMS", "Python", "Data Science"]

# Email configuration – fill in real credentials or set via environment vars
EMAIL_ADDRESS  = os.environ.get("EMAIL_ADDRESS", "your_email@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your_app_password")

# ── Ensure required folders/files exist ──────────────────────────────────────
os.makedirs(DATASET_FOLDER, exist_ok=True)

def init_students_csv():
    """Create students.csv with headers if it does not exist."""
    if not os.path.exists(STUDENTS_CSV):
        with open(STUDENTS_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Student_ID", "Name", "Parent_Email", "Courses"])

def init_attendance_excel():
    """Create attendance.xlsx with one sheet per course if it does not exist."""
    if not os.path.exists(ATTENDANCE_EXCEL):
        with pd.ExcelWriter(ATTENDANCE_EXCEL, engine="openpyxl") as writer:
            for course in COURSES:
                df = pd.DataFrame(columns=["Student_ID", "Name", "Date", "Time", "Status"])
                df.to_excel(writer, sheet_name=course, index=False)

init_students_csv()
init_attendance_excel()

# ══════════════════════════════════════════════════════════════════════════════
# FACE RECOGNITION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def load_known_faces():
    """
    Walk the dataset/ folder and encode every student image.
    Returns (encodings_list, names_list).
    """
    encodings, names = [], []
    if not FACE_RECOGNITION_AVAILABLE:
        return encodings, names

    for student_name in os.listdir(DATASET_FOLDER):
        student_path = os.path.join(DATASET_FOLDER, student_name)
        if not os.path.isdir(student_path):
            continue
        for img_file in os.listdir(student_path):
            img_path = os.path.join(student_path, img_file)
            try:
                image = face_recognition.load_image_file(img_path)
                enc   = face_recognition.face_encodings(image)
                if enc:
                    encodings.append(enc[0])
                    names.append(student_name)
            except Exception as e:
                print(f"[WARN] Could not encode {img_path}: {e}")
    print(f"[INFO] Loaded {len(encodings)} face encodings.")
    return encodings, names


def recognize_face_from_base64(image_b64: str):
    """
    Decode a base64 image, detect & recognise faces.
    Returns list of recognised student names (empty if none).
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Demo mode – return a mock student
        return ["Demo_Student"]

    known_encodings, known_names = load_known_faces()
    if not known_encodings:
        return []

    # Decode image
    img_data    = base64.b64decode(image_b64.split(",")[-1])
    nparr       = np.frombuffer(img_data, np.uint8)
    frame       = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_frame   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locs   = face_recognition.face_locations(rgb_frame)
    face_encs   = face_recognition.face_encodings(rgb_frame, face_locs)

    recognised = []
    for enc in face_encs:
        matches    = face_recognition.compare_faces(known_encodings, enc, tolerance=0.5)
        face_dists = face_recognition.face_distance(known_encodings, enc)
        if True in matches:
            best_idx = np.argmin(face_dists)
            if matches[best_idx]:
                recognised.append(known_names[best_idx])
    return recognised

# ══════════════════════════════════════════════════════════════════════════════
# CSV / EXCEL HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_students():
    """Return all students as a list of dicts."""
    students = []
    if not os.path.exists(STUDENTS_CSV):
        return students
    with open(STUDENTS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students.append(row)
    return students


def get_student_by_name(name: str):
    for s in get_students():
        if s["Name"].lower() == name.lower():
            return s
    return None


def mark_attendance_in_excel(student_id, name, course, status="Present"):
    """Append an attendance record to the appropriate Excel sheet."""
    now  = datetime.datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M")

    try:
        df = pd.read_excel(ATTENDANCE_EXCEL, sheet_name=course)
    except Exception:
        df = pd.DataFrame(columns=["Student_ID", "Name", "Date", "Time", "Status"])

    # Avoid duplicate entries for the same student on the same date
    existing = df[(df["Student_ID"].astype(str) == str(student_id)) & (df["Date"] == date)]
    if not existing.empty:
        return False  # Already marked

    new_row = pd.DataFrame([{
        "Student_ID": student_id,
        "Name"      : name,
        "Date"      : date,
        "Time"      : time,
        "Status"    : status
    }])
    df = pd.concat([df, new_row], ignore_index=True)

    # Write back – preserve all sheets
    try:
        with pd.ExcelWriter(ATTENDANCE_EXCEL, engine="openpyxl", mode="a",
                            if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name=course, index=False)
    except Exception:
        # Fallback: rewrite entire file
        with pd.ExcelWriter(ATTENDANCE_EXCEL, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=course, index=False)
    return True

# ══════════════════════════════════════════════════════════════════════════════
# EMAIL HELPER
# ══════════════════════════════════════════════════════════════════════════════

def send_absence_email(parent_email: str, student_name: str,
                       student_id: str, course: str):
    """Send an absence notification email to the parent."""
    date_str = datetime.datetime.now().strftime("%d %B %Y")
    subject  = "Attendance Alert – Absence Notification"
    body     = f"""Dear Parent,

Your child {student_name} (Student ID: {student_id}) was absent for the
course '{course}' on {date_str}.

Please ensure regular attendance.

Regards,
College Attendance System
AI-Powered Smart Attendance System
"""
    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = parent_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, parent_email, msg.as_string())
        print(f"[EMAIL] Absence alert sent to {parent_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# FLASK ROUTES – Pages
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/attendance")
def attendance():
    return render_template("attendance.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/student_report/<student_id>")
def student_report_page(student_id):
    return render_template("student_report.html")

# ══════════════════════════════════════════════════════════════════════════════
# FLASK ROUTES – API
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/students", methods=["GET"])
def api_students():
    """Return all registered students."""
    return jsonify(get_students())


@app.route("/api/register", methods=["POST"])
def api_register():
    """Register a new student (images captured on client, sent as base64 list)."""
    data         = request.json
    student_id   = data.get("student_id")
    name         = data.get("name", "").strip().replace(" ", "_")
    parent_email = data.get("parent_email")
    courses      = data.get("courses", [])
    images       = data.get("images", [])   # list of base64 strings

    if not all([student_id, name, parent_email, courses]):
        return jsonify({"success": False, "message": "All fields are required."}), 400

    # Save images
    student_folder = os.path.join(DATASET_FOLDER, name)
    os.makedirs(student_folder, exist_ok=True)

    for idx, img_b64 in enumerate(images):
        try:
            img_data = base64.b64decode(img_b64.split(",")[-1])
            img_path = os.path.join(student_folder, f"image{idx+1}.jpg")
            with open(img_path, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"[WARN] Could not save image {idx}: {e}")

    # Save student record to CSV
    with open(STUDENTS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([student_id, name, parent_email, ",".join(courses)])

    return jsonify({
        "success": True,
        "message": f"Student {name} registered with {len(images)} images.",
        "images_saved": len(images)
    })


@app.route("/api/recognize", methods=["POST"])
def api_recognize():
    """
    Receive a webcam frame (base64), recognise faces,
    mark attendance, send emails for absences.
    """
    data    = request.json
    image   = data.get("image")
    course  = data.get("course", "AI")

    if not image:
        return jsonify({"success": False, "message": "No image provided."}), 400

    recognised = recognize_face_from_base64(image)

    results = []
    for student_name in recognised:
        student = get_student_by_name(student_name)
        if not student:
            results.append({"name": student_name, "status": "Unknown – not in CSV"})
            continue

        marked = mark_attendance_in_excel(
            student["Student_ID"], student_name, course, "Present"
        )
        results.append({
            "name"      : student_name,
            "student_id": student["Student_ID"],
            "course"    : course,
            "status"    : "Marked Present" if marked else "Already Marked"
        })

    return jsonify({"success": True, "recognised": results})


@app.route("/api/mark_absent", methods=["POST"])
def api_mark_absent():
    """Mark a student absent and send email notification."""
    data       = request.json
    student_id = data.get("student_id")
    course     = data.get("course", "AI")

    students = get_students()
    student  = next((s for s in students if s["Student_ID"] == str(student_id)), None)
    if not student:
        return jsonify({"success": False, "message": "Student not found."}), 404

    mark_attendance_in_excel(student_id, student["Name"], course, "Absent")
    email_sent = send_absence_email(
        student["Parent_Email"], student["Name"], student_id, course
    )
    return jsonify({
        "success"   : True,
        "message"   : f"{student['Name']} marked absent for {course}.",
        "email_sent": email_sent
    })


@app.route("/api/attendance", methods=["GET"])
def api_attendance():
    """Return attendance records, optionally filtered by course."""
    course = request.args.get("course", "AI")
    try:
        df = pd.read_excel(ATTENDANCE_EXCEL, sheet_name=course)
        return jsonify(df.to_dict(orient="records"))
    except Exception:
        return jsonify([])


@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    """Return summary statistics for the dashboard."""
    students      = get_students()
    total_students = len(students)
    today_str     = datetime.datetime.now().strftime("%d-%m-%Y")

    present_today = set()
    absent_today  = set()
    course_stats  = {}

    for course in COURSES:
        try:
            df      = pd.read_excel(ATTENDANCE_EXCEL, sheet_name=course)
            today_df = df[df["Date"] == today_str]
            p = len(today_df[today_df["Status"] == "Present"])
            a = len(today_df[today_df["Status"] == "Absent"])
            course_stats[course] = {"present": p, "absent": a,
                                    "percentage": round(p/(p+a)*100, 1) if (p+a) else 0}
            present_today.update(today_df[today_df["Status"] == "Present"]["Name"].tolist())
            absent_today.update(today_df[today_df["Status"] == "Absent"]["Name"].tolist())
        except Exception:
            course_stats[course] = {"present": 0, "absent": 0, "percentage": 0}

    return jsonify({
        "total_students" : total_students,
        "present_today"  : len(present_today),
        "absent_today"   : len(absent_today),
        "course_stats"   : course_stats,
        "courses"        : COURSES
    })


@app.route("/api/download_excel")
def api_download_excel():
    """Download the attendance Excel file."""
    if os.path.exists(ATTENDANCE_EXCEL):
        return send_file(ATTENDANCE_EXCEL, as_attachment=True)
    return jsonify({"error": "File not found"}), 404


@app.route("/api/courses")
def api_courses():
    return jsonify(COURSES)


@app.route("/api/delete_student", methods=["POST"])
def api_delete_student():
    """Remove a student from students.csv and their image dataset folder."""
    data       = request.json
    student_id = str(data.get("student_id", "")).strip()
    if not student_id:
        return jsonify({"success": False, "message": "No student_id provided."}), 400

    students = get_students()
    target   = next((s for s in students if str(s["Student_ID"]) == student_id), None)
    if not target:
        return jsonify({"success": False, "message": "Student not found."}), 404

    # Remove from CSV
    remaining = [s for s in students if str(s["Student_ID"]) != student_id]
    with open(STUDENTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Student_ID", "Name", "Parent_Email", "Courses"])
        writer.writeheader()
        writer.writerows(remaining)

    # Remove dataset folder
    import shutil
    folder = os.path.join(DATASET_FOLDER, target["Name"])
    if os.path.isdir(folder):
        shutil.rmtree(folder)

    return jsonify({"success": True, "message": f"Student {target['Name']} deleted."})


@app.route("/api/student_report/<student_id>")
def api_student_report(student_id):
    """Return full attendance history for a single student across all courses."""
    student = next((s for s in get_students() if str(s["Student_ID"]) == str(student_id)), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    report = {"student": student, "courses": {}}
    for course in COURSES:
        try:
            df   = pd.read_excel(ATTENDANCE_EXCEL, sheet_name=course)
            rows = df[df["Student_ID"].astype(str) == str(student_id)]
            p    = int((rows["Status"] == "Present").sum())
            a    = int((rows["Status"] == "Absent").sum())
            report["courses"][course] = {
                "present"   : p,
                "absent"    : a,
                "percentage": round(p / (p + a) * 100, 1) if (p + a) else 0,
                "records"   : rows.to_dict(orient="records")
            }
        except Exception:
            report["courses"][course] = {"present": 0, "absent": 0, "percentage": 0, "records": []}

    return jsonify(report)


@app.route("/api/add_course", methods=["POST"])
def api_add_course():
    """Add a new course sheet to attendance.xlsx."""
    data   = request.json
    course = data.get("course", "").strip()
    if not course:
        return jsonify({"success": False, "message": "Course name required."}), 400
    if course in COURSES:
        return jsonify({"success": False, "message": "Course already exists."}), 400

    COURSES.append(course)
    cols = ["Student_ID", "Name", "Date", "Time", "Status"]
    try:
        with pd.ExcelWriter(ATTENDANCE_EXCEL, engine="openpyxl", mode="a",
                            if_sheet_exists="overlay") as writer:
            pd.DataFrame(columns=cols).to_excel(writer, sheet_name=course, index=False)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True, "message": f"Course '{course}' added.", "courses": COURSES})


@app.route("/api/today_summary")
def api_today_summary():
    """Return today's present/absent student names for a quick roll-call view."""
    today_str = datetime.datetime.now().strftime("%d-%m-%Y")
    course    = request.args.get("course", COURSES[0])
    try:
        df       = pd.read_excel(ATTENDANCE_EXCEL, sheet_name=course)
        today_df = df[df["Date"] == today_str]
        present  = today_df[today_df["Status"] == "Present"][["Student_ID","Name"]].to_dict(orient="records")
        absent   = today_df[today_df["Status"] == "Absent"][["Student_ID","Name"]].to_dict(orient="records")
    except Exception:
        present, absent = [], []

    # Students not yet scanned
    all_students = get_students()
    scanned_ids  = {str(r["Student_ID"]) for r in present + absent}
    not_scanned  = [s for s in all_students if str(s["Student_ID"]) not in scanned_ids]

    return jsonify({
        "date"       : today_str,
        "course"     : course,
        "present"    : present,
        "absent"     : absent,
        "not_scanned": not_scanned
    })


@app.route("/api/test_email", methods=["POST"])
def api_test_email():
    """Send a test email to verify SMTP credentials are working."""
    data  = request.json
    email = data.get("email", EMAIL_ADDRESS)
    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = email
        msg["Subject"] = "AttendAI – SMTP Test ✅"
        msg.attach(MIMEText(
            "This is a test email from your AI Smart Attendance System.\n\n"
            "SMTP is configured correctly!",
            "plain"
        ))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        return jsonify({"success": True, "message": f"Test email sent to {email}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  AI Smart Attendance System – Flask Backend")
    print("  Visit: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
