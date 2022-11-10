# fairy/users/forms.py
import datetime
from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, Regexp
from fairy.models import Santa


# форма регистрации
class RegisterForm(FlaskForm):
    email_address = StringField(label='Email:', validators=[Email(), DataRequired(), Length(max=60)])
    first_name = StringField(label='Имя:', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField(label='Фамилия:', validators=[DataRequired(), Length(min=2, max=30)])
    phone = StringField(label='Телефон', validators={DataRequired(),
                                                     Length(min=11, max=11),
                                                     Regexp(regex='^[0-9]+$',
                                                            message='Ошибка ввода номера телефона! Введите номер телефона в формате '
                                                                    '89001112233')})
    password1 = PasswordField(label='Пароль:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Подтвердите пароль:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Зарегистрироваться')
    recaptcha = RecaptchaField()

    # проверка на наличие в базе адреса почты
    def validate_email_address(self, email_address_to_check):
        current_time = int(round(datetime.now().timestamp()))
        email_address = Santa.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            registration_time = int(round(email_address.registered_on.timestamp()))
            registration_confirm_time_dif = current_time - registration_time
            if registration_confirm_time_dif < 86400:
                raise ValidationError('Вы уже зарегистрированы, но пока не подтвердили вашу учетную запись. '
                                      'Проверьте ваш почтовый ящик (загляните в папку Спам), там должна быть ссылка '
                                      'для активации вашей учетной записи.'
                                      'Ссылка действительна 1 час.')


# форма редактирования профиля пользователя
# не даем менять электронную почту, потому что она является логином
class ProfileUpdateForm(FlaskForm):
    email_address = StringField(label='Email:',
                                validators=[Email(message='Не правильный формат электронной почты'),
                                            DataRequired(message='Поле электронная почта не может быть пустым'),
                                            Length(max=60,
                                                   message='Максимальная длина почты 60 символов')])
    first_name = StringField(label='Имя:',
                             validators=[DataRequired(message='Поле имя не может быть пустым'),
                                         Length(min=2,
                                                message='Допустимая длина имени от 2 до 30 символов')])
    last_name = StringField(label='Фамилия:',
                            validators=[DataRequired(message='Поле фамилия не может быть пустым'),
                                        Length(min=2, max=30, message='Допустимая длина имени от 2 до 30 символов')])
    phone = StringField(label='Телефон',
                        validators={DataRequired(message='Поле телефона не может быть пустым'),
                                    Length(min=11, max=11, message='Введите мобильный номер в формате 89001112233'),
                                    Regexp(regex='^[0-9]+$',
                                           message='Ошибка ввода номера телефона! Введите номер телефона в формате '
                                                                    '89001112233')})
    submit = SubmitField(label='Сохранить')

    # проверка на наличие в базе адреса почты
    def validate_email_address(self, email_address):
        if email_address.data != current_user.email_address:
            email = Santa.query.filter_by(email_address=email_address.data).first()
            if email:
                raise ValidationError('Данный адрес электронной почты уже используется, попробуйте '
                                      'ввести другой адрес.')

    # проверка на наличие в базе телефона
    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            phone = Santa.query.filter_by(phone=phone.data).first()
            if phone:
                raise ValidationError('Данный номер телефона уже используется, попробуйте '
                                      'ввести другой номер.')


# форма авторизации
class LoginForm(FlaskForm):
    email_address = StringField(label='Email:', validators=[DataRequired()])
    password = PasswordField(label='Пароль:', validators=[DataRequired()])
    submit = SubmitField(label='Войти')
    recaptcha = RecaptchaField()


# форма запрос сброса пароля
class RequestResetPasswordForm(FlaskForm):
    email_address = StringField(label='Email:',
                                validators=[Email(message='Ошибка ввода Email. Введите email в формате aaa@example.'
                                                          'com'),
                                            DataRequired(message='Поле не может быть пустым.'),
                                            Length(max=60, message='Максимальная длина адреса почты 60 символов.')])
    submit = SubmitField(label='Сбросить пароль')
    recaptcha = RecaptchaField()

    def validate_email(self, email_address):
        user = Santa.query.filter_by(email_address=email_address.data).first()
        if user is None:
            raise ValidationError('Учетная запись с таким ящиком электронной почты не найдена или вы ввели не '
                                  'корректный адрес электронной почты.')

# форма ввода нового пароля, после сброса
class ResetPasswordForm(FlaskForm):
    password1 = PasswordField(label='Пароль:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Подтвердите пароль:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Сохранить новый пароль')
    recaptcha = RecaptchaField()
