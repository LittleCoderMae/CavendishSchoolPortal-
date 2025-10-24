# manage.py
from app import create_app
from database import db
from flask_script import Manager

app = create_app('development')
manager = Manager(app)

@manager.command
def create_db():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
    print("Database tables created!")

@manager.command
def drop_db():
    """Drop all database tables"""
    with app.app_context():
        db.drop_all()
    print("Database tables dropped!")

if __name__ == '__main__':
    manager.run()