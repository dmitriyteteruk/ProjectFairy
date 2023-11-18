import datetime
import bcrypt

from flask import render_template, redirect, url_for, flash, request, Blueprint, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import func, distinct

from fairy import app, db, send_email
from fairy.users.forms import RegisterForm, LoginForm, ProfileUpdateForm, RequestResetPasswordForm, \
    ResetPasswordForm
from fairy.gifts.forms import GiftStatusUpdateForm
from fairy.models import Gift, Santa, Project, House

users_bp = Blueprint('users_bp', __name__)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# USER Registration route
@users_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    request_password_reset_form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = Santa.query.filter_by(email_address=form.email_address.data).first()

        # если запись есть, но она не подтверждена, меняем дату регистрации на сейчас.
        if user and not user.confirmed:
            user.registered_on = datetime.datetime.now()
            db.session.commit()

            # Токен и адрес для подтверждения email
            token = s.dumps(user.email_address, salt=app.config['SECRET_KEY'])
            link = url_for('utils_bp.email_confirmation', token=token, _external=True)

            # вывод сообщения пользователю
            flash('На ваш почтовый ящик отправлена новая ссылка для активации учетной записи. Срок действия ссылки 1 '
                  'час.')

            # отправка пользователю подтверждения на email
            send_email(user.email_address, 'Подтвердите адрес электронной почты', 'mail/confirm',
                       link=link, user=user)

        # если запись есть и подтверждена, то переводим пользователя на страницу авторизации.
        if user and user.confirmed:
            flash(f'Данный адрес почты уже занят. Если вы забыли свой пароль, то воспользуйтесь функцией сброса '
                  'пароля.', category='info')
            return render_template('request_password_reset.html', request_password_reset_form=request_password_reset_form)

        # если запись новая, то создаем запись в БД.
        else:
            user = Santa(email_address=form.email_address.data,
                         password=form.password1.data,
                         first_name=form.first_name.data,
                         last_name=form.last_name.data,
                         phone=form.phone.data,
                         role="user",
                         confirmed=False,
                         registered_on=datetime.datetime.now())
            db.session.add(user)
            db.session.commit()

            # Токен и адрес для подтверждения email
            token = s.dumps(user.email_address, salt=app.config['SECRET_KEY'])
            link = url_for('utils_bp.email_confirmation', token=token, _external=True)

            # отправка пользователю подтверждения на email
            send_email(user.email_address, 'Подтвердите адрес электронной почты', 'mail/confirm',
                       link=link, user=user)

        # отправка email админу о новом пользователей
        if app.config['FLASKY_ADMIN']:
            send_email(app.config['FLASKY_ADMIN'], 'Новый пользователь ' + user.email_address,
                       'mail/new_user', user=user)

        flash(f'Учетная запись для адреса почты  '
              f'{user.email_address} успешно создана!', category='success')

        return redirect(url_for('utils_bp.registered'))

    if form.errors != {}:  # if there are no errors from validators
        for err_msg in form.errors.values():
            flash(f'Произошла ошибка при создании учетной записи : {err_msg}', category='danger')

    return render_template('register.html', form=form)


# USER Login route
@users_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Santa.query.filter_by(email_address=form.email_address.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            if not attempted_user.confirmed:
                flash('Ваша учетная запись создана, но не подтверждена. Проверьте почту и активируйте учетную запись. '
                      'Если после регистрации прошло больше 24 часов, то попробуйте зарегистрироваться заново.',
                      category='danger')
                return redirect(url_for('main_bp.login_page'))
            else:
                login_user(attempted_user)
                flash(f'Добро пожаловать {attempted_user.first_name} {attempted_user.last_name} ', category='success')
                if current_user.role == "user":
                    return redirect(url_for('users_bp.welcome_page'))
                if attempted_user.role == "admin":
                    return redirect(url_for('users_bp.status_page'))
        else:
            flash(f'Вы ввели не верный адрес почты или пароль. Попробуйте еще раз.', category='danger')
    return render_template('login.html', form=form)


# Password Reset route
@users_bp.route('/request_reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users_bp.welcome_page'))
    user = Santa.verify_reset_token(token)
    if user is None:
        flash(f'Вы использовали недействительный или просроченный токен.', category='warning')
        return redirect(url_for('utils_bp.request_reset_password'))
    reset_password_form = ResetPasswordForm()
    if reset_password_form.validate_on_submit():
        salt = bcrypt.gensalt()
        password = reset_password_form.password1.data.encode('utf-8')
        user.password_hash = bcrypt.hashpw(password, salt)
        db.session.commit()
        flash(f'Ваш пароль был успешно обновлен! Вы можете авторизоваться в системе', category='success')
        return redirect(url_for('users_bp.login_page'))
    return render_template('reset_password_with_token.html', reset_password_form=reset_password_form)


##########################################
# USER All gifts route
# Статусы подарков:
# None (NULL в БД) - подарок на елке
# 0 - подарок снят пользователем
# 1 - подарок заказан
# 2 - подарок доставлен на СВХ
# 3 - подарок вручен
##########################################
@users_bp.route('/mygifts', methods=['GET', 'POST'])
@login_required
def all_my_gifts_page():
    gift_status_update_form = GiftStatusUpdateForm()
    mail = Mail()
    gifts = Gift.query.filter_by(santa_id=current_user.id)
    gifts_on_tree = Gift.query.filter(Gift.status == None).all()
    if request.method == "GET":
        return render_template('mygifts.html', gifts=gifts, gift_status_update_form=gift_status_update_form,
                               gifts_on_tree=gifts_on_tree)

    if request.method == "POST":
        picked_gift = request.form.get('picked_gift')
        p_gift_object = Gift.query.filter_by(id=picked_gift).first()
        if p_gift_object:
            p_gift_object.status_update(request.form.get('status'), current_user)
            p_gift_object.status_updated_time = datetime.datetime.now()
            p_gift_object.status_updated_by_user = current_user.id
            flash(f'Статус подарка {p_gift_object.name} успешно обновлен!', category='success')

        with app.app_context():
            msg = Message(
                subject='Статус подарка обновлен ' + p_gift_object.name,
                sender=app.config.get('MAIL_USERNAME'),
                recipients=[current_user.email_address],
                body='Статус подарка ' + p_gift_object.name + ' обновлен')
            mail.send(msg)

        return render_template('mygifts.html', gifts=gifts, gift_status_update_form=gift_status_update_form)


# USER Profile Update route
@users_bp.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile_page(id):
    if current_user.id == id:
        user = current_user
        profile_update_form = ProfileUpdateForm()
        if profile_update_form.validate_on_submit():
            if request.method == 'POST':
                if user:
                    user.first_name = request.form['first_name']
                    user.last_name = request.form['last_name']
                    user.email_address = request.form['email_address']
                    user.phone = request.form['phone']

                    db.session.commit()
                    flash(f'Данные пользователя успешно обновлены.', category='success')
                    return redirect(url_for('users_bp.profile_page', id=current_user.id))
                return f'Профиля с ID = {id} не существует в базе данных'
            elif request.method == 'GET':
                profile_update_form.data.first_name = current_user.first_name
                profile_update_form.data.last_name = current_user.last_name
                profile_update_form.data.phone = current_user.phone
                profile_update_form.data.email_address = current_user.email_address
        if profile_update_form.errors != {}:
            for err_msg in profile_update_form.errors.values():
                flash(f'Произошла ошибка при обновлении профиля : {err_msg}', category='danger')

        return render_template('profile.html', user=user, profile_update_form=profile_update_form)
    else:
        abort(403)


# USER Logout route
@users_bp.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash('Вы вышли из системы', category='info')
    return redirect(url_for('main_bp.home_page'))


# Welcome page route
@users_bp.route('/welcome')
@login_required
def welcome_page():
    users = Santa.query.filter_by(id=current_user.id)
    gifts = Gift.query.filter_by(santa_id=current_user.id)
    gifts_on_tree = Gift.query.filter(Gift.status == None).all()
    houses = House.query.all()
    projects = Project.query.all()
    return render_template('welcome.html', gifts=gifts, users=users, houses=houses, projects=projects, gifts_on_tree=gifts_on_tree)


# STATUS page route
@users_bp.route('/status')
@login_required
def status_page():
    if current_user.role == "admin":
        users_registered = Santa.query.with_entities(func.count(distinct(Santa.email_address))).scalar()
        users_activated = Santa.query.filter(Santa.confirmed == True).count()
        number_of_santas_with_at_least_1_gift = Gift.query.with_entities(func.count(distinct(Gift.santa_id))).scalar()
        number_of_santas_without_gifts = users_activated - number_of_santas_with_at_least_1_gift
        gifts = Gift.query.all()
        gifts_on_tree = Gift.query.filter(Gift.status == None).all()
        gifts_picked_by_santas = Gift.query.filter(Gift.status != None).all()
        gifts_ordered = Gift.query.filter(Gift.status == 1).all()
        gifts_on_warehouse = Gift.query.filter(Gift.status == 2).all()
        houses = House.query.all()
        house_id = House.query.filter_by(id=House.id)
        projects = Project.query.all()
        return render_template('status.html', gifts=gifts, houses=houses, projects=projects,
                               gifts_on_tree=gifts_on_tree, gifts_picked_by_santas=gifts_picked_by_santas,
                               gifts_ordered=gifts_ordered, gifts_on_warehouse=gifts_on_warehouse, house_id=house_id,
                               number_of_santas_with_at_least_1_gift=number_of_santas_with_at_least_1_gift,
                               users_activated=users_activated,
                               users_registered=users_registered,
                               number_of_santas_without_gifts=number_of_santas_without_gifts,
                               )
    else:
        abort(403)
