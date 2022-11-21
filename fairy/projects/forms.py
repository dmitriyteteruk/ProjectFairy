# fairy/projects/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField
from wtforms.validators import Length, DataRequired


# форма проекта
class ProjectForm(FlaskForm):
    name = StringField(label='Название проекта', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField(label='Описание проекта', validators=[DataRequired(), Length(max=10000)])
    delivery_date = DateField(label='Крайний срок сбора подарков на СВХ')
    visit_date = DateField(label='Дата поездки')
    submit = SubmitField(label='Сохранить')
