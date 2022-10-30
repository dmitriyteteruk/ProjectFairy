from flask import render_template, redirect, url_for, flash, request, Blueprint, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from fairy import db
from fairy.houses.forms import HouseForm
from fairy.models import House, Kid

houses_bp = Blueprint('houses_bp', __name__)


# HOUSES page route
@houses_bp.route('/houses')
@login_required
def houses_page():
    if current_user.role == "admin":
        # JOIN подзапрос для объединения таблиц kid + house
        kids_houses = db.session.query(
            House.short_name,
            House.contact_person,
            House.phone,
            House.id,
            Kid.house_id).outerjoin(Kid, Kid.house_id == House.id).subquery()

        # преобразование подзапроса в нужный формат (суммируем детей)
        result_query = db.session.query(
            kids_houses.c.short_name,
            func.count(kids_houses.c.house_id).label('kid_sum'),
            kids_houses.c.contact_person,
            kids_houses.c.id,
            kids_houses.c.phone.label('phone')).group_by(kids_houses.c.id).all()
        return render_template('houses.html', houses_with_kids=result_query)
    else:
        abort(403)

# ADD House route
@houses_bp.route('/houses/add_house', methods=['GET', 'POST'])
@login_required
def new_house_page():
    if current_user.role == "admin":
        house_form = HouseForm()
        if request.method == "GET":
            return render_template('house_create.html', house_form=house_form)

        if request.method == "POST":
            if house_form.validate_on_submit():
                new_house = House(short_name=house_form.short_name.data,
                                  full_name=house_form.full_name.data,
                                  address=house_form.address.data,
                                  phone=house_form.phone.data,
                                  email=house_form.email_address.data,
                                  contact_person=house_form.contact_person.data)
                db.session.add(new_house)
                db.session.commit()
                flash(f'Учреждение {new_house.short_name} успешно добавлено!', category='success')
                return redirect(url_for('houses_bp.houses_page'))

            if house_form.errors != {}:  # if there are no errors from validators
                for err_msg in house_form.errors.values():
                    flash(f'Произошла ошибка при добавлении учреждения : {err_msg}', category='danger')

        return render_template('houses.html')
    else:
        abort(403)


# DELETE House route
@houses_bp.route('/houses/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def house_delete(id):
    if current_user.role == "admin":
        house = House.query.filter_by(id=id).first()
        if request.method == 'POST':
            if house:
                db.session.delete(house)
                db.session.commit()
                flash(f'Учреждение: {house.short_name} удалено.', category='success')
                return redirect(url_for('houses_bp.houses_page'))
        return render_template('house_delete.html', house=house)
    else:
        abort(403)

# EDIT House route
@houses_bp.route('/houses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def house_edit(id):
    if current_user.role == "admin":
        house = House.query.filter_by(id=id).first()
        house_form = HouseForm()
        if house_form.validate_on_submit():
            if request.method == 'POST':
                if house:
                    house.short_name = request.form['short_name']
                    house.full_name = request.form['full_name']
                    house.address = request.form['address']
                    house.phone = request.form['phone']
                    house.email = request.form['email_address']
                    house.contact_person = request.form['contact_person']

                    db.session.commit()
                    flash(f'Данные об учреждении: {house.short_name} успешно сохранены.', category='success')
                    return redirect(url_for('houses_bp.houses_page'))
                return f'Учреждения с ID = {id} не существует в базе данных'

        if house_form.errors != {}:
            for err_msg in house_form.errors.values():
                flash(f'Произошла ошибка при добавлении учреждения : {err_msg}', category='danger')

        return render_template('house_update.html', house=house, house_form=house_form)
    else:
        abort(403)