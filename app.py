from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
from supabase_client import supabase
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        result = supabase.table("healthcare_worker").select("*").eq("username", username).execute()

        if result.data and result.data[0]["password_hash"] == password:
            worker = result.data[0]
            session["worker_id"] = worker["worker_id"]
            session["username"] = worker["username"]
            session["role"] = worker["role"]
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "worker_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html", username=session["username"], role=session["role"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/register-patient", methods=["GET", "POST"])
def register_patient():
    if "worker_id" not in session:
        return redirect("/login")
    
    error = None
    success = None

    if request.method == "POST":
        national_id = request.form["national_id"]
        name = request.form["name"]
        dob = request.form["dob"]
        pin = request.form["pin"]

        existing = supabase.table("patient").select("*").eq("national_id", national_id).execute()
        if existing.data:
            error = "A patient with this national ID already exists"
        else:
            supabase.table("patient").insert({
                "national_id": national_id,
                "name": name,
                "date_of_birth": dob,
                "pin_hash": pin
            }).execute()
            success = f"Patient {name} registered successfully"

    return render_template("register_patient.html", error=error, success=success)

@app.route("/search-patient", methods=["GET", "POST"])
def search_patient():
    if "worker_id" not in session:
        return redirect("/login")

    patient = None
    error = None

    if request.method == "POST":
        national_id = request.form["national_id"]
        result = supabase.table("patient").select("*").eq("national_id", national_id).execute()

        if result.data:
            patient = result.data[0]
        else:
            error = "No patient found with that national ID"

    return render_template("search_patient.html", patient=patient, error=error)

@app.route("/patient/<patient_id>")
def patient_profile(patient_id):
    if "worker_id" not in session:
        return redirect("/login")

    patient = supabase.table("patient").select("*").eq("patient_id", patient_id).execute()
    records = supabase.table("medical_record").select("*").eq("patient_id", patient_id).order("visit_date", desc=True).execute()

    if not patient.data:
        return redirect("/search-patient")

    supabase.table("audit_log").insert({
        "worker_id": session["worker_id"],
        "action": f"Viewed patient {patient_id}"
    }).execute()

    return render_template("patient_profile.html", patient=patient.data[0], records=records.data, role=session["role"])

@app.route("/add-record/<patient_id>", methods=["GET", "POST"])
def add_record(patient_id):
    if "worker_id" not in session:
        return redirect("/login")
    if session["role"] != "doctor":
        return redirect("/dashboard")

    success = None

    if request.method == "POST":
        supabase.table("medical_record").insert({
            "patient_id": patient_id,
            "worker_id": session["worker_id"],
            "hospital_id": supabase.table("healthcare_worker").select("hospital_id").eq("worker_id", session["worker_id"]).execute().data[0]["hospital_id"],
            "diagnosis": request.form["diagnosis"],
            "medications": request.form["medications"],
            "allergies": request.form["allergies"],
            "procedures": request.form["procedures"]
        }).execute()

        supabase.table("audit_log").insert({
            "worker_id": session["worker_id"],
            "action": f"Added medical record for patient {patient_id}"
        }).execute()

        return redirect(f"/patient/{patient_id}")

    return render_template("add_record.html", patient_id=patient_id)

@app.route("/admin")
def admin():
    if "worker_id" not in session or session["role"] != "admin":
        return redirect("/dashboard")

    workers = supabase.table("healthcare_worker").select("*").execute()
    hospitals = supabase.table("hospital").select("*").execute()
    return render_template("admin.html", workers=workers.data, hospitals=hospitals.data)

@app.route("/admin/create-worker", methods=["POST"])
def create_worker():
    if "worker_id" not in session or session["role"] != "admin":
        return redirect("/dashboard")

    supabase.table("healthcare_worker").insert({
        "hospital_id": request.form["hospital_id"],
        "username": request.form["username"],
        "password_hash": request.form["password"],
        "role": request.form["role"]
    }).execute()

    return redirect("/admin")

@app.route("/admin/deactivate/<worker_id>")
def deactivate_worker(worker_id):
    if "worker_id" not in session or session["role"] != "admin":
        return redirect("/dashboard")

    supabase.table("healthcare_worker").delete().eq("worker_id", worker_id).execute()
    return redirect("/admin")

@app.route("/audit-log")
def audit_log():
    if "worker_id" not in session:
        return redirect("/login")
    if session["role"] != "admin":
        return redirect("/dashboard")

    logs = supabase.table("audit_log").select("*, healthcare_worker(username)").order("timestamp", desc=True).execute()
    return render_template("audit_log.html", logs=logs.data)

if __name__ == "__main__":
    app.run(debug=True)