# routes/payment.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from database.database import db
from models.payment import Payment
from models.student import Student

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/make_payment', methods=['POST'])
@login_required
def make_payment():
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    amount = float(request.form.get('amount'))
    payment_type = request.form.get('payment_type')
    payment_method = request.form.get('payment_method')
    academic_year = request.form.get('academic_year', student.year_of_study)
    semester = request.form.get('semester', student.semester)
    
    # Generate transaction ID (in real app, use proper payment gateway)
    import uuid
    transaction_id = str(uuid.uuid4())[:8].upper()
    
    payment = Payment(
        student_id=student.id,
        amount=amount,
        payment_type=payment_type,
        payment_method=payment_method,
        transaction_id=transaction_id,
        academic_year=academic_year,
        semester=semester,
        description=f"{payment_type} payment via {payment_method}"
    )
    
    db.session.add(payment)
    db.session.commit()
    
    flash(f'Payment of K{amount} completed successfully! Transaction ID: {transaction_id}', 'success')
    return redirect(url_for('student.payments'))

@payment_bp.route('/docket_fee', methods=['POST'])
@login_required
def pay_docket_fee():
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Generate transaction ID
    import uuid
    transaction_id = str(uuid.uuid4())[:8].upper()
    
    payment = Payment(
        student_id=student.id,
        amount=5.00,  # K5 docket printing fee
        payment_type='docket_printing',
        payment_method='mobile_money',  # Default method
        transaction_id=transaction_id,
        academic_year=student.year_of_study,
        semester=student.semester,
        description='Docket printing fee'
    )
    
    db.session.add(payment)
    db.session.commit()
    
    flash('Docket printing fee paid successfully! You can now print your dockets.', 'success')
    return redirect(url_for('student.dockets'))