# routes/results.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

results_bp = Blueprint('results', __name__)

@results_bp.route('/publish', methods=['POST'])
@login_required
def publish_results():
    if current_user.role not in ['admin', 'lecturer']:
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    # Implementation for publishing results
    pass

@results_bp.route('/view/<int:student_id>')
@login_required
def view_student_results(student_id):
    if current_user.role not in ['admin', 'lecturer']:
        flash('Access denied', 'error')
        return redirect(url_for('auth.login'))
    
    from models.result import Result
    student_results = Result.query.filter_by(student_id=student_id).all()
    return render_template('lecturer/results.html', results=student_results)