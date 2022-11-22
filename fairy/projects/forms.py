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
    delivery_address = StringField(label='Адрес для доставки', validators=[Length(max=1000)])
    contact_person = StringField(label='Контактное лицо для службы доставки', validators=[Length(max=60)])
    phone = StringField(label='Телефон',
                        validators=[DataRequired(),
                                    Length(min=11, max=11),
                                    Regexp(regex='^[0-9]+$',
                                           message='Ошибка ввода номера телефона! Введите номер телефона в формате '
                                                   '89001112233')])
    pickup_point_address_1 = StringField(label='Адрес пункта самовывоза Ozon', validators=[Length(max=1000)])
    pickup_point_address_2 = StringField(label='Адрес пункта самовывоза Wildberries', validators=[Length(max=1000)])
