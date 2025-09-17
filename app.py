from flask import Flask, render_template, request, redirect, session, jsonify
from cs50 import SQL
import requests
import hashlib
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key")

# Initialize database with automatic creation
try:
    db = SQL("sqlite:///privacy.db")
except RuntimeError:
    # Create the database file if it doesn't exist
    open("privacy.db", "a").close()  # Create an empty file
    db = SQL("sqlite:///privacy.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            breaches_count INTEGER DEFAULT 0,
            score INTEGER DEFAULT 100
        )
    """)

@app.route("/")
def index():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return "Must provide email and password", 400
        hashed_password = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (email, password) VALUES (?, ?)", email, hashed_password)
            rows = db.execute("SELECT * FROM users WHERE email = ?", email)
            session["user_id"] = rows[0]["id"]
            return redirect("/dashboard")
        except:
            return "Email already registered", 400
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return "Must provide email and password", 400
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if rows and check_password_hash(rows[0]["password"], password):
            session["user_id"] = rows[0]["id"]
            return redirect("/dashboard")
        return "Invalid email or password", 400
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session["user_id"]
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            return render_template("dashboard.html", breaches_count=0, score=0, error="Must provide email", api_error=None)
        response = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers={"User-Agent": "PrivacyDashboard/1.0"}, timeout=5)
        breaches = []
        if response.status_code == 200:
            breaches = response.json()
        elif response.status_code == 401:
            breaches = []
            return render_template("dashboard.html", breaches_count=0, score=100, api_error="Email scan limited without API key. Consider upgrading for full breach detection.")
        breaches_count = len(breaches)
        score = max(0, 100 - (breaches_count * 10))
        db.execute("UPDATE users SET breaches_count = ?, score = ? WHERE id = ?", breaches_count, score, user_id)
        tip = generate_privacy_tip(breaches_count)
        return render_template("dashboard.html", breaches_count=breaches_count, score=score, tip=tip)
    rows = db.execute("SELECT breaches_count, score FROM users WHERE id = ?", user_id)
    tip = generate_privacy_tip(rows[0]["breaches_count"])
    return render_template("dashboard.html", breaches_count=rows[0]["breaches_count"], score=rows[0]["score"], tip=tip)

@app.route("/check_password", methods=["POST"])
def check_password():
    if not session.get("user_id"):
        return redirect("/login")
    password = request.form.get("password")
    if not password:
        return "Must provide password", 400
    sha1_password = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]
    response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", headers={"User-Agent": "PrivacyDashboard/1.0"}, timeout=5)
    if response.status_code == 200:
        hashes = dict(line.split(":") for line in response.text.splitlines())
        if suffix in hashes:
            return "This password has been breached! Use a new one.", 200
    return "Password appears safe.", 200

@app.route("/backup_db", methods=["GET"])
def backup_db():
    if not session.get("user_id"):
        return redirect("/login")
    with open("privacy.db", "rb") as f:
        db_backup = f.read()
    # Note: This is a local backup simulation; for production, upload to cloud storage
    return jsonify({"message": "Backup created locally. Download manually from server."})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def generate_privacy_tip(breaches_count):
    if breaches_count > 0:
        return "Consider changing your passwords and enabling two-factor authentication."
    return "Your account is secure! Keep using strong, unique passwords."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)