# fairy/kids/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, \
    TextAreaField, IntegerField, FileField, SelectField, HiddenField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, Regexp


# форма ребенка
class KidForm(FlaskForm):
    name = StringField(label='Имя Ф.', validators=[DataRequired(message='Поле ИМЯ'), Length(max=100)])
    birthday = DateField(label='Дата рождения', validators=[DataRequired(message='Поле Дата Рождения')])
    house_id = IntegerField(label='Учреждение', validators=[DataRequired(message='Поле Учреждение')])
    submit = SubmitField(label='Сохранить')
