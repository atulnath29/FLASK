from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

@app.route('/')
def home():
    return "home"

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()
    return 'User added successfully!'

@app.route('/add_admin', methods=['POST'])
def add_admin():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    new_admin = User(name=name, email=email, role='admin', password=password)
    db.session.add(new_admin)
    db.session.commit()
    return f'Admin created with email = {email} and password = {password}'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session["user"] = User.query.filter_by(email=email, password=password).first()
        user = session["user"]
        if user:
            return f'Welcome {user.name}!'
        else:
            return 'Invalid credentials. Please try again.'
    return render_template('login.html')

@app.route('/task')
def task():
    user = session.get("user")
    if user:
        return f'Welcome {user.name}! You are on the task page.'
    else:
        return 'Please log in first.'
    
@app.route('/user')
def user():
    user = session.get("user")
    if user:
        return f'User Information: {user.name}, Email: {user.email}, Role: {user.role}'
    else:
        return 'Please log in first.'

@app.route('/logout')
def logout():
    session.pop("user", None)
    return 'Logged out successfully!'

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)