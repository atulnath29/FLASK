from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/show/<int:age>')
def show(age):
    return render_template('home.html', age = age)

@app.route('/loop/<name>')
def loop(name):
    text = "Books", "Bag", "Pen", "Pencil"
    return render_template('loop.html', text=text, user_name=name)

@app.route('/auth/<role>')
def auth(role):
    return render_template('page.html', role = role)

@app.route("/courses")
def list_courses():
    courses = [
        "Python Programming",
        "Web Development",
        "Data Science",
        "Machine Learning",
        "Artificial Intelligence"
    ]
    return render_template("list.html", courses=courses)

@app.route("/stu")
def stu():
    students = [
        {"name": "Ayush", "course": "Python", "city": "Bhopal"},
        {"name": "Riya", "course": "Flask", "city": "Indore"},
        {"name": "Karan", "course": "Data Science", "city": "Delhi"}
    ]
    return render_template("students.html", students=students)


if __name__ == '__main__':    
    app.run(debug=True)