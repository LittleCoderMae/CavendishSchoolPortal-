from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from database.database import db
from models.user import User, UserRole, Payment  # Updated imports
import uuid

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/make_payment', methods=['POST'])
@login_required
def make_payment():
    if not current_user.is_student():
        return jsonify({'success': False, 'message': 'Access denied. Students only.'})
    
    # No need to query Student - current_user IS the student
    amount = float(request.form.get('amount'))
    payment_type = request.form.get('payment_type')
    payment_method = request.form.get('payment_method')
    
    # Use current_user's data directly
    academic_year = request.form.get('academic_year', current_user.year_of_study)
    semester = request.form.get('semester', getattr(current_user, 'semester', 1))  # Fallback if semester doesn't exist
    
    # Generate transaction ID
    transaction_id = str(uuid.uuid4())[:8].upper()
    
    # Create payment using user_id instead of student_id
    payment = Payment(
        user_id=current_user.id,  # Changed from student_id to user_id
        amount=amount,
        payment_type=payment_type,
        payment_method=payment_method,
        transaction_id=transaction_id,
        academic_year=academic_year,
        semester=semester,
        description=f"{payment_type} payment via {payment_method}",
        status='completed'  # Add status field
    )
    
    db.session.add(payment)
    db.session.commit()
    
    flash(f'Payment of K{amount} completed successfully! Transaction ID: {transaction_id}', 'success')
    return redirect(url_for('student.payments'))

@payment_bp.route('/docket_fee', methods=['POST'])
@login_required
def pay_docket_fee():
    if not current_user.is_student():
        return jsonify({'success': False, 'message': 'Access denied. Students only.'})
    
    # No need to query Student - current_user IS the student
    # Generate transaction ID
    transaction_id = str(uuid.uuid4())[:8].upper()
    
    # Create payment using user_id instead of student_id
    payment = Payment(
        user_id=current_user.id,  # Changed from student_id to user_id
        amount=5.00,  # K5 docket printing fee
        payment_type='docket_printing',
        payment_method='mobile_money',  # Default method
        transaction_id=transaction_id,
        academic_year=current_user.year_of_study,
        semester=getattr(current_user, 'semester', 1),  # Fallback if semester doesn't exist
        description='Docket printing fee',
        status='completed'  # Add status field
    )
    
    db.session.add(payment)
    db.session.commit()
    
    flash('Docket printing fee paid successfully! You can now print your dockets.', 'success')
    return redirect(url_for('student.dockets'))

# ------------------------------------------------------------
# ADDITIONAL PAYMENT ROUTES (Optional enhancements)
# ------------------------------------------------------------

@payment_bp.route('/history')
@login_required
def payment_history():
    """View payment history for students"""
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get all payments for this user
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(
        Payment.payment_date.desc()
    ).all()
    
    return render_template('student/payment_history.html', payments=payments)

@payment_bp.route('/status/<transaction_id>')
@login_required
def payment_status(transaction_id):
    """Check payment status"""
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    
    if not payment:
        flash('Payment not found.', 'error')
        return redirect(url_for('student.payments'))
    
    # Verify the payment belongs to the current user
    if payment.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('student/payment_status.html', payment=payment)

@payment_bp.route('/api/my_payments')
@login_required
def my_payments_api():
    """API endpoint to get current user's payments"""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(
        Payment.payment_date.desc()
    ).all()
    
    payments_data = [{
        'id': payment.id,
        'amount': payment.amount,
        'description': payment.description,
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'status': payment.status,
        'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
        'academic_year': payment.academic_year,
        'semester': payment.semester
    } for payment in payments]
    
    return jsonify({'payments': payments_data})