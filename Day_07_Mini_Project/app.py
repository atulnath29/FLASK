from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(50))



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    author = db.Column(db.String(50))



@app.route("/")
def home():
    return render_template("home.html")



@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        user = User(username=username, email=email, password=password)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session["user"] = user.username
            return redirect(url_for("create_post"))

        return "Invalid Username or Password"

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))



@app.route("/view")
def view_post():

    posts = Post.query.all()
    return render_template("view.html", posts=posts)



@app.route("/create", methods=["GET", "POST"])
def create_post():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        post = Post(
            title=title,
            content=content,
            author=session["user"]
        )

        db.session.add(post)
        db.session.commit()

        return redirect(url_for("view_post"))

    return render_template("create.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  

    app.run(debug=True)
