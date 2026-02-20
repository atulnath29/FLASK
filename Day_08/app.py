from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "Admin":
            return "<h2 style='color:red;text-align:center'>Access Denied : Admin Only</h2>"
        return f(*args, **kwargs)
    return wrapper

def init_db():
    with app.app_context():
        db.create_all()

        if User.query.count() == 0:
            users = [
                User(username="admin", email="admin@gmail.com", password="admin123", role="Admin"),
                User(username="editor", email="editor@gmail.com", password="editor123", role="Editor"),
                User(username="user", email="user@gmail.com", password="user123", role="User"),
            ]
            db.session.add_all(users)
            db.session.commit()

        if Task.query.count() == 0:
            tasks = [
                Task(title="Prepare Report", status="Pending", user_id=1),
                Task(title="Fix Website Bug", status="Completed", user_id=1),
                Task(title="Update Database", status="Pending", user_id=2),
            ]
            db.session.add_all(tasks)
            db.session.commit()

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            session["user"] = user.username
            session["role"] = user.role
            return redirect(url_for("dashboard"))

        flash("Invalid Credentials")

    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= DASHBOARD =================
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html",
                           username=session["user"],
                           role=session["role"])

# ================= USERS (ADMIN) =================
@app.route("/users")
@admin_required
def view_users():
    users = User.query.all()
    return render_template("users.html", users=users, username=session["user"])

# ================= ADD USER =================
@app.route("/add_user", methods=["GET","POST"])
@admin_required
def add_user():
    if request.method == "POST":
        new_user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=request.form["password"],
            role=request.form["role"]
        )
        db.session.add(new_user)
        db.session.commit()
        flash("User Added Successfully")
        return redirect(url_for("view_users"))

    return render_template("add_user.html")

# ================= EDIT USER =================
@app.route("/edit_user/<int:id>", methods=["GET","POST"])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == "POST":
        user.username = request.form["username"]
        user.email = request.form["email"]
        user.password = request.form["password"]
        user.role = request.form["role"]
        db.session.commit()
        flash("User Updated Successfully")
        return redirect(url_for("view_users"))

    return render_template("edit_user.html", user=user)

# ================= DELETE USER =================
@app.route("/delete_user/<int:id>")
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)

    if user.username == session["user"]:
        flash("You cannot delete yourself!")
        return redirect(url_for("view_users"))

    db.session.delete(user)
    db.session.commit()
    flash("User Deleted Successfully")
    return redirect(url_for("view_users"))

# ================= TASKS =================
@app.route("/tasks")
@login_required
def view_tasks():
    tasks = Task.query.all()
    return render_template("tasks.html", tasks=tasks)

# ================= TOGGLE TASK STATUS =================
@app.route("/toggle_task/<int:id>")
@admin_required
def toggle_task(id):
    task = Task.query.get_or_404(id)
    task.status = "Completed" if task.status == "Pending" else "Pending"
    db.session.commit()
    return redirect(url_for("view_tasks"))

# ================= RUN APP =================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
