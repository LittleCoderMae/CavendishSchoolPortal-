from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from database.database import db
from models.user import User, UserRole, Payment, Result
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get student's recent data
    recent_payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.payment_date.desc()).limit(5).all()
    recent_results = Result.query.filter_by(user_id=current_user.id).order_by(Result.created_at.desc()).limit(5).all()
    
    return render_template('student/dashboard.html', 
                         student=current_user,
                         payments=recent_payments,
                         results=recent_results)

@student_bp.route('/registration', methods=['GET', 'POST'])
@login_required
def registration():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        course_ids = request.form.getlist('courses')
        academic_year = request.form.get('academic_year')
        semester = request.form.get('semester')
        
        # TODO: Implement course registration logic
        # Since we simplified models, you might need to adjust this based on your course structure
        
        flash('Course registration submitted!', 'success')
        return redirect(url_for('student.registration'))
    
    # Get available courses (temporarily empty until Course model is created)
    available_courses = []  # Empty list for now
    
    return render_template('student/registration.html', 
                         available_courses=available_courses,
                         student=current_user)

@student_bp.route('/payments')
@login_required
def payments():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    student_payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.payment_date.desc()).all()
    
    # Calculate totals
    total_paid = sum(p.amount for p in student_payments if p.status == 'completed')
    total_pending = sum(p.amount for p in student_payments if p.status == 'pending')
    
    return render_template('student/payments.html', 
                         payments=student_payments,
                         student=current_user,
                         total_paid=total_paid,
                         total_pending=total_pending)

@student_bp.route('/results')
@login_required
def results():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    student_results = Result.query.filter_by(user_id=current_user.id).order_by(
        Result.academic_year.desc(), 
        Result.semester.desc()
    ).all()
    
    # Calculate GPA or averages if needed
    if student_results:
        total_marks = sum(result.marks for result in student_results)
        average_marks = total_marks / len(student_results)
    else:
        average_marks = 0
    
    return render_template('student/results.html', 
                         results=student_results,
                         student=current_user,
                         average_marks=average_marks)

@student_bp.route('/dockets')
@login_required
def dockets():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    # Check payment status for docket printing
    docket_fee_paid = check_docket_fee_payment(current_user.id)
    
    # Check exam eligibility based on payments
    cat1_eligible = check_exam_eligibility(current_user.id, 'cat1')
    cat2_eligible = check_exam_eligibility(current_user.id, 'cat2')
    final_eligible = check_exam_eligibility(current_user.id, 'final')
    
    return render_template('student/dockets.html',
                         student=current_user,
                         docket_fee_paid=docket_fee_paid,
                         cat1_eligible=cat1_eligible,
                         cat2_eligible=cat2_eligible,
                         final_eligible=final_eligible)

@student_bp.route('/profile')
@login_required
def profile():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('student/profile.html', student=current_user)

@student_bp.route('/registration-slip')
@login_required
def registration_slip():
    """Download registration slip"""
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    # Create a simple PDF registration slip
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content to PDF
    p.drawString(100, 750, "CAVENDISH UNIVERSITY ZAMBIA")
    p.drawString(100, 730, "STUDENT REGISTRATION SLIP")
    p.drawString(100, 700, f"Student ID: {current_user.student_id}")
    p.drawString(100, 680, f"Name: {current_user.first_name} {current_user.last_name}")
    p.drawString(100, 660, f"Program: {current_user.program}")
    p.drawString(100, 640, f"Year: {current_user.year_of_study}")
    p.drawString(100, 620, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    p.drawString(100, 600, "This is your official registration slip.")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"registration_slip_{current_user.student_id}.pdf", mimetype='application/pdf')

@student_bp.route('/timetable')
@login_required
def timetable():
    """Download timetable"""
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    # Create a simple PDF timetable
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content to PDF
    p.drawString(100, 750, "CAVENDISH UNIVERSITY ZAMBIA")
    p.drawString(100, 730, "STUDENT TIMETABLE")
    p.drawString(100, 700, f"Student ID: {current_user.student_id}")
    p.drawString(100, 680, f"Name: {current_user.first_name} {current_user.last_name}")
    p.drawString(100, 660, f"Program: {current_user.program}")
    p.drawString(100, 640, "Academic Year: 2024")
    
    # Sample timetable
    p.drawString(100, 600, "Monday: Computer Science 09:00-11:00")
    p.drawString(100, 580, "Tuesday: Mathematics 10:00-12:00")
    p.drawString(100, 560, "Wednesday: Physics 08:00-10:00")
    p.drawString(100, 540, "Thursday: Programming 14:00-16:00")
    p.drawString(100, 520, "Friday: Research Methods 11:00-13:00")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"timetable_{current_user.student_id}.pdf", mimetype='application/pdf')

# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def check_docket_fee_payment(user_id):
    """Check if student has paid docket printing fee"""
    docket_payment = Payment.query.filter_by(
        user_id=user_id,
        description='Docket printing fee',
        status='completed'
    ).first()
    return docket_payment is not None

def check_exam_eligibility(user_id, exam_type):
    """Check if student is eligible for specific exam based on payments"""
    # Define payment thresholds for each exam type
    thresholds = {
        'cat1': 0.25,  # 25% of fees paid
        'cat2': 0.50,  # 50% of fees paid  
        'final': 0.75  # 75% of fees paid
    }
    
    # Get total payments for current user
    total_payments = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.user_id == user_id,
        Payment.status == 'completed'
    ).scalar() or 0
    
    # TODO: Get total required fees (you might need a Fees model)
    total_required_fees = 5000  # Example amount
    
    payment_ratio = total_payments / total_required_fees if total_required_fees > 0 else 0
    
    return payment_ratio >= thresholds.get(exam_type, 1.0)

# ------------------------------------------------------------
# API ENDPOINTS FOR AJAX CALLS
# ------------------------------------------------------------

@student_bp.route('/api/payment-summary')
@login_required
def payment_summary():
    if not current_user.is_student():
        return {'error': 'Access denied'}, 403
    
    completed_payments = Payment.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).all()
    
    pending_payments = Payment.query.filter_by(
        user_id=current_user.id, 
        status='pending'
    ).all()
    
    total_completed = sum(p.amount for p in completed_payments)
    total_pending = sum(p.amount for p in pending_payments)
    
    return {
        'total_completed': total_completed,
        'total_pending': total_pending,
        'completed_count': len(completed_payments),
        'pending_count': len(pending_payments)
    }

@student_bp.route('/api/result-summary')
@login_required
def result_summary():
    if not current_user.is_student():
        return {'error': 'Access denied'}, 403
    
    results = Result.query.filter_by(user_id=current_user.id).all()
    
    if not results:
        return {'message': 'No results available'}
    
    # Calculate statistics
    total_courses = len(results)
    average_marks = sum(r.marks for r in results) / total_courses
    
    # Count grades
    grade_distribution = {}
    for result in results:
        grade_distribution[result.grade] = grade_distribution.get(result.grade, 0) + 1
    
    return {
        'total_courses': total_courses,
        'average_marks': round(average_marks, 2),
        'grade_distribution': grade_distribution,
        'latest_result': {
            'course_name': results[0].course_name,
            'grade': results[0].grade,
            'marks': results[0].marks
        } if results else None
    }