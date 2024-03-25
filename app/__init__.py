from flask import Flask
from flask_migrate import Migrate
from flask.cli import with_appcontext
import os, click
from .database import db
from .models import Question, Admin, Participant
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = "oz_kwak_coding"

    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    dbfile = os.path.join(basedir, "db.sqlite")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + dbfile
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import main as main_blp, admin as admin_blp

    app.register_blueprint(main_blp)
    app.register_blueprint(admin_blp)

    def add_initial_questions():
        initial_questions = [
            "오즈코딩스쿨에 대해서 알고 계신가요?",
            "프론트엔드 과정에 참여하고 계신가요?",
            "전공자 이신가요?",
            "프로젝트를 진행해보신적 있으신가요?",
            "개발자로 일한 경력이 있으신가요?",
        ]
        yesterday = datetime.utcnow() - timedelta(days=1)  # 어제 날짜 계산

        # 관리자 계정 추가 로직, 비밀번호 해시 처리 적용
        existing_admin = Admin.query.filter_by(username="admin").first()
        if not existing_admin:
            hashed_password = generate_password_hash("0000")  # 비밀번호를 해시 처리
            new_admin = Admin(username="admin", password=hashed_password)
            db.session.add(new_admin)

        participants_without_created_at = Participant.query.filter(
            Participant.created_at == None
        ).all()

        for participant in participants_without_created_at:
            participant.created_at = yesterday

        for question_content in initial_questions:
            existing_question = Question.query.filter_by(
                content=question_content
            ).first()
            if not existing_question:
                new_question = Question(content=question_content)
                db.session.add(new_question)
        questions = Question.query.all()
        for question in questions:
            question.order_num = question.id
            question.is_active = True  # 모든 질문을 활성화 상태로 설정
        db.session.commit()

    @click.command("init-db")
    @with_appcontext
    def init_db_command():
        db.create_all()
        add_initial_questions()
        click.echo("Initialized the database.")

    app.cli.add_command(init_db_command)

    return app
