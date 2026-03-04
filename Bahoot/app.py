from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "SECRET123"


# ---------- DB Helpers ----------
def get_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (quiz_id) REFERENCES quiz(quiz_id)
    )
    """)


    c.execute("""
    CREATE TABLE IF NOT EXISTS quiz (
        quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        picture TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer_options TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        UNIQUE(quiz_id, question),
        FOREIGN KEY (quiz_id) REFERENCES quiz(quiz_id)
    )
    """)

    conn.commit()
    conn.close()


def seed_quizzes():
    conn = get_db()
    c = conn.cursor()

    quizzes = [
        ("English", "English language quiz", ""),
        ("Maths", "Simple maths quiz", ""),
        ("French", "Basic French quiz", "")
    ]

    c.executemany("""
        INSERT OR IGNORE INTO quiz (subject, description, picture)
        VALUES (?, ?, ?)
    """, quizzes)

    conn.commit()
    conn.close()


def seed_questions():
    conn = get_db()
    c = conn.cursor()

    count = c.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    if count == 0:
        questions = [
            (1, "What is the capital of France?", "Paris|London|Rome|Berlin", "Paris"),
            (1, "What is the capital of England?", "London|Paris|Rome|Madrid", "London"),
            (2, "What is 5 + 5?", "8|9|10|11", "10"),
            (2, "What is 12 - 7?", "3|4|5|6", "5"),
            (3, "What does 'Bonjour' mean?", "Hello|Goodbye|Please|Thanks", "Hello"),
        ]

        c.executemany("""
        INSERT INTO questions
        (quiz_id, question, answer_options, correct_answer)
        VALUES (?, ?, ?, ?)
        """, questions)

    conn.commit()
    conn.close()

# ---------- Routes ----------
@app.route("/")
def index():
    conn = get_db()
    quizzes = conn.execute(
        "SELECT quiz_id, subject, description FROM quiz"
    ).fetchall()
    conn.close()
    return render_template("index.html", quizzes=quizzes)


@app.route("/quiz/<int:id>")
def start_quiz(id):
    session["quiz_id"] = id
    session["question_index"] = 0
    session["score"] = 0
    return redirect(url_for("quiz"))


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    quiz_id = session.get("quiz_id")

    conn = get_db()
    questions = conn.execute(
        "SELECT * FROM questions WHERE quiz_id = ?",
        (quiz_id,)
    ).fetchall()
    conn.close()

    index = session.get("question_index", 0)

    if index >= len(questions):
        return render_template(
            "quiz_complete.html",
            score=session["score"],
            total=len(questions)
        )

    question = questions[index]
    options = question["answer_options"].split("|")

    if request.method == "POST":
        selected = request.form.get("selected_answer")

        if selected == question["correct_answer"]:
            session["score"] += 1

        session["question_index"] += 1
        return redirect(url_for("quiz"))

    return render_template(
        "questionpage.html",
        question=question,
        options=options
    )


if __name__ == "__main__":
    init_db()
    seed_quizzes()
    seed_questions()
    app.run(debug=True)