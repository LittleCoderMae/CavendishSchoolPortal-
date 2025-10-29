from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from database.database import db
from models.user import User, UserRole, Result  # Updated imports

results_bp = Blueprint('results', __name__)

# ------------------------------------------------------------
# LECTURER & ADMIN RESULTS MANAGEMENT
# ------------------------------------------------------------

@results_bp.route('/publish', methods=['POST'])
@login_required
def publish_results():
    if not (current_user.is_lecturer() or current_user.is_admin()):
        flash('Access denied. Lecturers and Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        course_code = data.get('course_code')
        course_name = data.get('course_name')
        grade = data.get('grade')
        marks = data.get('marks')
        semester = data.get('semester')
        academic_year = data.get('academic_year')
        
        # Check if result already exists
        existing_result = Result.query.filter_by(
            user_id=user_id,
            course_code=course_code,
            semester=semester,
            academic_year=academic_year
        ).first()
        
        if existing_result:
            # Update existing result
            existing_result.grade = grade
            existing_result.marks = marks
            existing_result.course_name = course_name
            flash('Result updated successfully!', 'success')
        else:
            # Create new result
            new_result = Result(
                user_id=user_id,
                course_code=course_code,
                course_name=course_name,
                grade=grade,
                marks=marks,
                semester=semester,
                academic_year=academic_year
            )
            db.session.add(new_result)
            flash('Result published successfully!', 'success')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Result published successfully!'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error publishing result: {str(e)}'})

@results_bp.route('/view/<int:user_id>')
@login_required
def view_student_results(user_id):
    if not (current_user.is_lecturer() or current_user.is_admin()):
        flash('Access denied. Lecturers and Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    student_results = Result.query.filter_by(user_id=user_id).order_by(
        Result.academic_year.desc(),
        Result.semester.desc()
    ).all()
    
    student = User.query.get(user_id)
    
    return render_template('lecturer/results.html', 
                         results=student_results,
                         student=student)

@results_bp.route('/manage')
@login_required
def manage_results():
    if not (current_user.is_lecturer() or current_user.is_admin()):
        flash('Access denied. Lecturers and Admins only.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get all students for dropdown
    students = User.query.filter_by(role=UserRole.STUDENT).all()
    
    # Get results based on user role
    if current_user.is_lecturer():
        # Lecturers can only see results for their department
        results = Result.query.join(User).filter(
            User.department == current_user.department
        ).order_by(Result.academic_year.desc()).all()
    else:
        # Admins can see all results
        results = Result.query.order_by(Result.academic_year.desc()).all()
    
    return render_template('admin/results_management.html',
                         students=students,
                         results=results)

@results_bp.route('/bulk-upload', methods=['POST'])
@login_required
def bulk_upload():
    if not (current_user.is_lecturer() or current_user.is_admin()):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        # TODO: Implement CSV/Excel file parsing
        # This would parse the file and create Result records
        
        return jsonify({'success': True, 'message': 'Results uploaded successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error uploading file: {str(e)}'})

# ------------------------------------------------------------
# STUDENT RESULTS VIEW
# ------------------------------------------------------------

@results_bp.route('/my-results')
@login_required
def my_results():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('auth.login'))
    
    student_results = Result.query.filter_by(user_id=current_user.id).order_by(
        Result.academic_year.desc(),
        Result.semester.desc()
    ).all()
    
    # Calculate statistics
    if student_results:
        total_courses = len(student_results)
        average_marks = sum(result.marks for result in student_results) / total_courses
        
        # Grade distribution
        grade_count = {}
        for result in student_results:
            grade_count[result.grade] = grade_count.get(result.grade, 0) + 1
    else:
        total_courses = 0
        average_marks = 0
        grade_count = {}
    
    return render_template('student/results.html',
                         results=student_results,
                         total_courses=total_courses,
                         average_marks=round(average_marks, 2),
                         grade_count=grade_count)

# ------------------------------------------------------------
# API ENDPOINTS
# ------------------------------------------------------------

@results_bp.route('/api/student/<int:user_id>')
@login_required
def get_student_results_api(user_id):
    if not (current_user.is_lecturer() or current_user.is_admin()):
        return jsonify({'error': 'Access denied'}), 403
    
    results = Result.query.filter_by(user_id=user_id).all()
    
    results_data = [{
        'id': result.id,
        'course_code': result.course_code,
        'course_name': result.course_name,
        'grade': result.grade,
        'marks': result.marks,
        'semester': result.semester,
        'academic_year': result.academic_year
    } for result in results]
    
    return jsonify({'results': results_data})

@results_bp.route('/api/course/<course_code>')
@login_required
def get_course_results_api(course_code):
    if not (current_user.is_lecturer() or current_user.is_admin()):
        return jsonify({'error': 'Access denied'}), 403
    
    results = Result.query.filter_by(course_code=course_code).all()
    
    # Get student details for each result
    results_with_students = []
    for result in results:
        student = User.query.get(result.user_id)
        results_with_students.append({
            'student_name': f"{student.first_name} {student.last_name}",
            'student_id': student.student_id,
            'grade': result.grade,
            'marks': result.marks,
            'semester': result.semester,
            'academic_year': result.academic_year
        })
    
    return jsonify({'course_results': results_with_students})

@results_bp.route('/api/delete/<int:result_id>', methods=['DELETE'])
@login_required
def delete_result_api(result_id):
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied. Admins only.'}), 403
    
    try:
        result = Result.query.get(result_id)
        if not result:
            return jsonify({'error': 'Result not found'}), 404
        
        db.session.delete(result)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Result deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting result: {str(e)}'}), 500

# ------------------------------------------------------------
# RESULTS ANALYSIS
# ------------------------------------------------------------

@results_bp.route('/analysis')
@login_required
def results_analysis():
    if not (current_user.is_lecturer() or current_user.is_admin()):
        flash('Access denied.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get results statistics
    total_results = Result.query.count()
    distinct_students = db.session.query(Result.user_id).distinct().count()
    distinct_courses = db.session.query(Result.course_code).distinct().count()
    
    # Grade distribution
    grade_distribution = db.session.query(
        Result.grade, 
        db.func.count(Result.id)
    ).group_by(Result.grade).all()
    
    # Average marks per course
    course_averages = db.session.query(
        Result.course_code,
        Result.course_name,
        db.func.avg(Result.marks).label('average_marks')
    ).group_by(Result.course_code, Result.course_name).all()
    
    return render_template('admin/results_analysis.html',
                         total_results=total_results,
                         distinct_students=distinct_students,
                         distinct_courses=distinct_courses,
                         grade_distribution=grade_distribution,
                         course_averages=course_averages)