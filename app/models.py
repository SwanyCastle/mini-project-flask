from .database import db
from datetime import datetime
from pytz import timezone


class Participant(db.Model):
    __tablename__ = "participants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Seoul')))


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))
    order_num = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    chosen_answer = db.Column(db.String(255))
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))

    participant = db.relationship("Participant", backref="answers")
    question = db.relationship("Question", backref="answers")


class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
