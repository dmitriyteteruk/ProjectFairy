import datetime
from datetime import timedelta

from flask import render_template, Blueprint
from fairy.models import Gift, Project

main_bp = Blueprint('main_bp', __name__)


# Main page route
@main_bp.route('/')
@main_bp.route('/home')
def home_page():
    active_project = Project.query.filter(Project.delivery_date >= datetime.date.today()).first()
    gifts_on_tree = Gift.query.filter(Gift.status == None, Gift.project_id == active_project.id).all()
    gifts_total = Gift.query.filter(Gift.project_id == active_project.id).all()
    project_date = Project.query.filter(Project.delivery_date).first()
    today_date = datetime.date.today()
    return render_template('home.html', gifts_on_tree=gifts_on_tree, active_project=active_project, gifts_total=gifts_total, project_date=project_date, today_date=today_date)


# About page route - description about the project
@main_bp.route('/about')
def about_page():
    return render_template('about.html')


# Contacts page route
@main_bp.route('/contacts')
def contacts_page():
    return render_template('contacts.html')
