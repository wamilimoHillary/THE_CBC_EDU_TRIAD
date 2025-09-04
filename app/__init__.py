from flask import Flask
from flask_mail import Mail
from .config import Config
from .routes.main_routes import main_routes
from .routes.auth_routes import auth_routes
from .routes.student_routes import student_routes
from .routes.teacher_routes import teacher_routes
from .routes.parent_routes import parent_routes
from .routes.admin_routes import admin_routes

# Create Flask-Mail instance
mail = Mail()

def create_app():
    # Create the Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize Flask-Mail with the app
    mail.init_app(app)
    

    # Register Blueprints
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(student_routes, url_prefix='/student')
    app.register_blueprint(teacher_routes, url_prefix='/teacher')
    app.register_blueprint(parent_routes, url_prefix='/parent')
    app.register_blueprint(admin_routes, url_prefix='/admin')

    return app