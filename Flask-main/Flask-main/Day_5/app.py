from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

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
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def index():
    return "Flask + SQLAlchemy Running"


@app.route('/add')
def add():
    user = User(
        username='Ayush',
        role='Student',
        email='ayush123@gmail.com'
    )
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Email {user.email} already exists. Please use a different email."
    return f"User {user.username} added successfully"

@app.route('/show_f')
def show_f():
    users = User.query.filter(User.email.like('%@gmail.com')).all()
    return render_template('index.html', users=users)

@app.route('/show_all')
def show_all():
    #users = User.query.all()
    users = User.query.order_by(desc(User.id)).all()
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

@app.route('/show_user')
def show_user():
    users = User.query.filter(User.username.like('A%')).all()
    return render_template('index.html', users=users)

@app.route('/count')
def count():
    user_count = User.query.count()
    return f"Total number of users: {user_count}"

#---------------------------------------------------------

@app.route('/post')
def post():
    user = User(username = "Abhi", email = "abhi@gmail.com", role = "Student")
    db.session.add(user)
    db.session.commit()
    post = Post(title='Fourth Post', content='This is the content of the Fourth post.', user_id=user.id)
    db.session.add(post)
    db.session.commit()
    return f"Post '{post.title}' added for user {user.username}"

@app.route('/post_by/<name>')
def post_by(name):
    user = User.query.filter(User.username == name).first()
    if user:
        post = Post(title='User Post', content=f'This post is created by {user.username}', user_id=user.id)
        db.session.add(post)
        db.session.commit()
        return f"Post '{post.title}' added for user {user.username}"
    else:
        return f"No user found with username {name}"

@app.route('/show_post')
def show_post():
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(Post, User).join(User, Post.user_id == User.id).paginate(page=page, per_page=2).items
    print(posts)
    for post, user in posts:
        print(f" {post.title} by {user.username}")
    return render_template('post.html', posts=posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)