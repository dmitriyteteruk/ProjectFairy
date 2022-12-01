# fairy/gifts/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, SelectField, HiddenField
from wtforms.validators import Length, DataRequired


# форма подарка
class GiftForm(FlaskForm):
    name = StringField(label='Название', validators=[DataRequired(message='name'), Length(max=100)])
    description = TextAreaField(label='Подробное описание', validators=[Length(max=1000)])
    postcard_url = HiddenField(label='Ссылка на файл открытки')
    house = SelectField(label='Выберите учреждение', choices=[], coerce=int, validate_choice=False)
    kid = SelectField(label='Выберите ребенка', choices=[], coerce=int, validate_choice=False)
    project_id = SelectField(label='Выберите проект', choices=[], coerce=int, validate_choice=False)
    postcard_file = FileField(label='Файл открытки')
    submit = SubmitField(label='Сохранить')


# форма снятия открытки/шарика с елки
class PickGift(FlaskForm):
    submit = SubmitField(label='Подарить!')


# форма изменения статуса подарка
class GiftStatusUpdateForm(FlaskForm):
    submit = SubmitField(label='Сохранить')
