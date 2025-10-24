# app.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template
from config import app_config

# Import database components
from database.database import db, login_manager

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    
    # Import models to ensure they are registered with SQLAlchemy
    import models.user
    import models.student
    import models.course
    import models.payment
    import models.result
    
    # Initialize database and login manager
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Define user_loader after models are imported
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✓ Database tables created!")
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp
    from routes.payment import payment_bp
    from routes.results import results_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(results_bp, url_prefix='/results')
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True)