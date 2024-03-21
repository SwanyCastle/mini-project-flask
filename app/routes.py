from flask import (
    Blueprint, render_template, request, jsonify, url_for
)
from .models import Participant
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
    return render_template("question.html")


@main.route("/submit", methods=["POST"])
def submit():
    pass

@main.route("/questions")
def get_questions():
    pass


@main.route("/results")
def show_results():
    pass