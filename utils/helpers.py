# utils/helpers.py
import re
from flask import flash
from models.payment import Payment
from models.student import Student

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def format_currency(amount):
    """Format amount as currency"""
    return f"K{amount:,.2f}"

def calculate_student_balance(student_id, academic_year, semester):
    """Calculate student's fee balance"""
    student = Student.query.get(student_id)
    if not student:
        return 0
    
    # Get total fees for registered courses
    total_fees = sum(course.fee_amount for course in student.registered_courses)
    
    # Get total payments made
    total_payments = Payment.query.filter_by(
        student_id=student_id,
        academic_year=academic_year,
        semester=semester,
        status='completed'
    ).with_entities(db.func.sum(Payment.amount)).scalar() or 0
    
    return total_fees - total_payments

def check_docket_eligibility(student_id, exam_type, academic_year, semester):
    """Check if student is eligible to print docket for specific exam"""
    from .payment_calculator import check_payment_threshold
    
    return check_payment_threshold(student_id, exam_type, academic_year, semester)