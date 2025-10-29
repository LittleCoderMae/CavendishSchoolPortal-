from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db
from models.user import User
from models.student import Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not email or not password or not role:
            flash('Please fill in all fields', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email, role=role).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect_by_role(user.role)
        else:
            flash('Invalid email, password, or role selection', 'error')

    return render_template('auth/login.html')

def redirect_by_role(role):
    if role == 'student':
        return redirect(url_for('student.dashboard'))
    elif role == 'lecturer':
        return redirect(url_for('lecturer.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        program = request.form.get('program')
        year_of_study = request.form.get('year_of_study')
        semester = request.form.get('semester')

        if not all([username, email, password, confirm_password]):
            flash('Please fill in all required fields', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('auth/register.html')

        if role == 'student':
            if not all([first_name, last_name, program, year_of_study, semester]):
                flash('Please fill in all student details', 'error')
                return render_template('auth/register.html')

        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role=role
            )
            db.session.add(user)
            db.session.flush()

            if role == 'student':
                student = Student(
                    user_id=user.id,
                    student_id=f"S{user.id:06d}",
                    first_name=first_name,
                    last_name=last_name,
                    program=program,
                    year_of_study=int(year_of_study),
                    semester=int(semester)
                )
                db.session.add(student)

            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash('Error during registration, please try again.', 'error')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/create-demo-users')
def create_demo_users():
    try:
        # Delete existing demo users first
        demo_emails = ['student@cuz.ac.zm', 'lecturer@cuz.ac.zm', 'admin@cuz.ac.zm']
        existing_users = User.query.filter(User.email.in_(demo_emails)).all()
        for user in existing_users:
            db.session.delete(user)
        db.session.commit()

        # Create demo student
        student_user = User(
            username='demo_student',
            email='student@cuz.ac.zm',
            password_hash=generate_password_hash('password123'),
            role='student'
        )
        db.session.add(student_user)
        db.session.flush()

        student_profile = Student(
            user_id=student_user.id,
            student_id=f"S{student_user.id:06d}",
            first_name='John',
            last_name='Smith',
            program='Computer Science',
            year_of_study=2,
            semester=1
        )
        db.session.add(student_profile)

        # Create demo lecturer
        lecturer_user = User(
            username='demo_lecturer',
            email='lecturer@cuz.ac.zm',
            password_hash=generate_password_hash('password123'),
            role='lecturer'
        )
        db.session.add(lecturer_user)

        # Create demo admin
        admin_user = User(
            username='demo_admin',
            email='admin@cuz.ac.zm',
            password_hash=generate_password_hash('password123'),
            role='admin'
        )
        db.session.add(admin_user)

        db.session.commit()
        flash('Demo users created successfully! You can now login with the demo credentials.', 'success')
        return redirect(url_for('auth.login'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating demo users: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/debug-users')
def debug_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'password_hash': user.password_hash
        })
    return {'users': result}