# database/database.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def init_db(app):
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import models inside app context to avoid circular imports
    with app.app_context():
        # Import models here - this prevents circular imports
        import models.user
        import models.student
        import models.course
        import models.payment
        import models.result
        
        # Create all tables
        db.create_all()
        print("✓ Database initialized successfully!")
        print("✓ All tables created!")