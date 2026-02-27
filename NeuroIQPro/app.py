from flask import Flask, render_template, request, redirect, url_for, session
import random
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "neuroiq_secret_key"

LEADERBOARD_FILE = "leaderboard.json"

# -------------------------
# Utility Functions
# -------------------------

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as f:
        return json.load(f)

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_question(difficulty):
    if difficulty == "easy":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        return {
            "question": f"What is {a} + {b} ?",
            "options": [a+b, a+b+1, a+b-1, a+b+2],
            "answer": a+b,
            "category": "Logical"
        }

    if difficulty == "medium":
        a = random.randint(10, 50)
        b = random.randint(1, 10)
        return {
            "question": f"If a train travels {a} km in {b} hours, what is its speed?",
            "options": [a//b, a//b+2, a//b-1, a//b+5],
            "answer": a//b,
            "category": "Analytical"
        }

    if difficulty == "hard":
        series_start = random.randint(2, 5)
        series = [series_start * i for i in range(1, 5)]
        next_val = series_start * 5
        options = [next_val, next_val+2, next_val-1, next_val+3]
        random.shuffle(options)

        return {
            "question": f"Find next number: {series}",
            "options": options,
            "answer": next_val,
            "category": "Pattern"
        }

# -------------------------
# Routes
# -------------------------

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/start", methods=["POST"])
def start():
    name = request.form.get("name")
    difficulty = request.form.get("difficulty")

    session["name"] = name
    session["difficulty"] = difficulty
    session["score"] = 0
    session["question_count"] = 0
    session["questions"] = []

    return redirect(url_for("test"))

@app.route("/test", methods=["GET", "POST"])
def test():
    if "name" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        selected = request.form.get("answer")
        correct = session["current_answer"]

        if selected and int(selected) == correct:
            session["score"] += 1

        session["question_count"] += 1

    if session["question_count"] >= 5:
        return redirect(url_for("result"))

    question_data = generate_question(session["difficulty"])

    session["current_answer"] = question_data["answer"]

    return render_template(
        "test.html",
        question=question_data["question"],
        options=question_data["options"],
        q_number=session["question_count"] + 1
    )

@app.route("/result")
def result():
    if "name" not in session:
        return redirect(url_for("login"))

    score = session["score"]
    iq_score = 80 + (score * 8)

    suggestions = []
    if score <= 2:
        suggestions.append("Practice basic logic puzzles daily.")
    if score == 3:
        suggestions.append("Try medium-level reasoning challenges.")
    if score >= 4:
        suggestions.append("Attempt advanced IQ mock tests.")

    leaderboard = load_leaderboard()
    leaderboard.append({
        "name": session["name"],
        "score": score,
        "iq": iq_score,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
    })

    leaderboard = sorted(leaderboard, key=lambda x: x["iq"], reverse=True)
    save_leaderboard(leaderboard)

    return render_template(
        "result.html",
        name=session["name"],
        score=score,
        iq=iq_score,
        suggestions=suggestions
    )

@app.route("/leaderboard")
def leaderboard():
    data = load_leaderboard()
    return render_template("leaderboard.html", leaderboard=data)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/reset")
def reset():
    save_leaderboard([])
    return redirect(url_for("leaderboard"))

if __name__ == "__main__":
    app.run()

