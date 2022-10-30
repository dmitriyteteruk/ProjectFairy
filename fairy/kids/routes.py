from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint, abort
from flask_login import login_required, current_user
from fairy import db
from fairy.kids.forms import KidForm
from fairy.models import House, Kid

kids_bp = Blueprint('kids_bp', __name__)


# KIDS page route
@kids_bp.route('/kids/page/<int:page_num>')
@login_required
def kids_page(page_num):
    if current_user.role == "admin":
        kids = Kid.query.paginate(per_page=10, page=page_num, error_out=True)
        return render_template('kids.html', kids=kids)
    else:
        abort(403)


# CREATE Kid route
@kids_bp.route('/kids/add_kid', methods=['GET', 'POST'])
@login_required
def new_kid_page():
    if current_user.role == "admin":
        kid_form = KidForm()
        list_of_houses = db.session.query(House.id, House.short_name).all()
        if request.method == "GET":
            return render_template('kid_create.html', kid_form=kid_form, list_of_houses=list_of_houses)
        if request.method == "POST":
            if kid_form.validate_on_submit():
                new_kid = Kid(
                    name=kid_form.name.data,
                    birthday=kid_form.birthday.data,
                    house_id=kid_form.house_id.data)
                db.session.add(new_kid)
                db.session.commit()
                flash(f'Ребенок {new_kid.name} успешно добавлен!', category='success')
                return redirect(url_for('kids_bp.kids_page', page_num=1))
            if kid_form.errors != {}:  # if there are no errors from validators
                for err_msg in kid_form.errors.values():
                    flash(f'Произошла следующая ошибка при добавлении ребенка: {err_msg}', category='danger')
        return render_template('kids.html')
    else:
        abort(403)


# EDIT Kid route
@kids_bp.route('/kids/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def kid_edit(id):
    if current_user.role == "admin":
        kid = Kid.query.filter_by(id=id).first()
        kid_form = KidForm()
        list_of_houses_without_current = db.session.query(House.id, House.short_name).filter(House.id != kid.house_id)
        if kid_form.validate_on_submit():
            if request.method == 'POST':
                if kid:
                    kid.name = request.form['name']
                    kid.birthday = request.form['birthday']
                    kid.house_id = request.form['house_id']
                    db.session.commit()
                    flash(f'Данные о ребенке: {kid.name} успешно сохранены.', category='success')
                    return redirect(url_for('kids_bp.kids_page', page_num=1))
                return f'Ребенка с ID = {id} не существует в базе данных'

        if kid_form.errors != {}:
            for err_msg in kid_form.errors.values():
                flash(f'Произошла следующая ошибка при обновлении информации о ребенке: {err_msg}', category='danger')

        return render_template('kid_update.html', kid=kid, kid_form=kid_form,
                               list_of_houses_without_current=list_of_houses_without_current)
    else:
        abort(403)

# DELETE Kid route
@kids_bp.route('/kids/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def kid_delete(id):
    if current_user.role == "admin":
        kid = Kid.query.filter_by(id=id).first()
        if request.method == 'POST':
            if kid:
                db.session.delete(kid)
                db.session.commit()
                flash(f'Запись о ребенке: {kid.name} удалена из БД.', category='success')
                return redirect(url_for('kids_bp.kids_page', page_num=1))
        return render_template('kid_delete.html', kid=kid)
    else:
        abort(403)