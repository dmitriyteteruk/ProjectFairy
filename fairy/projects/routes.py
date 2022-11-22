from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint, abort
from flask_login import login_required, current_user
from fairy import db
from fairy.projects.forms import ProjectForm
from fairy.models import Project

projects_bp = Blueprint('projects_bp', __name__)


# PROJECTS page route
@projects_bp.route('/projects')
@login_required
def projects_page():
    if current_user.role == "admin":
        projects = Project.query.all()
        return render_template('projects.html', projects=projects)
    else:
        abort(403)


# ADD Project route
@projects_bp.route('/project/add_project', methods=['GET', 'POST'])
@login_required
def new_project_page():
    if current_user.role == "admin":
        project_form = ProjectForm()
        if request.method == "GET":
            return render_template('project_create.html', project_form=project_form)
        if request.method == "POST":
            if project_form.validate_on_submit():
                new_project = Project(
                    name=project_form.name.data,
                    description=project_form.description.data,
                    delivery_date=project_form.delivery_date.data,
                    visit_date=project_form.visit_date.data,
                    delivery_address=project_form.delivery_address,
                    contact_person=project_form.contact_person,
                    phone=project_form.phone,
                    pickup_point_address_1=project_form.pickup_point_address_1,
                    pickup_point_address_2=project_form.pickup_point_address_2)
                db.session.add(new_project)
                db.session.commit()
                flash(f'Проект {new_project.name} успешно добавлен!', category='success')
                return redirect(url_for('projects_bp.projects_page'))
            if project_form.errors != {}:  # if there are no errors from validators
                for err_msg in project_form.errors.values():
                    flash(f'Произошла ошибка при добавлении проекта: {err_msg}', category='danger')
        return render_template('projects.html')
    else:
        abort(403)


# EDIT Project route
@projects_bp.route('/project/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def project_edit(id):
    if current_user.role == "admin":
        project = Project.query.filter_by(id=id).first()
        project_form = ProjectForm()
        if project_form.validate_on_submit():
            if request.method == 'POST':
                if project:
                    project.name = request.form['name']
                    project.description = request.form['description']
                    project.delivery_date = request.form['delivery_date']
                    project.visit_date = request.form['visit_date']
                    project.delivery_address = request.form['delivery_address']
                    project.contact_person = request.form['contact_person']
                    project.phone = request.form['phone']
                    project.pickup_point_address_1 = request.form['pickup_point_address_1']
                    project.pickup_point_address_2 = request.form['pickup_point_address_2']

                    db.session.commit()
                    flash(f'Данные о проекте {project.name} успешно сохранены.', category='success')
                    return redirect(url_for('projects_bp.projects_page'))
                return f'Проекта с ID = {id} не существует в базе данных'

        if project_form.errors != {}:
            for err_msg in project_form.errors.values():
                flash(f'Произошла следующая ошибка при сохранении данных: {err_msg}', category='danger')

        return render_template('project_update.html', project=project, project_form=project_form)
    else:
        abort(403)


# DELETE Project route
@projects_bp.route('/project/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def project_delete(id):
    if current_user.role == "admin":
        project = Project.query.filter_by(id=id).first()
        if request.method == 'POST':
            if project:
                db.session.delete(project)
                db.session.commit()
                flash(f'Проект: {project.name} удален.', category='success')
                return redirect(url_for('projects_bp.projects_page'))
        return render_template('project_delete.html', project=project)
    else:
        abort(403)


