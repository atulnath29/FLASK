from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route('/')
def index():
    search_text = request.args.get('search_text')
    if search_text:
        return f'Searching for: {search_text}'
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", user=session['user'])
    else:
        return redirect(url_for('index'))

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    return f'Thank you, {name}! Your email {email} has been received.'

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'Ayush' and password == 'password':
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid credentials. Please try again.'

@app.route('/logout')
def logout():
    session.pop('user', None)
    return 'You have been logged out'

if __name__ == '__main__':
    app.run(debug=True)
