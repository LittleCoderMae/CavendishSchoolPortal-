from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db
from models.user import User, UserRole

auth_bp = Blueprint('auth', __name__)

# ------------------------------------------------------------
# REDIRECT BY ROLE (Helper function - should be above routes)
# ------------------------------------------------------------
def redirect_by_role(role):
    if role == 'student':
        return redirect(url_for('student.dashboard'))
    elif role == 'lecturer':
        return redirect(url_for('lecturer.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

# ------------------------------------------------------------
# LOGIN ROUTE
# ------------------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role.value)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not email or not password or not role:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        # Debug logging (remove in production)
        print(f"Login attempt: {email} as {role}")
        if user:
            print(f"User found: {user.email}, actual role: {user.role.value}")
            print(f"Password check: {check_password_hash(user.password_hash, password)}")
            print(f"Role match: {user.role.value == role}")

        if not user:
            flash('No account found with that email.', 'error')
        elif user.role.value != role:
            flash(f'Incorrect role selected. This email is registered as a {user.role.value}.', 'error')
        elif not check_password_hash(user.password_hash, password):
            flash('Invalid password.', 'error')
        elif not user.is_active:
            flash('Account is deactivated. Please contact administrator.', 'error')
        else:
            login_user(user, remember=True)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect_by_role(user.role.value)

    return render_template('auth/login.html')
# ------------------------------------------------------------
# REGISTER ROUTE
# ------------------------------------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role.value)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        # Role-specific fields
        program = request.form.get('program')
        year_of_study = request.form.get('year_of_study')
        staff_id = request.form.get('staff_id')
        department = request.form.get('department')

        # --- Validations ---
        if not all([email, password, confirm_password, first_name, last_name]):
            flash('Please fill in all required fields.', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('auth/register.html')

        # Role-specific validations
        if role == 'student' and not program:
            flash('Please select a program for student registration.', 'error')
            return render_template('auth/register.html')

        if role == 'lecturer' and not all([staff_id, department]):
            flash('Please fill in all lecturer details.', 'error')
            return render_template('auth/register.html')

        # --- User creation with single model ---
        try:
            # Convert role string to Enum
            user_role = UserRole(role)
            
            # Create user
            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                role=user_role
            )

            # Add role-specific data
            if role == 'student':
                user.program = program
                user.year_of_study = int(year_of_study) if year_of_study else None
                user.student_id = f"S{User.query.count() + 1:06d}"  # Generate student ID
            elif role == 'lecturer':
                user.staff_id = staff_id
                user.department = department

            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except ValueError:
            flash('Invalid role selected.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'error')

    return render_template('auth/register.html')

# ------------------------------------------------------------
# LOGOUT ROUTE
# ------------------------------------------------------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# ------------------------------------------------------------
# CREATE DEMO USERS ROUTE
# ------------------------------------------------------------
@auth_bp.route('/create-demo-users')
def create_demo_users():
    try:
        demo_emails = ['student@cuz.ac.zm', 'lecturer@cuz.ac.zm', 'admin@cuz.ac.zm']

        # Delete existing demo users first
        existing_users = User.query.filter(User.email.in_(demo_emails)).all()
        for user in existing_users:
            db.session.delete(user)
        db.session.commit()

        # --- Create demo student ---
        student_user = User(
            email='student@cuz.ac.zm',
            password_hash=generate_password_hash('password123'),
            first_name='John',
            last_name='Smith',
            role=UserRole.STUDENT,
            program='Computer Science',
            year_of_study=2,
            student_id='S000001'
        )
        db.session.add(student_user)

        # --- Create demo lecturer ---
        lecturer_user = User(
            email='lecturer@cuz.ac.zm',
            password_hash=generate_password_hash('password123'),
            first_name='Dr. Sarah',
            last_name='Johnson',
            role=UserRole.LECTURER,
            staff_id='L000001',
            department='Computer Science'
        )
        db.session.add(lecturer_user)

        # --- Create demo admin ---
        admin_user = User(
            email='admin@cuz.ac.zm',
            password_hash=generate_password_hash('password123'),
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN
        )
        db.session.add(admin_user)

        db.session.commit()
        flash('Demo users created successfully! You can now login with the demo credentials.', 'success')
        return redirect(url_for('auth.login'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating demo users: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

# ------------------------------------------------------------
# DEBUG ROUTE FOR ADMIN USE
# ------------------------------------------------------------
@auth_bp.route('/debug-users')
def debug_users():
    users = User.query.all()
    result = [{
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role.value,
        'student_id': user.student_id,
        'staff_id': user.staff_id,
        'program': user.program,
        'is_active': user.is_active
    } for user in users]
    return jsonify({'users': result})

# ------------------------------------------------------------
# TEST ROUTE - To check if auth routes are working
# ------------------------------------------------------------
@auth_bp.route('/test')
def test_auth():
    return jsonify({'message': 'Auth routes are working!'})