
# 🐍 Flask Learning Journey

A structured, day-by-day Flask learning project covering core web development concepts — from routing basics to building a full-featured CRM application.

---

## 📁 Project Structure

```
Flask-main/
├── Day_01/              # Flask basics & routing
├── Day_02/              # Practice notebook (Jupyter)
├── Day_03/              # Jinja2 templating
├── Day_04/              # Flask-SQLAlchemy intro
├── Day_05/              # SQLAlchemy queries + Inventory app
├── Day_06/              # HTML forms & WTForms
├── Day_07/              # Sessions, decorators & authentication
├── Day_07_Mini_Project/ # Blog app with auth
├── Day_08/              # User management (admin dashboard)
├── Day_09/              # App blueprints & modular structure
│   ├── Session_1/       # Inventory Management System
│   └── Session_2/       # Store with separated models/DB layer
└── Project/             # 🏆 Final Project: CRM System
```

---

## 📚 Day-by-Day Breakdown

### Day 01 — Flask Basics
- Creating a Flask app
- Route definitions (`@app.route`)
- Dynamic URL parameters (`/show/<n>`)
- Rendering HTML templates with `render_template`
- Passing variables to templates
- Intro to SQLAlchemy models (commented scaffold)

### Day 02 — Practice
- Jupyter notebook exercises for consolidating concepts

### Day 03 — Jinja2 Templating
- Template rendering with variables
- Loops (`{% for %}`) and conditionals in templates
- Passing lists and dicts to templates
- Multiple template pages (home, list, loop, students)

### Day 04 — Flask-SQLAlchemy Introduction
- Configuring SQLAlchemy with SQLite
- Defining models (`db.Model`)
- Basic CRUD via URL routes
- Database creation with `db.create_all()`

### Day 05 — Advanced SQLAlchemy Queries
- Filtering, ordering, counting records
- Foreign keys and model relationships (`User` → `Post`)
- Pagination with `.paginate()`
- **Mini Project:** Inventory Management System (add, update, delete products)

### Day 06 — Forms & Input Handling
- HTML forms with `request.form`
- Registration form with success/failure feedback
- **Mini Task:** User registration & login with session-based dashboard

### Day 07 — Sessions, Decorators & Auth
- Flask session management
- Building login-protected routes using Python decorators
- Password hashing with `werkzeug.security`
- User registration, login, and logout flows

### Day 07 Mini Project — Blog App
- Full authentication (register/login/logout)
- Create and view blog posts stored in a text file
- Session-based access control
- Custom CSS styling

### Day 08 — Admin Dashboard
- Multi-role user management
- User CRUD (add, edit, delete)
- Task tracking per user
- Template inheritance with `base.html`
- Login required across all admin pages

### Day 09 — Modular Flask Apps
**Session 1** — Inventory System (refactored, with virtual environment)
- Separated concerns with `models.py` and `database.py`
- Virtual environment setup (Python 3.13)

**Session 2** — Store Application
- Clean model/database separation
- Custom CSS styling
- SQLite via SQLAlchemy

---

## 🏆 Final Project — CRM System

A fully functional **Customer Relationship Management** application.

### Features
- **Authentication** — register, login, logout with hashed passwords
- **Dashboard** — overview with charts and key metrics
- **Customer Management** — add, view, and profile customers
- **Customer Analytics** — trust scores, purchase history, activity tags (VIP, Good, Normal, Risky, Bad, Banned)
- **Product Management** — add/edit products with categories, pricing, tax, and stock
- **Billing & Invoicing** — create invoices, view billing history, invoice detail pages
- **Returns Management** — handle return requests, validate/invalidate returns
- **Transaction Search** — search across orders and transactions
- **User Management** — admin-controlled user roles

### Tech Stack
- **Backend:** Flask, SQLite (via `sqlite3`)
- **Auth:** `werkzeug.security` (password hashing)
- **Frontend:** Jinja2 templates, custom CSS (auth, dashboard, pages)
- **Database:** Raw SQLite with `sqlite3.Row` factory

### Running the Project
```bash
cd Project
pip install -r requirements.txt
python app.py
```

---

## ⚙️ Requirements

```
flask>=2.3.0
werkzeug>=2.3.0
flask-sqlalchemy  # used in Day_01 through Day_09
```

Install all dependencies:
```bash
pip install flask flask-sqlalchemy werkzeug
```

---

## 🚀 Getting Started

Clone the repository and navigate into any day's folder:

```bash
git clone https://github.com/your-username/Flask.git
cd Flask/Day_01
python app.py
```

Each day folder contains its own `app.py`. Run it with Python and open `http://127.0.0.1:5000` in your browser.

---

## 🧰 Tech Stack

| Technology       | Usage                            |
|------------------|----------------------------------|
| Python 3.13      | Core language                    |
| Flask 3.x        | Web framework                    |
| Flask-SQLAlchemy | ORM for database interactions    |
| SQLite           | Lightweight relational database  |
| Jinja2           | HTML templating engine           |
| Werkzeug         | Password hashing, request utils  |
| HTML/CSS         | Frontend templates               |

---

## 📌 Notes

- Each day's folder is standalone and independently runnable.
- The `Day_09/Session_1/venv/` folder contains a full Windows virtual environment — this can be excluded from version control by adding it to `.gitignore`.
- SQLite database files (`.db`) are included for reference but can be regenerated by running the app.

---

## 🙈 Recommended `.gitignore`

```gitignore
__pycache__/
*.pyc
*.db
venv/
.env
instance/
```

---

## 📄 License

This project is for educational purposes. Feel free to fork, modify, and build upon it.
