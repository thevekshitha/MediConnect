# MediConnect — Setup Guide

A full-stack health management web app built with Flask.

---

## Features
- Patient registration & login
- Medical records (add, view, delete, file upload)
- Doctor directory with appointment booking
- Doctor dashboard (accept/reject appointments, view patients)
- Medicine reminders with voice alarms (7 Indian languages)
- AI-powered Symptom Checker (via Anthropic Claude API)

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key (for Symptom Checker)
```bash
# Linux / Mac
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```
> Get a free API key at https://console.anthropic.com
> The Symptom Checker falls back to local rule-based analysis if no key is set.

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://127.0.0.1:5000
```

---

## Demo Doctor Logins
Six demo doctors are auto-created on first run. Password for all: `doctor123`

| Doctor | Email | Specialization |
|--------|-------|----------------|
| Dr. Priya Sharma | priya@mediconnect.com | Cardiologist |
| Dr. Ravi Kumar | ravi@mediconnect.com | General Physician |
| Dr. Anita Reddy | anita@mediconnect.com | Dermatologist |
| Dr. Suresh Patel | suresh@mediconnect.com | Orthopedic |
| Dr. Meena Nair | meena@mediconnect.com | Pediatrician |
| Dr. Arun Joshi | arun@mediconnect.com | Psychiatrist |

---

## Project Structure
```
mediconnect/
├── app.py               ← Flask app (routes, models, API)
├── requirements.txt     ← Python dependencies
├── README.md
├── uploads/             ← Uploaded medical files (auto-created)
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── record.html
    ├── add_record.html
    ├── doctors.html
    ├── book_appointment.html
    ├── reminders.html
    ├── add_reminder.html
    ├── symptoms_checker.html
    ├── doctor_login.html
    ├── doctor_register.html
    ├── doctor_dashboard.html
    └── doctor_update.html
```

---

## Notes
- Database: SQLite (`mediconnect.db`) — auto-created on first run
- File uploads stored in `uploads/` folder (PDF, JPG, PNG up to 16MB)
- Voice reminders use the browser's Web Speech API — keep the reminders page open
