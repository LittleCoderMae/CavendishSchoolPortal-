# utils/payment_calculator.py
from models.payment import Payment
from models.student import Student
from config import Config

def calculate_total_fees(student_id, academic_year, semester):
    """Calculate total fees for student's registered courses"""
    student = Student.query.get(student_id)
    if not student:
        return 0
    
    total_fees = sum(course.fee_amount for course in student.registered_courses)
    return total_fees

def calculate_paid_amount(student_id, academic_year, semester):
    """Calculate total amount paid by student"""
    total_paid = Payment.query.filter_by(
        student_id=student_id,
        academic_year=academic_year,
        semester=semester,
        status='completed'
    ).with_entities(db.func.sum(Payment.amount)).scalar() or 0
    
    return total_paid

def check_payment_threshold(student_id, exam_type, academic_year, semester):
    """Check if student has paid required percentage for exam docket"""
    total_fees = calculate_total_fees(student_id, academic_year, semester)
    paid_amount = calculate_paid_amount(student_id, academic_year, semester)
    
    if total_fees == 0:
        return False
    
    payment_ratio = paid_amount / total_fees
    
    if exam_type == 'cat1':
        return payment_ratio >= Config.CAT1_PAYMENT_THRESHOLD
    elif exam_type == 'cat2':
        return payment_ratio >= Config.CAT2_PAYMENT_THRESHOLD
    elif exam_type == 'final':
        return payment_ratio >= Config.FINAL_EXAM_PAYMENT_THRESHOLD
    else:
        return False

def has_paid_docket_printing_fee(student_id, academic_year, semester):
    """Check if student has paid the K5 docket printing fee"""
    docket_payment = Payment.query.filter_by(
        student_id=student_id,
        academic_year=academic_year,
        semester=semester,
        payment_type='docket_printing',
        status='completed'
    ).first()
    
    return docket_payment is not None