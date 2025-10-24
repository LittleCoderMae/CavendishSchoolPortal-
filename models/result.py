# models/result.py
from database.database import db
from datetime import datetime

class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    academic_year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    
    # Assessment marks
    cat1_marks = db.Column(db.Float, default=0.0)
    cat2_marks = db.Column(db.Float, default=0.0)
    final_exam_marks = db.Column(db.Float, default=0.0)
    
    # Calculated fields
    total_marks = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(2))  # A, B, C, D, F
    grade_point = db.Column(db.Float, default=0.0)
    
    # Status
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Result {self.student_id} - {self.course_id} - {self.total_marks}>'