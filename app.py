from flask import Flask, render_template
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

# Import configuration
from config import DevelopmentConfig

# Create app FIRST
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Initialize database
from database.database import db
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# User loader
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

# Register blueprints
def register_blueprints():
    try:
        from routes.auth import auth_bp
        from routes.student import student_bp
        from routes.lecturer import lecturer_bp
        from routes.admin import admin_bp
        from routes.payment import payment_bp
        from routes.results import results_bp
        from routes.chatbot import chatbot_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(student_bp, url_prefix='/student')
        app.register_blueprint(lecturer_bp, url_prefix='/lecturer')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(payment_bp, url_prefix='/payment')
        app.register_blueprint(results_bp, url_prefix='/results')
        app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
        
        print("✅ All blueprints registered successfully")
    except Exception as e:
        print(f"❌ Error registering blueprints: {e}")

# Basic routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

# Context processor
@app.context_processor
def inject_template_variables():
    from models.user import UserRole
    return dict(
        current_user=current_user,
        UserRole=UserRole
    )

# Create demo users
def create_demo_users():
    with app.app_context():
        try:
            from models.user import User, UserRole
            
            # Create tables first
            db.create_all()
            
            # Create default admin user if doesn't exist
            admin_user = User.query.filter_by(email='admin@cavendish.edu.zm').first()
            if not admin_user:
                admin_user = User(
                    email='admin@cavendish.edu.zm',
                    password_hash=generate_password_hash('admin123'),
                    first_name='System',
                    last_name='Administrator',
                    role=UserRole.ADMIN
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created: admin@cavendish.edu.zm / admin123")
            
            # Create demo student if doesn't exist
            demo_student = User.query.filter_by(email='student@cavendish.edu.zm').first()
            if not demo_student:
                demo_student = User(
                    email='student@cavendish.edu.zm',
                    password_hash=generate_password_hash('password123'),
                    first_name='John',
                    last_name='Doe',
                    role=UserRole.STUDENT,
                    student_id='S2024001',
                    program='Computer Science',
                    year_of_study=2
                )
                db.session.add(demo_student)
                db.session.commit()
                print("✅ Demo student created: student@cavendish.edu.zm / password123")
            
            # Create demo lecturer if doesn't exist
            demo_lecturer = User.query.filter_by(email='lecturer@cavendish.edu.zm').first()
            if not demo_lecturer:
                demo_lecturer = User(
                    email='lecturer@cavendish.edu.zm',
                    password_hash=generate_password_hash('password123'),
                    first_name='Dr. Sarah',
                    last_name='Johnson',
                    role=UserRole.LECTURER,
                    staff_id='L2024001',
                    department='Computer Science'
                )
                db.session.add(demo_lecturer)
                db.session.commit()
                print("✅ Demo lecturer created: lecturer@cavendish.edu.zm / password123")
                
        except Exception as e:
            print(f"❌ Error creating demo users: {str(e)}")

# Initialize the app
with app.app_context():
    register_blueprints()
    create_demo_users()

if __name__ == '__main__':
    print("🚀 Starting Cavendish School Portal...")
    print("📍 Access the application at: http://localhost:5000")
    print("🔑 Login URL: http://localhost:5000/auth/login")
    print("")
    print("👤 Demo Credentials:")
    print("   Admin: admin@cavendish.edu.zm / admin123")
    print("   Student: student@cavendish.edu.zm / password123")
    print("   Lecturer: lecturer@cavendish.edu.zm / password123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)