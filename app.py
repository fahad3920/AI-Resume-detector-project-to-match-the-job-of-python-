from flask import Flask, request, render_template, redirect, url_for, session, flash
from resume_parser import parse_resume_text
from job_scraper import scrape_jobs
from matcher import match_jobs
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Database init (SQLite)
def init_db():
    with sqlite3.connect("jobs.db") as conn:
        c = conn.cursor()
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
        # Create jobs table
        c.execute('''CREATE TABLE IF NOT EXISTS jobs
                     (id INTEGER PRIMARY KEY, title TEXT, company TEXT, location TEXT, description TEXT, url TEXT)''')
        # Create bookmarks table
        c.execute('''CREATE TABLE IF NOT EXISTS bookmarks
                     (user_id INTEGER, job_id INTEGER,
                      PRIMARY KEY (user_id, job_id),
                      FOREIGN KEY (user_id) REFERENCES users(id),
                      FOREIGN KEY (job_id) REFERENCES jobs(id))''')
        conn.commit()
init_db()

# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Please provide both username and password.")
            return redirect(url_for("register"))
        password_hash = generate_password_hash(password)
        try:
            with sqlite3.connect("jobs.db") as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
                conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
            return redirect(url_for("register"))
    return render_template("register.html")

# User login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with sqlite3.connect("jobs.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            if user and check_password_hash(user[1], password):
                session["user_id"] = user[0]
                session["username"] = username
                flash("Logged in successfully.")
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password.")
                return redirect(url_for("login"))
    return render_template("login.html")

# User logout route
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        # Redirect to login if not authenticated
        return redirect(url_for("login"))

    if request.method == "POST":
        resume_file = request.files.get("resume")
        if not resume_file:
            return "No resume uploaded", 400

        # Extract text from PDF
        from PyPDF2 import PdfReader
        pdf_reader = PdfReader(resume_file)
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"

        # Parse resume
        resume_data = parse_resume_text(full_text)
        print("DEBUG: Extracted resume text:", resume_data.get("full_text", "")[:500])

        # Scrape jobs (example: scraping Indeed for "software engineer")
        jobs = scrape_jobs("software engineer", location="Remote")
        print(f"DEBUG: Number of jobs scraped: {len(jobs)}")
        for i, job in enumerate(jobs[:3]):
            print(f"DEBUG: Job {i+1} description snippet: {job['description'][:200]}")

        # Remove duplicate jobs by URL
        seen_urls = set()
        unique_jobs = []
        for job in jobs:
            if job["url"] not in seen_urls:
                unique_jobs.append(job)
                seen_urls.add(job["url"])
        jobs = unique_jobs

        # Store jobs in DB (replace old ones)
        with sqlite3.connect("jobs.db") as conn:
            c = conn.cursor()
            c.execute("DELETE FROM jobs")
            for job in jobs:
                c.execute("INSERT INTO jobs (title, company, location, description, url) VALUES (?, ?, ?, ?, ?)",
                          (job["title"], job["company"], job["location"], job["description"], job["url"]))
            conn.commit()

        # Validate resume text and job descriptions before matching
        if not resume_data.get("full_text") or not any(job.get("description") for job in jobs):
            print("DEBUG: Empty resume text or job descriptions detected, skipping matching.")
            matched_jobs = []
        else:
            # Match jobs
            matched_jobs = match_jobs(resume_data, jobs)

        # If user logged in, get bookmarked job ids
        bookmarked_job_ids = set()
        if "user_id" in session:
            with sqlite3.connect("jobs.db") as conn:
                c = conn.cursor()
                c.execute("SELECT job_id FROM bookmarks WHERE user_id = ?", (session["user_id"],))
                bookmarked_job_ids = set(row[0] for row in c.fetchall())

        # Render results
        return render_template("index.html", jobs=matched_jobs, resume=resume_data, uploaded=True, bookmarked_job_ids=bookmarked_job_ids)

    # GET request
    return render_template("index.html", uploaded=False)
    
# Route to toggle bookmark for a job (AJAX)
@app.route("/bookmark/<int:job_id>", methods=["POST"])
def bookmark(job_id):
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401
    user_id = session["user_id"]
    with sqlite3.connect("jobs.db") as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM bookmarks WHERE user_id = ? AND job_id = ?", (user_id, job_id))
        exists = c.fetchone()
        if exists:
            c.execute("DELETE FROM bookmarks WHERE user_id = ? AND job_id = ?", (user_id, job_id))
            conn.commit()
            return {"status": "removed"}
        else:
            c.execute("INSERT INTO bookmarks (user_id, job_id) VALUES (?, ?)", (user_id, job_id))
            conn.commit()
            return {"status": "added"}

if __name__ == "__main__":
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    threading.Timer(1.5, open_browser).start()

    app.run(debug=True)
