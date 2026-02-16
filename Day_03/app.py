from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    role = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(50), nullable = False)

@app.route("/")
def home():
    return "<p>Home</p>"

@app.route("/user/add")
def add_user():
    return render_template("userAdd.html")

@app.post("/user/add/submit")
def user_add_submit_action():
    uname = request.form.get('name')
    role = request.form.get('role')
    email = request.form.get('email')

    if not uname or not role:
        return {"error": "Name and role are required"}, 400

    user = User()
    user.name = uname
    user.role = role
    user.email = email

    db.session.add(user)
    db.session.commit()

    return fetch_user()

@app.route("/user/show")
def fetch_user():
    users = User.query.all()
  
    print("ID\t\tNAME\t\tROLE\t\tEMAIL")
    for user in users:
        id = user.id
        name = str(user.name)
        role = str(user.role)
        email = str(user.email)
        print(f"{id}\t\t{name.capitalize()}\t\t{role.capitalize()}\t\t{email}")

    return render_template("userShow.html",users = users)


@app.route("/user/update/<int:id>")
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return "<p>ERROR: User not found</p>", 404

    name = request.args.get("name", default="", type=str)
    role = request.args.get("role", default="", type=str)

    if name:
        user.name = name

    if role:
        user.role = role

    db.session.commit()
    return f"<p>MESSAGE: User {user.name} updated successfully</p>"


@app.route("/user/delete/<int:id>")
def delete_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return "<p>ERROR: User not found</p>", 404

    db.session.delete(user)
    db.session.commit()
    return f"<p>MESSAGE: User {user.name} deleted successfully</p>"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)   
