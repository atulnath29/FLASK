from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    session['msg'] = "Registration Successful!"
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return render_template("login.html", msg=session.pop('msg', None))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        session['user'] = user.name
        return redirect(url_for('dashboard'))
    else:
        return "Invalid login"

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", user=session['user'])
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

if __name__ == "__main__":
    app.run(debug=True)
