from datetime import datetime
from database.database import db

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('chat_sessions', lazy=True))
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ChatSession {self.id} for User {self.user_id}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_bot = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {"Bot" if self.is_bot else "User"}>'