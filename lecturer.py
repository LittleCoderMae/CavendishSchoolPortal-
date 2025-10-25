# lecturer.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

lecturer_bp = Blueprint('lecturer', __name__, url_prefix='/lecturer')

@lecturer_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'lecturer':
        flash('Access denied. Lecturer access required.', 'error')
        return redirect(url_for('index'))
    return render_template('lecturer/dashboard.html')

@lecturer_bp.route('/results')
@login_required
def results():
    if current_user.role != 'lecturer':
        flash('Access denied. Lecturer access required.', 'error')
        return redirect(url_for('index'))
    return render_template('lecturer/results.html')