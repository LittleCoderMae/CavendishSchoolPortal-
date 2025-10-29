# routes/lecturer.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import User, UserRole

lecturer_bp = Blueprint('lecturer', __name__)

@lecturer_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_lecturer():
        flash('Access denied. Lecturers only.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('lecturer/dashboard.html', user=current_user)

@lecturer_bp.route('/students')
@login_required
def students():
    if not current_user.is_lecturer():
        flash('Access denied. Lecturers only.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get all students (you can filter by department later)
    students = User.query.filter_by(role=UserRole.STUDENT).all()
    return render_template('lecturer/students.html', 
                         students=students,
                         user=current_user)

@lecturer_bp.route('/results')
@login_required
def results():
    if not current_user.is_lecturer():
        flash('Access denied. Lecturers only.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('lecturer/results.html', user=current_user)

@lecturer_bp.route('/profile')
@login_required
def profile():
    if not current_user.is_lecturer():
        flash('Access denied. Lecturers only.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('lecturer/profile.html', user=current_user)