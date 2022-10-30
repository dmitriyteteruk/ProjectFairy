import os
import hashlib

from flask import render_template, redirect, url_for, flash, request, Blueprint, jsonify, abort
from flask_login import login_required, current_user
from flask_mail import Mail, Message  # эту ошибку можно игнорировать
from sqlalchemy import func
from werkzeug.utils import secure_filename

from fairy import app, db, age_calculator, allowed_file, gifts
from fairy.gifts.forms import PickGift, GiftForm
from fairy.models import Gift, Santa, Project, House, Kid

gifts_bp = Blueprint('gifts_bp', __name__)


# GITS page route
@gifts_bp.route('/gifts/page/<int:page_num>')
@login_required
def gifts_page(page_num):
    if current_user.role == "admin":
        gifts = Gift.query.paginate(per_page=20, page=page_num, error_out=True)
        return render_template('gifts.html', gifts=gifts)
    else:
        abort(403)

# route для отображения картинки
@gifts_bp.route('/display/<filename>')
@login_required
def display_image(filename):
    return redirect(url_for('static', filename='/uploads/' + filename), code=301)


# CREATE Gift route
@gifts_bp.route('/gifts/add_gift/', methods=['GET', 'POST'])
@login_required
def new_gift_page():
    if current_user.role == "admin":
        gift_form = GiftForm()
        gift_form.house.choices = [(house.id, house.short_name) for house in House.query.all()]
        gift_form.house.choices.insert(0, (0, "-----"))
        print(gift_form.house.choices)
        gift_form.project_id.choices = [(project.id, project.name) for project in Project.query.all()]
        gift_form.project_id.choices.insert(0, (0, "-----"))
        basedir = os.path.abspath(os.path.dirname(__file__))
        basedir = os.chdir(basedir)
        basedir = os.chdir('../')
        basedir = os.getcwd()
        basedir = str(basedir)
        filename = ''
        postcard_url = ''

        if request.method == 'POST':
            kid_id = Kid.query.filter_by(id=gift_form.kid.data).first()
            if gift_form.validate_on_submit():
                if 'file' not in request.files:
                    flash('Не найден файл')
                file = request.files['file']
                if file.filename == '':
                    flash('Не выбрано изображение для загрузки')
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = hashlib.sha1(filename.encode())
                    filename = filename.hexdigest() + '.jpg'
                    postcard_url = filename
                    postcard_url_is_unique = Gift.query.filter_by(postcard_url=postcard_url).first()
                    if postcard_url_is_unique:
                        flash(f'Файл с именем : {filename} уже есть на сервере, измените имя файла',
                              category='danger')
                    else:
                        file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                        new_gift = Gift(
                            name=gift_form.name.data,
                            description=gift_form.description.data,
                            postcard_url=postcard_url,
                            kid_id=gift_form.kid.data,
                            project_id=gift_form.project_id.data,
                        )

                        db.session.add(new_gift)
                        db.session.commit()
                        text_year = ''
                        if age_calculator(kid_id.birthday) == 1:
                            text_year = 'год'
                        elif 2 <= age_calculator(kid_id.birthday) <= 4:
                            text_year = 'года'
                        elif 5 <= age_calculator(kid_id.birthday) <= 20:
                            text_year = 'лет'

                        flash(
                            f'Подарок {new_gift.name} для {kid_id.name} {age_calculator(kid_id.birthday)} {text_year} успешно '
                            f'добавлен!',
                            category='success')
                        return redirect(url_for('gifts_bp.gifts_page', page_num=1))
                    if gift_form.errors != {}:
                        for err_msg in gift_form.errors.values():
                            flash(f'Произошла ошибка при добавлении подарка: {err_msg}', category='danger')
                    return render_template('gift_create.html', gift_form=gift_form, filename=filename,
                                           postcard_url=postcard_url)

                elif flash('Разрешенные расширения файлов - PNG, JPG, JPEG', category='info'):
                    return redirect(request.url)

        return render_template('gift_create.html', gift_form=gift_form, filename=filename, postcard_url=postcard_url)
    else:
        abort(403)


# EDIT Gift route
@gifts_bp.route('/gift/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def gift_edit(id):
    if current_user.role == "admin":
        gift = Gift.query.filter_by(id=id).first()
        kid = Kid.query.filter_by(id=gift.kid_id).first()
        project = Project.query.filter_by(id=gift.project_id).first()
        list_of_houses_without_current = db.session.query(House.id, House.short_name).filter(House.id != kid.house_id)
        kids_without_current = db.session.query(Kid.id, Kid.name).filter(gift.id != gift.kid_id)
        project_without_current = db.session.query(Project.id, Project.name).filter(gift.project_id != Project.id)
        gift_form = GiftForm()
        gift_form.house.choices = [(house.id, house.short_name) for house in House.query.all()]
        gift_form.project_id.choices = [(project.id, project.name) for project in Project.query.all()]

        filename = gift.postcard_url
        if request.method == 'POST':
            if gift_form.validate_on_submit():
                if gift:
                    gift.name = request.form['name']
                    gift.description = request.form['description']
                    gift.postcard_url = filename
                    gift.house = request.form['house']
                    gift.kid_id = request.form['kid']
                    gift.project_id = request.form['project_id']
                    db.session.commit()
                    flash(f'Данные о подарке: {gift.name} успешно сохранены.', category='success')
                    return redirect(url_for('gifts_bp.gifts_page', page_num=1))
                return flash(f'Подарка с ID = {id} не существует в базе данных')

        if gift_form.errors != {}:
            for err_msg in gift_form.errors.values():
                flash(f'Произошла следующая ошибка при обновлении информации о подарке: {err_msg}', category='danger')

        return render_template('gift_update.html', gift=gift, gift_form=gift_form, filename=filename,
                               list_of_houses_without_current=list_of_houses_without_current, kid=kid,
                               kids_without_current=kids_without_current,
                               project_without_current=project_without_current,
                               project=project
                               )
    else:
        abort(403)


# DELETE Gift route
@gifts_bp.route('/gift/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def gift_delete(id):
    if current_user.role == "admin":
        basedir = os.path.abspath(os.path.dirname(__file__))
        basedir = os.chdir(basedir)
        basedir = os.chdir('../')
        basedir = os.getcwd()
        basedir = str(basedir)
        gift = Gift.query.filter_by(id=id).first()
        if request.method == 'POST':
            if gift:
                os.remove(os.path.join(basedir, app.config['UPLOAD_FOLDER'], gift.postcard_url))
                db.session.delete(gift)
                db.session.commit()
                flash(f'Запись о подарке: {gift.name} удалена из БД.', category='success')
                return redirect(url_for('gifts_bp.gifts_page', page_num=1))
        return render_template('gift_delete.html', gift=gift)
    abort(403)


# SELECTOR ROUTE FOR HOUSE -> KIDS
@app.route('/gifts/add_gift/<get_kid>')
@login_required
def kid_by_house(get_kid):
    if current_user.role == "admin":
        kid = Kid.query.filter_by(house_id=get_kid).all()
        stateArray = []
        for city in kid:
            stateObj = {}
            stateObj['id'] = city.id
            stateObj['name'] = city.name
            stateArray.append(stateObj)
        return jsonify({'kidhouse': stateArray})
    abort(403)


# Tree page route
@gifts_bp.route('/tree/', methods=['GET', 'POST'])
@login_required
def tree_page():
    purchase_form = PickGift()
    mail = Mail()

    # логика отображения данные из БД, где подарок не снят.
    if request.method == "GET":
        # выводим 5 случайных подарков
        gifts = Gift.query.filter_by(santa_id=None).order_by(func.rand()).limit(5).all()
        return render_template('tree.html', gifts=gifts, purchase_form=purchase_form)

    # Purchase item logic
    if request.method == "POST":
        picked_gift = request.form.get('picked_gift')
        p_gift_object = Gift.query.filter_by(name=picked_gift).first()
        if p_gift_object:
            # нижеследующий if реализует проверку наличия подарка в момент нажатия кнопки
            if p_gift_object.santa_id is None:
                p_gift_object.assign_ownership(current_user)
                with app.app_context():
                    msg = Message(
                        subject='Вы сняли открытку с подарком ' + p_gift_object.name,
                        sender=app.config.get('MAIL_USERNAME'),
                        recipients=[current_user.email_address, 'dmitriy.teteruk@gmail.com'],
                        body='Вы сняли открытку с подарком ' + p_gift_object.name + ' для ' + p_gift_object.kid.name)
                    mail.send(msg)

                flash(f'Поздравляем! Вы успешно сняли шарик! {p_gift_object.kid.name} теперь не останется без '
                      f'подарка!',
                      category='success')
                return redirect(url_for('users_bp.all_my_gifts_page'))
            else:
                flash(f'Упс! Открытку {p_gift_object.name} уже снял другой Дед Мороз ', category='danger')
        return redirect(url_for('gifts_bp.tree_page'))
