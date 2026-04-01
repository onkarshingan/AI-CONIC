# AI-Powered Smart Attendance System using Computer Vision

## Project Overview
An end-to-end web application that automates classroom attendance using facial recognition, replacing manual roll-calls with real-time AI detection.

---

## Problem Statement
Traditional attendance systems are time-consuming, error-prone, and vulnerable to proxy attendance. This project leverages Computer Vision to solve these problems automatically and accurately.

---

## AI Model Explanation
| Component | Library | Role |
|-----------|---------|------|
| Face Detection | OpenCV | Locate faces in webcam frames |
| Face Encoding | face_recognition (dlib) | Convert face to 128-d vector |
| Face Matching | Euclidean Distance | Compare live face to stored encodings |

The system encodes each registered student's face into a 128-dimensional numerical vector. When a new face appears on the webcam, it computes the distance between the live encoding and all stored encodings. If the distance is below `0.5` (tolerance), it's a match.

---

## Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.10+, Flask, Flask-CORS
- **AI / CV**: OpenCV, face_recognition, dlib
- **Data**: Pandas, OpenPyXL
- **Email**: Python smtplib (SMTP over SSL)
- **Charts**: Chart.js

---

## Folder Structure
```
smart-attendance-system/
├── app.py                  # Flask backend (all routes + AI logic)
├── requirements.txt        # Python dependencies
├── attendance.xlsx         # Auto-generated attendance records
├── students.csv            # Student registry
├── dataset/                # Student face images
│   └── Student_Name/
│       ├── image1.jpg
│       └── ...
├── templates/
│   ├── index.html          # Home / landing page
│   ├── register.html       # Student registration
│   ├── attendance.html     # Live scanning interface
│   └── dashboard.html      # Analytics dashboard
├── static/
│   ├── style.css           # All styles
│   └── script.js           # Shared JS utilities
└── README.md
```

---

## Installation Steps

### 1. Clone / download the project
```bash
cd smart-attendance-system
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate
```

### 3. Install core dependencies
```bash
pip install flask flask-cors pandas openpyxl numpy Pillow
```

### 4. Install computer vision libraries (optional – for real recognition)
```bash
# macOS / Linux
pip install cmake dlib face_recognition opencv-python

# Windows (recommended: use pre-built wheels)
pip install opencv-python
pip install https://github.com/jloh02/dlib/releases/download/v19.22/dlib-19.22.0-cp310-cp310-win_amd64.whl
pip install face_recognition
```
> **Note:** If `face_recognition` / `dlib` cannot be installed, the system runs in **Demo Mode** – all features work but face matching returns a mock student.

### 5. Configure email (optional)
Set environment variables before running:
```bash
export EMAIL_ADDRESS="your_gmail@gmail.com"
export EMAIL_PASSWORD="your_16_char_app_password"
```
> Enable **2-Factor Auth** on Gmail and generate an **App Password** (not your normal password).

---

## How to Run
```bash
python app.py
```
Open your browser at: **http://127.0.0.1:5000**

---

## How Attendance is Recorded
1. Teacher selects the course and clicks **Start Scanning**.
2. Webcam captures frames every 1.5 seconds.
3. System requires a face to be present for **3 continuous seconds** (anti-proxy).
4. Matched student is marked **Present** in `attendance.xlsx` under the selected course sheet.
5. Duplicate entries for the same student/day are prevented automatically.

---

## How Email Alerts Work
- When a student is manually marked **Absent** (via the UI or API), `send_absence_email()` is called.
- Python's `smtplib` connects to Gmail's SMTP server over SSL (port 465).
- An email is sent to the **parent's email** stored in `students.csv`.
- The email contains the student name, ID, course, and date.

---

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/register` | Registration page |
| GET | `/attendance` | Attendance scanning page |
| GET | `/dashboard` | Analytics dashboard |
| GET | `/api/students` | List all students |
| POST | `/api/register` | Register new student |
| POST | `/api/recognize` | Recognise face from frame |
| POST | `/api/mark_absent` | Mark student absent + send email |
| GET | `/api/attendance?course=AI` | Get attendance records |
| GET | `/api/dashboard` | Get dashboard stats |
| GET | `/api/download_excel` | Download attendance.xlsx |
| GET | `/api/courses` | List all courses |

---

## Future Scope / Improvements
1. **Mobile App Integration** – React Native app for teachers and parents
2. **Cloud Database** – PostgreSQL / Firebase instead of local Excel
3. **Face Mask Detection** – YOLOv8-based mask detection before recognition
4. **Advanced Anti-Spoofing** – Liveness detection to prevent photo attacks
5. **College ERP Integration** – Push attendance to existing ERP systems (SAP, Fedena)
6. **Multi-Camera Support** – Handle large lecture halls with multiple cameras
7. **Real-Time Dashboard** – WebSocket-based live updates without page refresh
8. **Offline Mode** – IndexedDB caching for poor connectivity environments

---

## Team / Credits
- **Project Type**: College AI Mini Project
- **Subject**: Artificial Intelligence / Computer Vision
- **Year**: 2026

---

## License
For educational use only.
