# models/user.py
from flask_login import UserMixin
from database.database import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, lecturer, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Use string for the relationship to avoid circular imports
    student_profile = db.relationship('Student', backref='user', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<User {self.username} - {self.role}>'