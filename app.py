from datetime import date, datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

app.config["SECRET_KEY"] = "change-this-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scheduler.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# DATABASE MODELS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    tasks = db.relationship(
        "Task",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    task_date = db.Column(
        db.Date,
        nullable=False
    )

    task_time = db.Column(
        db.Time,
        nullable=True
    )

    completed = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


# =========================
# AUTHENTICATION
# =========================

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# =========================
# HOME
# =========================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id
            session["username"] = user.username

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
@login_required
def dashboard():

    selected_date = request.args.get(
        "date",
        date.today().isoformat()
    )

    try:
        selected_date_obj = date.fromisoformat(selected_date)
    except ValueError:
        selected_date_obj = date.today()

    tasks = Task.query.filter_by(
        user_id=session["user_id"],
        task_date=selected_date_obj
    ).order_by(
        Task.task_time.asc()
    ).all()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        selected_date=selected_date_obj
    )


# =========================
# ADD TASK
# =========================

@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    task_date = request.form.get("task_date")
    task_time = request.form.get("task_time")

    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("dashboard"))

    try:
        task_date_obj = date.fromisoformat(task_date)

    except (ValueError, TypeError):
        flash("Invalid date.", "error")
        return redirect(url_for("dashboard"))

    task_time_obj = None

    if task_time:
        try:
            task_time_obj = datetime.strptime(
                task_time,
                "%H:%M"
            ).time()

        except ValueError:
            flash("Invalid time.", "error")
            return redirect(url_for("dashboard"))

    task = Task(
        title=title,
        description=description,
        task_date=task_date_obj,
        task_time=task_time_obj,
        user_id=session["user_id"]
    )

    db.session.add(task)
    db.session.commit()

    return redirect(
        url_for(
            "dashboard",
            date=task_date
        )
    )


# =========================
# COMPLETE / UNCOMPLETE
# =========================

@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):

    task = Task.query.filter_by(
        id=task_id,
        user_id=session["user_id"]
    ).first_or_404()

    task.completed = not task.completed

    db.session.commit()

    return redirect(
        url_for(
            "dashboard",
            date=task.task_date.isoformat()
        )
    )


# =========================
# DELETE TASK
# =========================

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):

    task = Task.query.filter_by(
        id=task_id,
        user_id=session["user_id"]
    ).first_or_404()

    task_date = task.task_date.isoformat()

    db.session.delete(task)
    db.session.commit()

    return redirect(
        url_for(
            "dashboard",
            date=task_date
        )
    )


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    })


# =========================
# CREATE DATABASE
# =========================

with app.app_context():
    db.create_all()


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )