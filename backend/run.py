from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Create the Flask app
app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = "bosto-primary-school-secret-key-2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///school.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Database Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20), default="student")  # student, teacher, admin
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create database tables and add sample data
with app.app_context():
    db.create_all()

    # Create admin user if not exists
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@bostoschool.com",
            full_name="School Administrator",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

        # Create a sample teacher
        teacher = User(
            username="teacher1",
            email="teacher@bostoschool.com",
            full_name="Jane Smith",
            role="teacher",
        )
        teacher.set_password("teacher123")
        db.session.add(teacher)

        # Create a sample student
        student = User(
            username="student1",
            email="student@bostoschool.com",
            full_name="John Doe",
            role="student",
        )
        student.set_password("student123")
        db.session.add(student)

        db.session.commit()
        print("=" * 50)
        print("Demo accounts created!")
        print("Admin - username: admin, password: admin123")
        print("Teacher - username: teacher1, password: teacher123")
        print("Student - username: student1, password: student123")
        print("=" * 50)


# Routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "teacher":
                return redirect(url_for("teacher_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("home"))


@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied", "error")
        return redirect(url_for("home"))

    # Get statistics
    total_students = User.query.filter_by(role="student").count()
    total_teachers = User.query.filter_by(role="teacher").count()

    return render_template(
        "admin_dashboard.html",
        students_count=total_students,
        teachers_count=total_teachers,
    )


@app.route("/teacher-dashboard")
@login_required
def teacher_dashboard():
    if current_user.role != "teacher":
        flash("Access denied", "error")
        return redirect(url_for("home"))
    return render_template("teacher_dashboard.html")


@app.route("/student-dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        flash("Access denied", "error")
        return redirect(url_for("home"))
    return render_template("student_dashboard.html")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 Bosto Primary School Website Starting...")
    print("=" * 50)
    print("📍 Access at: http://127.0.0.1:5000")
    print("📍 Access at: http://localhost:5000")
    print("=" * 50)
    print("Demo Accounts:")
    print("  👑 Admin: admin / admin123")
    print("  👩‍🏫 Teacher: teacher1 / teacher123")
    print("  👨‍🎓 Student: student1 / student123")
    print("=" * 50 + "\n")

    app.run(debug=True, host="127.0.0.1", port=5000)
