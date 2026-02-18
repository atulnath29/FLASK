from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

POST_FILE = "posts.txt"

def load_posts():
    try:
        with open(POST_FILE, "r") as f:
            posts = f.readlines()
        return [p.strip() for p in posts]
    except:
        return []

def save_post(post):
    with open(POST_FILE, "a") as f:
        f.write(post + "\n")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        session["user"] = username
        return redirect(url_for("create_post"))
    return render_template("login.html")

@app.route("/create", methods=["GET", "POST"])
def create_post():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        post = request.form.get("post")
        save_post(session["user"] + ": " + post)
        return redirect(url_for("view_posts"))

    return render_template("create_post.html", user=session["user"])

@app.route("/posts")
def view_posts():
    posts = load_posts()
    return render_template("view_posts.html", posts=posts)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
