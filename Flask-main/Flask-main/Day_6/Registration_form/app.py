from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("form.html")

@app.route("/register")
def register():
    name = request.args.get("name")
    email = request.args.get("email")

    if not name or not email:
        return "Please submit the form first"

    return render_template("success.html", name=name, email=email)

if __name__ == "__main__":
    app.run(debug=True)
