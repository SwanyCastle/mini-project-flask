from flask import (
    Blueprint, render_template, request, jsonify, url_for, redirect
)
from .models import Participant, Question, Answer
from .database import db

main = Blueprint("main", __name__)


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


@main.route("/question")
def question():
    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return redirect(url_for("main.home"))
    return render_template("question.html")


@main.route("/questions")
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


@main.route("/results")
def show_results():
    pass
