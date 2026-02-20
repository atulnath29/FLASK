from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


@app.route('/')
def index():
    return "Flask + SQLAlchemy Running"


@app.route('/add')
def add():
    user = User(
        username='Adil',
        role='Teacher',
        email='adil123@gmail.com'
    )
    db.session.add(user)
    db.session.commit()
    return f"User {user.username} added successfully"

@app.route('/show_f')
def show_f():
    users = User.query.filter(User.email.like('%@gmail.com')).all()
    return render_template('index.html', users=users)

@app.route('/show_all')
def show_all():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/update/<int:id>/<name>')
def update(id, name):
    user = User.query.get(id)
    user.username = name
    db.session.commit()
    return f"User updated to {user.username}"

@app.route('/delete/<int:id>')
def delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return f"User deleted successfully"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)