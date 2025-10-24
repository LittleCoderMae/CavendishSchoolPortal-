# models/payment.py
from database.database import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_type = db.Column(db.String(50), nullable=False)  # tuition, docket, etc.
    reference = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='completed')
    
    def __repr__(self):
        return f'<Payment {self.reference}>'