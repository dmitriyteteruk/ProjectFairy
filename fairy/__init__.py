import datetime
from datetime import date
from threading import Thread

from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from fairy.config import Config


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "users_bp.login_page"
login_manager.login_message_category = "info"
mail = Mail(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Калькулятор возраста ребенка - Текущий год - Год даты рождения
def age_calculator(birthday):
    today = int(date.today().strftime("%Y"))
    birth_year = int(datetime.datetime.strftime(birthday, "%Y"))
    age = today - birth_year
    return age


# добавление Калькулятора возраста ребенка в глобальные переменные Jinja
app.jinja_env.globals.update(
    age_calculator=age_calculator,
)


# Асинхронная отправка писем, чтобы не тупил браузер
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ': ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_confirmation_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ': ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

from fairy.gifts.routes import gifts_bp
from fairy.houses.routes import houses_bp
from fairy.kids.routes import kids_bp
from fairy.main.routes import main_bp
from fairy.projects.routes import projects_bp
from fairy.users.routes import users_bp
from fairy.users.utils import utils_bp
from fairy.errors.handlers import errors_bp

app.register_blueprint(gifts_bp)
app.register_blueprint(houses_bp)
app.register_blueprint(kids_bp)
app.register_blueprint(main_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(users_bp)
app.register_blueprint(utils_bp)
app.register_blueprint(errors_bp)




