# routes/admin.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('admin/dashboard.html')

@admin_bp.route('/students')
@login_required
def students():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    from models.student import Student
    all_students = Student.query.all()
    return render_template('admin/students.html', students=all_students)

@admin_bp.route('/payments')
@login_required
def payments():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    from models.payment import Payment
    all_payments = Payment.query.all()
    return render_template('admin/payments.html', payments=all_payments)