# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database.database import db
from models.user import User
from models.student import Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard' if current_user.role == 'student' else 'admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password_hash == password:  # In real app, use proper password hashing
            login_user(user)
            flash('Login successful!', 'success')
            
            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'lecturer':
                return redirect(url_for('lecturer.dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('auth/register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=password,  # In real app, hash this password
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        if role == 'student':
            # Create student profile
            student = Student(
                user_id=user.id,
                student_id=f"S{user.id:06d}",
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                program=request.form.get('program'),
                year_of_study=int(request.form.get('year_of_study', 1)),
                semester=int(request.form.get('semester', 1))
            )
            db.session.add(student)
            db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))