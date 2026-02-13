from flask import Flask, render_template, request, redirect, session, abort, url_for
import sqlite3
from datetime import datetime
import os
import secrets
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
app = Flask(__name__)
app.secret_key = "SECRET123"  # Change in production


# ---------- DB Helpers ----------
def get_db():
    db = app.config.get("DATABASE", "database.db")
    conn = sqlite3.connect(db, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,       -- we'll store email here
        password TEXT NOT NULL            -- hashed password
        
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS quiz (
        quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        picture TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS c (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    


def seed_quizes():
    conn = get_db()
    c = conn.cursor()

    quizzes = [
        {
            "subject": "English",
            "description": "Quizzes testing your understanding of the English Language and literature",
            "picture": "",
        },
        {
            "subject": "Maths",
            "description": "Quizzes testing your understanding of the Maths simple sums",
            "picture": "",
        },
        {
            "subject": "French",
            "description": "Quizzes testing your understanding of the French Language. Bonjour!",
            "picture": "",
        }
    ]

    for p in quizzes:
        c.execute("""
            INSERT OR IGNORE INTO quiz (subject, description, picture)
            VALUES (?, ?, ?)
        """, (p["subject"], p["description"], p["picture"]))

    conn.commit()
    conn.close()

# ---------- Routes ----------
@app.route("/")
def index():
    conn = get_db()
    rows = conn.execute("SELECT subject, picture, description FROM quiz ORDER BY subject").fetchall()
    conn.close()
    return render_template("index.html", quizzes=rows)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    # pretend this came from a DB
    questions = [
        {"question": "What is capital of France", "answer": "Paris"},
        {"question": "What is capital of England", "answer": "London"}
    ]

    feedback = None

    if request.method == "POST":
        user_question = request.form.get("question")
        user_answer = request.form.get("answer")

        # find correct answer
        correct_answer = None
        for q in questions:
            if q["question"] == user_question:
                correct_answer = q["answer"]
                break

        # compare
        if user_answer == correct_answer:
            feedback = "✅ Correct!"
        else:
            feedback = f"❌ Incorrect — the correct answer was {correct_answer}"

    return render_template(
        "questionpage.html",
        questions=questions,
        feedback=feedback
    )


@app.route("/login")
def login():
    return ""

@app.route("/register")
def register():
    return ""

if __name__ == "__main__":
    init_db()
    seed_quizes()
    app.run(debug=True)
