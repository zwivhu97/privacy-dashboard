from flask import Flask, render_template, request, redirect, session
from cs50 import SQL
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Replace with a random string (e.g., secrets.token_hex(16))

# Initialize database (creates privacy.db if it doesn't exist)
db = SQL("sqlite:///privacy.db")

# Create users table if it doesn't exist
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        breaches_count INTEGER DEFAULT 0,
        score INTEGER DEFAULT 100
    )
""")

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/login")
    return redirect("/dashboard")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            return "Must provide email", 400
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if not rows:
            db.execute("INSERT INTO users (email) VALUES (?)", email)
            rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        session["user_id"] = rows[0]["id"]
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session["user_id"]
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            return "Must provide email", 400
        response = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers={"User-Agent": "PrivacyDashboard/1.0"})
        breaches = response.json() if response.status_code == 200 else []
        breaches_count = len(breaches)
        score = max(0, 100 - (breaches_count * 10))
        db.execute("UPDATE users SET breaches_count = ?, score = ? WHERE id = ?", breaches_count, score, user_id)
        return redirect("/dashboard")
    rows = db.execute("SELECT breaches_count, score FROM users WHERE id = ?", user_id)
    return render_template("dashboard.html", breaches_count=rows[0]["breaches_count"], score=rows[0]["score"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)