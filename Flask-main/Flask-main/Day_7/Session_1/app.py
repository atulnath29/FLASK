from flask import Flask, render_template, request, session, redirect, url_for
from functools import wraps

secret_key = 'your_secret_key'

app = Flask(__name__)
app.secret_key = secret_key

def check_user(func):
    @wraps(func)
    def wrapper(name):
        if name == 'admin':
            return "Access Denied"
        return func(name)
    return wrapper

@app.route('/')
def home():
    return "Home"

@app.route('/login/<name>')
def login(name):
    if name == 'admin':
        session ['user'] = name
        return redirect(url_for('dashboard'))
    return "Invalid user"

@app.route('/dashboard')
def dashboard():
    if "user" in session:
        user = session.get('user')
        return f"dashboard for {user}"
    return "No current user"

@app.route('/logout')
def logout():
    session.pop('user')
    return f"session closed"

if __name__ == '__main__':
    app.run(debug=True)