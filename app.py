from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            firstname TEXT,
            lastname TEXT,
            email TEXT,
            address TEXT
        )
    """)
    conn.commit()
    conn.close()

def user_file_path(username):
    return os.path.join(UPLOAD_FOLDER, f"{username}.txt")

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        address = request.form["address"]


        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            (username, password, firstname, lastname, email, address)
        )
        conn.commit()
        conn.close()
        return redirect(f"/profile/{username}")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect(f"/profile/{username}")
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/profile/<username>")
def profile(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user is None:
        return "User not found"

    word_count = None
    path = user_file_path(username)
    if os.path.exists(path):
        with open(path, "r") as f:
            word_count = len(f.read().split())

    return render_template("profile.html", user=user, word_count=word_count)

@app.route("/upload/<username>", methods=["POST"])
def upload(username):
    file = request.files["file"]
    if file and file.filename:
        file.save(user_file_path(username))
    return redirect(f"/profile/{username}")

@app.route("/download/<username>")
def download(username):
    path = user_file_path(username)
    if not os.path.exists(path):
        return "No file uploaded"
    return send_file(path, as_attachment=True, download_name="Limerick.txt")


init_db()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)