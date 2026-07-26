from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = "mediconnect_secret_key_2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mediconnect.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

db = SQLAlchemy(app)


# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer)
    fee = db.Column(db.Float, default=0.0)
    availability = db.Column(db.String(200), default="Mon-Fri, 9am-5pm")
    about = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('DoctorReview', backref='doctor', lazy=True)


class DoctorReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="appointments")
    doctor = db.relationship("Doctor", backref="appointments")


class MedicineReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    medicine_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    reminder_times = db.Column(db.String(500), nullable=False)
    language = db.Column(db.String(20), default="te-IN")
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
# SEED DEMO DOCTORS
# ─────────────────────────────────────────────

def seed_demo_doctors():
    if Doctor.query.count() == 0:
        demo = [
            Doctor(name="Priya Sharma", email="priya@mediconnect.com",
                   password=generate_password_hash("doctor123"),
                   specialization="Cardiologist", experience=12, fee=800,
                   availability="Mon-Sat, 9am-6pm",
                   about="Expert in cardiovascular diseases with 12 years at Apollo Hospital."),
            Doctor(name="Ravi Kumar", email="ravi@mediconnect.com",
                   password=generate_password_hash("doctor123"),
                   specialization="General Physician", experience=8, fee=300,
                   availability="Mon-Fri, 10am-7pm",
                   about="Experienced general physician specialising in chronic disease management."),
            Doctor(name="Anita Reddy", email="anita@mediconnect.com",
                   password=generate_password_hash("doctor123"),
                   specialization="Dermatologist", experience=6, fee=600,
                   availability="Tue-Sun, 11am-5pm",
                   about="Skin specialist with expertise in acne, eczema, and cosmetic dermatology."),
            Doctor(name="Suresh Patel", email="suresh@mediconnect.com",
                   password=generate_password_hash("doctor123"),
                   specialization="Orthopedic", experience=15, fee=900,
                   availability="Mon-Fri, 9am-4pm",
                   about="Senior orthopedic surgeon specialising in joint replacement and sports injuries."),
            Doctor(name="Meena Nair", email="meena@mediconnect.com",
                   password=generate_password_hash("doctor123"),
                   specialization="Pediatrician", experience=10, fee=400,
                   availability="Mon-Sat, 8am-6pm",
                   about="Child health specialist with a gentle approach and expertise in vaccinations."),
            Doctor(name="Arun Joshi", email="arun@mediconnect.com",
                   password=generate_password_hash("doctor123"),
                   specialization="Psychiatrist", experience=9, fee=700,
                   availability="Tue-Sat, 2pm-8pm",
                   about="Mental health specialist providing therapy and medication management."),
        ]
        for d in demo:
            db.session.add(d)
        db.session.commit()


# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


# ─────────────────────────────────────────────
# PATIENT AUTH
# ─────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        blood_group = request.form["blood"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("register"))

        new_user = User(
            name=name, email=email,
            password=generate_password_hash(password),
            age=age, blood_group=blood_group
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = "patient"
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")


# ─────────────────────────────────────────────
# PATIENT DASHBOARD
# ─────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    records = (MedicalRecord.query
               .filter_by(user_id=session["user_id"])
               .order_by(MedicalRecord.created_at.desc())
               .limit(3).all())
    total_records = MedicalRecord.query.filter_by(user_id=session["user_id"]).count()
    appointments = (Appointment.query
                    .filter_by(user_id=session["user_id"])
                    .order_by(Appointment.created_at.desc())
                    .limit(3).all())
    total_appointments = Appointment.query.filter_by(user_id=session["user_id"]).count()
    reminders = MedicineReminder.query.filter_by(user_id=session["user_id"], is_active=True).all()
    total_reminders = len(reminders)

    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        records=records, total_records=total_records,
        appointments=appointments, total_appointments=total_appointments,
        reminders=reminders, total_reminders=total_reminders,
        greeting=greeting
    )


# ─────────────────────────────────────────────
# MEDICAL RECORDS
# ─────────────────────────────────────────────

@app.route("/records")
def records():
    logged_in = "user_id" in session and session.get("role") == "patient"
    all_records = []
    if logged_in:
        all_records = (MedicalRecord.query
                       .filter_by(user_id=session["user_id"])
                       .order_by(MedicalRecord.created_at.desc())
                       .all())
    return render_template("record.html", records=all_records, logged_in=logged_in)


@app.route("/records/add", methods=["GET", "POST"])
def add_record():
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        filename = None
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename != "" and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        record = MedicalRecord(
            user_id=session["user_id"],
            title=request.form["title"],
            record_type=request.form["record_type"],
            description=request.form["description"],
            date=request.form["date"],
            filename=filename
        )
        db.session.add(record)
        db.session.commit()
        flash("Medical record added successfully!", "success")
        return redirect(url_for("records"))
    return render_template("add_record.html")


@app.route("/records/delete/<int:record_id>")
def delete_record(record_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    record = MedicalRecord.query.get_or_404(record_id)
    if record.user_id != session["user_id"]:
        flash("You cannot delete this record.", "error")
        return redirect(url_for("records"))
    if record.filename:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], record.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(record)
    db.session.commit()
    flash("Record deleted.", "success")
    return redirect(url_for("records"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ─────────────────────────────────────────────
# DOCTORS & APPOINTMENTS
# ─────────────────────────────────────────────

@app.route("/doctors")
def doctors():
    specialization = request.args.get("specialization", "all")
    query_text = request.args.get("q", "").strip()

    doctor_query = Doctor.query
    if specialization and specialization != "all":
        doctor_query = doctor_query.filter_by(specialization=specialization)
    if query_text:
        doctor_query = doctor_query.filter(
            Doctor.name.ilike(f"%{query_text}%") |
            Doctor.specialization.ilike(f"%{query_text}%") |
            Doctor.about.ilike(f"%{query_text}%")
        )

    all_doctors = doctor_query.order_by(Doctor.name).all()

    rating_rows = (db.session.query(
        DoctorReview.doctor_id,
        func.avg(DoctorReview.rating).label("avg_rating"),
        func.count(DoctorReview.id).label("review_count")
    )
    .group_by(DoctorReview.doctor_id)
    .all())
    ratings = {row.doctor_id: {"avg_rating": round(row.avg_rating or 0, 1), "review_count": row.review_count} for row in rating_rows}

    for doctor in all_doctors:
        doctor.avg_rating = ratings.get(doctor.id, {}).get("avg_rating", 0)
        doctor.review_count = ratings.get(doctor.id, {}).get("review_count", 0)

    specializations = [row[0] for row in db.session.query(Doctor.specialization).distinct().order_by(Doctor.specialization).all()]

    return render_template(
        "doctors.html",
        doctors=all_doctors,
        specializations=specializations,
        selected_specialization=specialization,
        query_text=query_text
    )


@app.route("/doctor/<int:doctor_id>")
def doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    reviews = (DoctorReview.query
               .filter_by(doctor_id=doctor_id)
               .order_by(DoctorReview.created_at.desc())
               .all())

    avg_rating = 0
    review_count = len(reviews)
    if review_count:
        avg_rating = round(sum(review.rating for review in reviews) / review_count, 1)

    can_review = "user_id" in session and session.get("role") == "patient"
    return render_template(
        "doctor_detail.html",
        doctor=doctor,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=review_count,
        can_review=can_review
    )


@app.route("/doctor/<int:doctor_id>/review", methods=["POST"])
def submit_doctor_review(doctor_id):
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login as a patient to leave a review.", "error")
        return redirect(url_for("doctor_profile", doctor_id=doctor_id))

    doctor = Doctor.query.get_or_404(doctor_id)
    rating = int(request.form.get("rating", 0))
    comment = request.form.get("comment", "").strip()
    rating = min(max(rating, 1), 5)

    review = DoctorReview(
        doctor_id=doctor.id,
        user_id=session["user_id"],
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    flash("Thank you for reviewing Dr. {}.".format(doctor.name), "success")
    return redirect(url_for("doctor_profile", doctor_id=doctor_id))


@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
def book_appointment(doctor_id):
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == "POST":
        appointment = Appointment(
            user_id=session["user_id"],
            doctor_id=doctor_id,
            date=request.form["date"],
            time=request.form["time"],
            reason=request.form["reason"]
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("book_appointment.html", doctor=doctor)


@app.route("/appointments")
def appointments():
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    all_appointments = (Appointment.query
                        .filter_by(user_id=session["user_id"])
                        .order_by(Appointment.created_at.desc())
                        .all())
    return render_template("appointments.html", appointments=all_appointments)


@app.route("/appointments/delete/<int:appointment_id>")
def delete_appointment_user(appointment_id):
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id != session["user_id"]:
        flash("You cannot cancel this appointment.", "error")
        return redirect(url_for("appointments"))
    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment cancelled.", "success")
    return redirect(url_for("appointments"))


@app.route("/account/update", methods=["GET", "POST"])
def update_account():
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        email = request.form["email"]
        if User.query.filter(User.email == email, User.id != user.id).first():
            flash("Email already registered.", "error")
            return redirect(url_for("update_account"))

        user.name = request.form["name"]
        user.email = email
        age_value = request.form.get("age", "").strip()
        user.age = int(age_value) if age_value.isdigit() else None
        user.blood_group = request.form.get("blood_group", "")
        password = request.form.get("password", "").strip()
        if password:
            user.password = generate_password_hash(password)
        db.session.commit()
        session["user_name"] = user.name
        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("patient_update.html", user=user)


@app.route("/account")
def account():
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    return render_template("account.html", user=user)


# ─────────────────────────────────────────────
# SYMPTOM CHECKER
# ─────────────────────────────────────────────

@app.route("/symptom-checker")
def symptom_checker():
    logged_in = "user_id" in session and session.get("role") == "patient"
    return render_template("symptoms_checker.html", logged_in=logged_in)


@app.route("/api/analyze-symptoms", methods=["POST"])
def analyze_symptoms_api():
    """Server-side proxy to Anthropic API — keeps the API key out of the browser."""
    if "user_id" not in session or session.get("role") != "patient":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    symptoms = (data.get("symptoms") or "").strip()
    age = data.get("age", "")
    gender = data.get("gender", "")

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"error": "API key not configured"}), 500

    prompt = (
        f"You are a medical assistant AI. A patient"
        f"{' aged ' + str(age) if age else ''}"
        f"{' (' + gender + ')' if gender else ''} "
        f'reports these symptoms: "{symptoms}"\n\n'
        "Respond ONLY with valid JSON (no markdown, no extra text) in exactly this format:\n"
        '{"severity":"low"|"medium"|"high","severityLabel":"brief label",'
        '"conditions":[{"name":"...","desc":"..."}],'
        '"homeRemedies":["..."],"actions":["..."],"warnings":["..."]}'
    )

    import urllib.request as urlreq

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urlreq.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
    )

    try:
        with urlreq.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        text = "".join(c.get("text", "") for c in result.get("content", []))
        parsed = json.loads(text.strip())
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# MEDICINE REMINDERS
# ─────────────────────────────────────────────

@app.route("/reminders")
def reminders():
    logged_in = "user_id" in session and session.get("role") == "patient"
    all_reminders = []
    if logged_in:
        all_reminders = (MedicineReminder.query
                         .filter_by(user_id=session["user_id"])
                         .order_by(MedicineReminder.created_at.desc())
                         .all())
    return render_template("reminders.html", reminders=all_reminders, logged_in=logged_in)


@app.route("/reminders/add", methods=["GET", "POST"])
def add_reminder():
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        times = request.form.getlist("reminder_times")
        reminder = MedicineReminder(
            user_id=session["user_id"],
            medicine_name=request.form["medicine_name"],
            dosage=request.form["dosage"],
            frequency=request.form["frequency"],
            reminder_times=",".join(times),
            language=request.form.get("language", "te-IN"),
            start_date=request.form["start_date"],
            end_date=request.form.get("end_date") or None,
            notes=request.form.get("notes") or None
        )
        db.session.add(reminder)
        db.session.commit()
        flash("Medicine reminder added successfully!", "success")
        return redirect(url_for("reminders"))
    return render_template("add_reminder.html")


@app.route("/reminders/delete/<int:reminder_id>")
def delete_reminder(reminder_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    reminder = MedicineReminder.query.get_or_404(reminder_id)
    if reminder.user_id != session["user_id"]:
        flash("You cannot delete this reminder.", "error")
        return redirect(url_for("reminders"))
    db.session.delete(reminder)
    db.session.commit()
    flash("Reminder deleted.", "success")
    return redirect(url_for("reminders"))


@app.route("/reminders/toggle/<int:reminder_id>")
def toggle_reminder(reminder_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    reminder = MedicineReminder.query.get_or_404(reminder_id)
    if reminder.user_id != session["user_id"]:
        return redirect(url_for("reminders"))
    reminder.is_active = not reminder.is_active
    db.session.commit()
    flash("Reminder " + ("activated." if reminder.is_active else "paused."), "success")
    return redirect(url_for("reminders"))


@app.route("/account/delete")
def delete_account():
    if "user_id" not in session or session.get("role") != "patient":
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("home"))

    records = MedicalRecord.query.filter_by(user_id=user.id).all()
    for record in records:
        if record.filename:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], record.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        db.session.delete(record)

    Appointment.query.filter_by(user_id=user.id).delete()
    MedicineReminder.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("Your patient account and all personal data have been deleted.", "success")
    return redirect(url_for("home"))


@app.route("/doctor/account/delete")
def delete_doctor_account():
    if "doctor_id" not in session or session.get("role") != "doctor":
        flash("Please login as a doctor.", "error")
        return redirect(url_for("doctor_login"))

    doctor = Doctor.query.get(session["doctor_id"])
    if not doctor:
        session.clear()
        return redirect(url_for("home"))

    Appointment.query.filter_by(doctor_id=doctor.id).delete()
    db.session.delete(doctor)
    db.session.commit()
    session.clear()
    flash("Your doctor account has been deleted.", "success")
    return redirect(url_for("home"))


# ─────────────────────────────────────────────
# DOCTOR AUTH
# ─────────────────────────────────────────────

@app.route("/doctor/register", methods=["GET", "POST"])
def doctor_register():
    if request.method == "POST":
        email = request.form["email"]
        if Doctor.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("doctor_register"))

        new_doctor = Doctor(
            name=request.form["name"],
            email=email,
            password=generate_password_hash(request.form["password"]),
            specialization=request.form["specialization"],
            experience=int(request.form["experience"]),
            fee=float(request.form["fee"]),
            about=request.form.get("about", "")
        )
        db.session.add(new_doctor)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("doctor_login"))
    return render_template("doctor_register.html")


@app.route("/doctor/login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        doctor = Doctor.query.filter_by(email=email).first()

        if doctor and check_password_hash(doctor.password, password):
            session["doctor_id"] = doctor.id
            session["doctor_name"] = doctor.name
            session["role"] = "doctor"
            flash(f"Welcome back, Dr. {doctor.name}!", "success")
            return redirect(url_for("doctor_dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("doctor_login"))
    return render_template("doctor_login.html")


# ─────────────────────────────────────────────
# DOCTOR DASHBOARD
# ─────────────────────────────────────────────

@app.route("/doctor/dashboard")
def doctor_dashboard():
    if "doctor_id" not in session or session.get("role") != "doctor":
        flash("Please login as a doctor.", "error")
        return redirect(url_for("doctor_login"))

    doctor = Doctor.query.get(session["doctor_id"])
    appointments = (Appointment.query
                    .filter_by(doctor_id=session["doctor_id"])
                    .order_by(Appointment.created_at.desc())
                    .all())
    total_appointments = len(appointments)
    pending = sum(1 for a in appointments if a.status == "Pending")
    patients = (User.query
                .join(Appointment)
                .filter(Appointment.doctor_id == session["doctor_id"])
                .distinct()
                .all())

    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    return render_template(
        "doctor_dashboard.html",
        doctor=doctor,
        appointments=appointments,
        total_appointments=total_appointments,
        pending=pending,
        patients=patients,
        greeting=greeting
    )


@app.route("/doctor/update", methods=["GET", "POST"])
def doctor_update():
    if "doctor_id" not in session or session.get("role") != "doctor":
        return redirect(url_for("doctor_login"))
    doctor = Doctor.query.get(session["doctor_id"])
    if request.method == "POST":
        doctor.fee = float(request.form["fee"])
        doctor.availability = request.form["availability"]
        doctor.about = request.form.get("about", "")
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("doctor_dashboard"))
    return render_template("doctor_update.html", doctor=doctor)


@app.route("/doctor/appointment/<int:appointment_id>/<status>")
def update_appointment(appointment_id, status):
    if "doctor_id" not in session or session.get("role") != "doctor":
        return redirect(url_for("doctor_login"))
    if status not in ("Accepted", "Rejected"):
        flash("Invalid status.", "error")
        return redirect(url_for("doctor_dashboard"))
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != session["doctor_id"]:
        flash("Unauthorised.", "error")
        return redirect(url_for("doctor_dashboard"))
    appointment.status = status
    db.session.commit()
    flash(f"Appointment marked as {status}.", "success")
    return redirect(url_for("doctor_dashboard"))


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_demo_doctors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)