from flask import render_template, Blueprint

main_bp = Blueprint('main_bp', __name__)


# Main page route
@main_bp.route('/')
@main_bp.route('/home')
def home_page():
    return render_template('home.html')


# About page route - description about the project
@main_bp.route('/about')
def about_page():
    return render_template('about.html')


# Contacts page route
@main_bp.route('/contacts')
def contacts_page():
    return render_template('contacts.html')




