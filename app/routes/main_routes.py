from flask import Blueprint, render_template


main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('main/index.html') 

@main_routes.route('/about')
def about():
    return render_template('main/about.html') 

@main_routes.route('/features')
def features():
    return render_template('main/features.html')  