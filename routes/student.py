# routes/student.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database.database import db
from models.student import Student, student_courses
from models.course import Course
from models.payment import Payment
from models.result import Result

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('student/dashboard.html', student=student)

@student_bp.route('/registration', methods=['GET', 'POST'])
@login_required
def registration():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        course_ids = request.form.getlist('courses')
        academic_year = request.form.get('academic_year')
        semester = request.form.get('semester')
        
        # Clear existing registrations for this academic year and semester
        db.session.execute(
            student_courses.delete().where(
                student_courses.c.student_id == student.id,
                student_courses.c.academic_year == academic_year,
                student_courses.c.semester == semester
            )
        )
        
        # Add new course registrations
        for course_id in course_ids:
            db.session.execute(
                student_courses.insert().values(
                    student_id=student.id,
                    course_id=course_id,
                    academic_year=academic_year,
                    semester=semester
                )
            )
        
        db.session.commit()
        flash('Course registration successful!', 'success')
        return redirect(url_for('student.registration'))
    
    # Get available courses for student's year and semester
    available_courses = Course.query.filter_by(
        year_offered=student.year_of_study,
        semester_offered=student.semester,
        is_active=True
    ).all()
    
    # Get currently registered courses
    registered_courses = student.registered_courses
    
    return render_template('student/registration.html', 
                         available_courses=available_courses,
                         registered_courses=registered_courses,
                         student=student)

@student_bp.route('/payments')
@login_required
def payments():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    student_payments = Payment.query.filter_by(student_id=student.id).all()
    
    return render_template('student/payments.html', 
                         payments=student_payments,
                         student=student)

@student_bp.route('/results')
@login_required
def results():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    student_results = Result.query.filter_by(
        student_id=student.id,
        is_published=True
    ).all()
    
    return render_template('student/results.html', 
                         results=student_results,
                         student=student)

@student_bp.route('/dockets')
@login_required
def dockets():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Check docket printing fee payment
    from utils.payment_calculator import has_paid_docket_printing_fee
    docket_fee_paid = has_paid_docket_printing_fee(student.id, student.year_of_study, student.semester)
    
    # Check exam eligibility
    from utils.payment_calculator import check_payment_threshold
    cat1_eligible = check_payment_threshold(student.id, 'cat1', student.year_of_study, student.semester)
    cat2_eligible = check_payment_threshold(student.id, 'cat2', student.year_of_study, student.semester)
    final_eligible = check_payment_threshold(student.id, 'final', student.year_of_study, student.semester)
    
    return render_template('student/dockets.html',
                         student=student,
                         docket_fee_paid=docket_fee_paid,
                         cat1_eligible=cat1_eligible,
                         cat2_eligible=cat2_eligible,
                         final_eligible=final_eligible)