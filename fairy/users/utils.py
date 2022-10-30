import datetime
from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from fairy import app, db, Thread, send_async_email
from fairy.users.forms import RequestResetPasswordForm
from fairy.models import Santa

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
utils_bp = Blueprint('utils_bp', __name__)


# Account Registered route
@utils_bp.route('/registered')
def registered():
    return render_template('registered.html')


# Request Password Reset route
@utils_bp.route('/request_reset_password', methods=['GET', 'POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('users_bp.welcome_page'))

    request_password_reset_form = RequestResetPasswordForm()
    if request_password_reset_form.validate_on_submit():
        user = Santa.query.filter_by(email_address=request_password_reset_form.email_address.data).first()
        if user:
            send_reset_email(user)
            flash(f'Инструкция по сбросу пароля отправлена вам на почту. Проверьте почтовый ящик.', category='success')
            return redirect(url_for('users_bp.login_page'))
        else:
            flash(f'Адрес почты {request_password_reset_form.email_address.data} не найден в базе.',
                  category='danger')
    return render_template('request_password_reset.html', request_password_reset_form=request_password_reset_form)


# Email Confirmation route
@utils_bp.route('/email_confirmation/<token>')
def email_confirmation(token, expire_time=86400):
    try:
        email = s.loads(token, salt=app.config['SECRET_KEY'], max_age=expire_time)
        user_to_confirm = Santa.query.filter_by(email_address=email).first()
        user_to_confirm.confirmed = True
        user_to_confirm.confirmed_on = datetime.datetime.now()
        db.session.commit()

    except SignatureExpired:
        return '<h1>Прошло больше 1 часа с момента вашей регистрации, ссылка уже не действительна. </h1>'

    return render_template('email_confirmation.html')



# функция отправки письма для сброса пароля
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject=app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' - запрос на сброс пароля.',
                  sender='santa@teteruk.com',
                  recipients=[user.email_address])
    msg.body = f'''Для сброса вашего пароля на платформе Фея перейдите по следующей ссылке:
{url_for('users_bp.reset_password_with_token', token=token, _external=True)}
Если вы не запрашивали сброс пароля или сделали это по ошибке, то просто проигнорируйте это письмо.
'''
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
