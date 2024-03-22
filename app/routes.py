from flask import (
    Blueprint, render_template, request, jsonify, url_for, redirect, session, flash
)
from werkzeug.security import check_password_hash
import pandas as pd
import json
import plotly
import plotly.express as px

from .models import Participant, Question, Answer, Admin
from .database import db

main = Blueprint("main", __name__)
admin = Blueprint("admin", __name__, url_prefix="/admin")


@main.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@main.route("/participants", methods=["POST"])
def add_participant():
    data = request.get_json()
    new_participant = Participant(name=data['name'], age=data['age'], gender=data['gender'])
    db.session.add(new_participant)
    db.session.commit()
    participant_data = {
        "participant_id": new_participant.id,
        "redirect": url_for("main.question")
    }
    return jsonify(participant_data)


@main.route("/question", methods=["GET"])
def question():
    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return redirect(url_for("main.home"))
    return render_template("question.html")


@main.route("/questions", methods=["GET"])
def get_questions():
    questions = Question.query.order_by(Question.id).all()
    question_list = [
        {
            "id": question.id,
            "content": question.content
        }
        for question in questions
    ]
    return jsonify(questions=question_list)


@main.route("/submit", methods=["POST"])
def submit():
    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return redirect(url_for("main.question"))
    data = request.get_json()
    for answer in data['quizzes']:
        answer_data = Answer(
            chosen_answer=answer['chosen_answer'],
            participant_id=participant_id,
            question_id=answer['question_id']
        )
        db.session.add(answer_data)
    db.session.commit()
    return jsonify({"msg": "Successfully Created Answer"})


@main.route("/results", methods=["GET"])
def show_results():
    participants = Participant.query.all()
    participants_data = [
        {
            "age": participant.age,
            "gender": participant.gender
        } for participant in participants
    ]

    answers = Answer.query.all()
    answers_data = [
        {
            "question_id": answer.question_id,
            "chosen_answer": answer.chosen_answer
            # "age": answer.participant.age,
            # "gender": answer.participant.gender
        } for answer in answers
    ]

    participant_df = pd.DataFrame(participants_data)
    answer_df = pd.DataFrame(answers_data)

    fig_age = px.pie(participant_df, names="age", title="참가자 나이 분포도")
    fig_gender = px.pie(participant_df, names="gender", title="참가자 성별 분포도")

    question_answer_figs = {}

    for question_id in answer_df['question_id'].unique():
        filter_question_df = answer_df[answer_df['question_id'] == question_id]
        fig = px.histogram(
            filter_question_df,
            x="chosen_answer",
            color="chosen_answer",
            title=f"Question {question_id} Responses",
            barmode="group"
        )
        fig.update_layout(
            xaxis_title="Chosen Answer",
            yaxis_title="Count",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
            title_font=dict(
                family="Helvetica, Arial, sans-serif", size=22, color="RebeccaPurple"
            ),
        )
        fig.update_traces(marker_line_width=1.5, opacity=0.6)
        question_answer_figs[f"question_{question_id}"] = fig

    graphs_json = json.dumps(
        {
            "age_distribution": fig_age,
            "gender_distribution": fig_gender,
            "quiz_responses": question_answer_figs
            # "age_quiz_response_figs": ""
        },
        cls=plotly.utils.PlotlyJSONEncoder
    )
    return render_template("results.html", graphs_json=graphs_json)

@admin.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session["admin_logined"] = True
            return render_template("dashboard.html")
        return flash("아이디 비밀번호가 맞지 않습니다.")
    return render_template("admin.html")


@admin.route("/logout", methods=["GET"])
def logout():
    session.pop("admin_logined", None)
    return redirect(url_for("main.home"))


from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logined" not in session:
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated_function


@admin.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    pass


@admin.route("/dashboard/questions", methods=["GET", "POST"])
@login_required
def manage_questions():
    pass


@admin.route("/dashboard/question-list", methods=["GET"])
@login_required
def question_list():
    pass