from flask import render_template, Blueprint
from fairy.models import Gift, Project

main_bp = Blueprint('main_bp', __name__)


# Main page route
@main_bp.route('/')
@main_bp.route('/home')
def home_page():
    project_name = Project.query.filter(Project.name != None).first()
    gifts_on_tree = Gift.query.filter(Gift.status == None).all()
    gifts_total = Gift.query.filter(Gift.id).all
    return render_template('home.html', gifts_on_tree=gifts_on_tree, project_name=project_name, gifts_total=gifts_total)


# About page route - description about the project
@main_bp.route('/about')
def about_page():
    return render_template('about.html')


# Contacts page route
@main_bp.route('/contacts')
def contacts_page():
    return render_template('contacts.html')




