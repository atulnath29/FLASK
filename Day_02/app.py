from flask import Flask, render_template
from functions.get_values import get_courses, get_employees

app = Flask(__name__)

@app.route("/")
def landing_page():
    return "this is landing page"

@app.route("/welcome/<name>")
def home_page(name:str):
    text = "Hello I'm admin this side, welcome to the site."
    fruits = ["apple", "mango", "banana"]
    num1 = 10.41
    num2 = 20.35
    nums = [10,22,31,47,59]
    return render_template("welcome.html" ,name = name, text=text, fruits = fruits, num1 = num1, num2 = num2, nums = nums)

@app.route("/home/<user>")
def conditionals(user):
    courses = get_courses()
    empls = get_employees()
    return render_template("home.html", user = user, courses = courses, empls = empls)
   

if __name__ == "__main__":
    app.run(debug=True)
