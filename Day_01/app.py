# from datetime import datetime
from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

# db = SQLAlchemy(app)

# class Todo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.String(500), nullable=True)
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)
#     def __repr__(self) -> str:
#         return f'{self.id} - {self.title}'

@app.route('/')
def home(todo_list = None):
    # todo_list = Todo.query.all()
    return render_template('index.html',todo_list = todo_list)

@app.route('/show/<name>')
def show(name):
    # todo = Todo(title = "my task", description = "this is my first task")
    # db.session.add(todo)
    # db.session.commit()
    # print(todo)
    text = ["hello","world","this","is","flask"]
    return render_template('about.html', user_name = name, text = text)

@app.route('/welcome/<name>')
def welcome(name):
    return render_template('welcome.html', user_name = name)

if __name__ == '__main__':    
    app.run(debug=True)