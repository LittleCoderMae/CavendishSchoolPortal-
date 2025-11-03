from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from database.database import db
from models.user import User, UserRole, Payment, Result  # Updated imports

admin_bp = Blueprint('admin', __name__)

# ------------------------------------------------------------
# ADMIN DASHBOARD
# ------------------------------------------------------------

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin():
        flash('Access denied. Admins only.')
        return redirect(url_for('auth.login'))
    
    # Get system statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role=UserRole.STUDENT).count()
    total_lecturers = User.query.filter_by(role=UserRole.LECTURER).count()
    total_admins = User.query.filter_by(role=UserRole.ADMIN).count()
    
    # Payment statistics
    total_payments = Payment.query.count()
    completed_payments = Payment.query.filter_by(status='completed').count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == 'completed'
    ).scalar() or 0
    
    # Recent activities
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_students=total_students,
                         total_lecturers=total_lecturers,
                         total_admins=total_admins,
                         total_payments=total_payments,
                         completed_payments=completed_payments,
                         total_revenue=total_revenue,
                         recent_payments=recent_payments,
                         recent_users=recent_users)

# ------------------------------------------------------------
# USER MANAGEMENT
# ------------------------------------------------------------

@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/students')
@login_required
def students():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    all_students = User.query.filter_by(role=UserRole.STUDENT).all()
    return render_template('admin/students.html', students=all_students)

@admin_bp.route('/lecturers')
@login_required
def lecturers():
    if not current_user.is_admin():
        flash('Access denied. Admins only.')
        return redirect(url_for('auth.login'))
    
    all_lecturers = User.query.filter_by(role=UserRole.LECTURER).all()
    return render_template('admin/lecturers.html', lecturers=all_lecturers)

@admin_bp.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    if not current_user.is_admin():
        flash('Access denied. Admins only.')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)
    user_payments = Payment.query.filter_by(user_id=user_id).all()
    user_results = Result.query.filter_by(user_id=user_id).all()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         payments=user_payments,
                         results=user_results)

@admin_bp.route('/user/toggle_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activated" if user.is_active else "deactivated"
        return jsonify({'success': True, 'message': f'User {status} successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# ------------------------------------------------------------
# PAYMENT MANAGEMENT
# ------------------------------------------------------------

@admin_bp.route('/payments')
@login_required
def payments():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    all_payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    
    # Calculate statistics
    total_revenue = sum(p.amount for p in all_payments if p.status == 'completed')
    pending_amount = sum(p.amount for p in all_payments if p.status == 'pending')
    
    return render_template('admin/payments.html',
                         payments=all_payments,
                         total_revenue=total_revenue,
                         pending_amount=pending_amount)

@admin_bp.route('/payment/update_status/<int:payment_id>', methods=['POST'])
@login_required
def update_payment_status(payment_id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'message': 'Payment not found'})
        
        new_status = request.json.get('status')
        if new_status not in ['pending', 'completed', 'failed', 'cancelled']:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        payment.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Payment status updated to {new_status}'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# ------------------------------------------------------------
# RESULTS MANAGEMENT
# ------------------------------------------------------------

@admin_bp.route('/results')
@login_required
def results_management():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    all_results = Result.query.order_by(Result.academic_year.desc(), Result.semester.desc()).all()
    
    # Get unique academic years and semesters for filtering
    academic_years = db.session.query(Result.academic_year).distinct().all()
    semesters = db.session.query(Result.semester).distinct().all()
    
    return render_template('admin/results_management.html',
                         results=all_results,
                         academic_years=academic_years,
                         semesters=semesters)

@admin_bp.route('/results/filter', methods=['POST'])
@login_required
def filter_results():
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    academic_year = request.json.get('academic_year')
    semester = request.json.get('semester')
    course_code = request.json.get('course_code')
    
    query = Result.query
    
    if academic_year:
        query = query.filter_by(academic_year=academic_year)
    if semester:
        query = query.filter_by(semester=semester)
    if course_code:
        query = query.filter_by(course_code=course_code)
    
    filtered_results = query.all()
    
    results_data = [{
        'id': result.id,
        'student_name': f"{result.user.first_name} {result.user.last_name}",
        'student_id': result.user.student_id,
        'course_code': result.course_code,
        'course_name': result.course_name,
        'grade': result.grade,
        'marks': result.marks,
        'semester': result.semester,
        'academic_year': result.academic_year
    } for result in filtered_results]
    
    return jsonify({'results': results_data})

# ------------------------------------------------------------
# COURSE MANAGEMENT
# ------------------------------------------------------------

@admin_bp.route('/courses')
@login_required
def courses():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    # If you still have a Course model, import and use it
    try:
        from models.course import Course
        all_courses = Course.query.all()
        return render_template('admin/courses.html', courses=all_courses)
    except ImportError:
        # If Course model doesn't exist yet, pass empty list
        return render_template('admin/courses.html', courses=[])

# ------------------------------------------------------------
# SYSTEM REPORTS
# ------------------------------------------------------------

@admin_bp.route('/reports')
@login_required
def reports():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    # User registration trends (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_registrations = User.query.filter(
        User.created_at >= thirty_days_ago
    ).count()
    
    # Payment trends
    recent_payments = Payment.query.filter(
        Payment.payment_date >= thirty_days_ago
    ).count()
    
    recent_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.payment_date >= thirty_days_ago,
        Payment.status == 'completed'
    ).scalar() or 0
    
    # Grade distribution
    grade_distribution = db.session.query(
        Result.grade,
        db.func.count(Result.id)
    ).group_by(Result.grade).all()
    
    return render_template('admin/reports.html',
                         recent_registrations=recent_registrations,
                         recent_payments=recent_payments,
                         recent_revenue=recent_revenue,
                         grade_distribution=grade_distribution)

# ------------------------------------------------------------
# API ENDPOINTS FOR DASHBOARD CHARTS
# ------------------------------------------------------------

@admin_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats_api():
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    # User role distribution
    role_distribution = {
        'students': User.query.filter_by(role=UserRole.STUDENT).count(),
        'lecturers': User.query.filter_by(role=UserRole.LECTURER).count(),
        'admins': User.query.filter_by(role=UserRole.ADMIN).count()
    }
    
    # Payment status distribution
    payment_status_distribution = {
        'completed': Payment.query.filter_by(status='completed').count(),
        'pending': Payment.query.filter_by(status='pending').count(),
        'failed': Payment.query.filter_by(status='failed').count()
    }
    
    # Monthly revenue (last 6 months)
    from datetime import datetime, timedelta
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    monthly_revenue = db.session.query(
        db.func.strftime('%Y-%m', Payment.payment_date),
        db.func.sum(Payment.amount)
    ).filter(
        Payment.status == 'completed',
        Payment.payment_date >= six_months_ago
    ).group_by(db.func.strftime('%Y-%m', Payment.payment_date)).all()
    
    return jsonify({
        'role_distribution': role_distribution,
        'payment_status_distribution': payment_status_distribution,
        'monthly_revenue': dict(monthly_revenue)
    })

# ------------------------------------------------------------
# SYSTEM SETTINGS
# ------------------------------------------------------------

@admin_bp.route('/settings')
@login_required
def settings():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('admin/settings.html')