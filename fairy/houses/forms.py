from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Email, DataRequired, Regexp


# форма учреждения
class HouseForm(FlaskForm):
    short_name = StringField(label='Название', validators=[DataRequired(), Length(max=50)])
    full_name = StringField(label='Полное название', validators=[DataRequired(), Length(max=200)])
    address = StringField(label='Адрес', validators=[DataRequired(), Length(max=1000)])
    phone = StringField(label='Телефон',
                        validators=[DataRequired(),
                                    Length(min=11, max=11),
                                    Regexp(regex='^[0-9]+$',
                                           message='Ошибка ввода номера телефона! Введите номер телефона в формате '
                                                   '89001112233')])
    email_address = StringField(label='Email:',
                                validators=[Email(message='Ошибка ввода Email. Введите email в формате aaa@example.'
                                                          'com'),
                                            DataRequired(),
                                            Length(max=60)])
    contact_person = StringField(label='Контактное лицо:', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField(label='Сохранить')
