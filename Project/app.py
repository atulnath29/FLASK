from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Tell Flask to use "html" folder instead of "templates"
app = Flask(__name__, template_folder='html')
app.config['SECRET_KEY'] = 'crm-secret-key-2024'

# ─── DB PATH ─────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ─── TEMPLATE FILTERS ────────────────────────────────────────────────────────
@app.template_filter('trust_class')
def trust_class(score):
    if score >= 90: return 'excellent'
    elif score >= 70: return 'good'
    elif score >= 40: return 'average'
    else: return 'poor'

@app.template_filter('tag_class')
def tag_class(tag):
    return {'VIP':'vip','Good':'good','Normal':'normal','Risky':'risky',
            'Bad':'bad','Banned':'banned','Excellent':'excellent','Poor':'poor'}.get(tag,'unknown')

@app.template_filter('status_class')
def status_class(status):
    return status.lower() if status else 'unknown'

# ─── DB INIT ─────────────────────────────────────────────────────────────────
def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS customer_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        total_purchases INTEGER DEFAULT 0,
        total_returns INTEGER DEFAULT 0,
        valid_returns INTEGER DEFAULT 0,
        invalid_returns INTEGER DEFAULT 0,
        trust_score INTEGER DEFAULT 50,
        tag TEXT DEFAULT 'Good',
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    );
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price DECIMAL(10,2) NOT NULL,
        tax DECIMAL(5,2) NOT NULL DEFAULT 0.00,
        qty INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        phone_number TEXT,
        total_amount DECIMAL(10,2) NOT NULL,
        total_tax DECIMAL(10,2) NOT NULL,
        grand_total DECIMAL(10,2) NOT NULL,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    );
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        tax_rate DECIMAL(5,2) NOT NULL,
        total_price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (bill_id) REFERENCES bills (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    );
    CREATE TABLE IF NOT EXISTS returns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER NOT NULL,
        transaction_id TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        phone_number TEXT,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        reason TEXT,
        status TEXT DEFAULT 'pending',
        is_valid INTEGER DEFAULT 0,
        approved_by INTEGER,
        approved_at TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id),
        FOREIGN KEY (approved_by) REFERENCES users (id)
    );
    ''')

    # Seed admin if not exists
    if not c.execute("SELECT id FROM users WHERE role='admin'").fetchone():
        c.execute("INSERT INTO users (username,email,password_hash,role) VALUES (?,?,?,?)",
                  ('admin','admin@crm.com', generate_password_hash('admin123'), 'admin'))

    # Seed sample data if empty
    if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ('Laptop Pro 15','Electronics',1299.99,8.25,25,'active'),
            ('Wireless Mouse','Electronics',29.99,5.50,150,'active'),
            ('USB-C Hub','Electronics',49.99,6.75,3,'active'),
            ('Mechanical Keyboard','Electronics',89.99,7.25,35,'active'),
            ('Monitor 27"','Electronics',399.99,8.50,12,'active'),
            ('Webcam HD','Electronics',79.99,6.00,2,'active'),
            ('Desk Lamp','Office',34.99,4.50,45,'active'),
            ('Office Chair','Furniture',299.99,9.00,18,'active'),
            ('Notebook Set','Stationery',19.99,3.50,200,'active'),
            ('Coffee Maker','Appliances',149.99,7.75,4,'active'),
        ]
        c.executemany("INSERT INTO products (name,category,price,tax,qty,status) VALUES (?,?,?,?,?,?)", products)

    if c.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
        customers = [
            ('John Doe','john@example.com','555-0101','123 Main St'),
            ('Jane Smith','jane@example.com','555-0102','456 Oak Ave'),
            ('Bob Johnson','bob@example.com','555-0103','789 Pine Rd'),
            ('Alice Brown','alice@example.com','555-0104','321 Elm St'),
            ('Charlie Wilson','charlie@example.com','555-0105','654 Maple Dr'),
        ]
        for name,email,phone,addr in customers:
            c.execute("INSERT INTO customers (name,email,phone,address) VALUES (?,?,?,?)",(name,email,phone,addr))
            cid = c.lastrowid
            c.execute("INSERT INTO customer_analytics (customer_id,total_purchases,valid_returns,invalid_returns,trust_score,tag) VALUES (?,?,?,?,?,?)",
                      (cid,5,2,1,85,'Good'))

    conn.commit()
    conn.close()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'error')
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'error')
            return redirect(url_for('auth'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def generate_transaction_id():
    conn = get_db()
    result = conn.execute("SELECT transaction_id FROM bills WHERE transaction_id LIKE 'TID%' ORDER BY transaction_id DESC LIMIT 1").fetchone()
    conn.close()
    if result:
        num = int(result['transaction_id'][3:]) + 1
    else:
        num = 1
    return f"TID{num:04d}"

def calculate_trust_score(purchases, valid_ret, invalid_ret):
    return purchases - (invalid_ret * 2) + valid_ret

def assign_trust_tag(score):
    if score <= 0: return 'Banned'
    elif score >= 20: return 'VIP'
    elif score >= 10: return 'Good'
    elif score >= 5: return 'Normal'
    elif score >= 1: return 'Risky'
    else: return 'Bad'

def update_customer_trust(customer_id):
    conn = get_db()
    try:
        name = conn.execute("SELECT name FROM customers WHERE id=?", (customer_id,)).fetchone()
        if not name: return
        name = name['name']
        purchases = conn.execute("SELECT COUNT(*) FROM bills WHERE customer_name=?", (name,)).fetchone()[0]
        valid_ret = conn.execute("SELECT COUNT(*) FROM returns WHERE customer_name=? AND is_valid=1", (name,)).fetchone()[0]
        invalid_ret = conn.execute("SELECT COUNT(*) FROM returns WHERE customer_name=? AND is_valid=0 AND status='rejected'", (name,)).fetchone()[0]
        score = calculate_trust_score(purchases, valid_ret, invalid_ret)
        tag = assign_trust_tag(score)
        existing = conn.execute("SELECT id FROM customer_analytics WHERE customer_id=?", (customer_id,)).fetchone()
        if existing:
            conn.execute("""UPDATE customer_analytics SET total_purchases=?,valid_returns=?,invalid_returns=?,
                trust_score=?,tag=?,last_activity=CURRENT_TIMESTAMP WHERE customer_id=?""",
                (purchases, valid_ret, invalid_ret, score, tag, customer_id))
        else:
            conn.execute("""INSERT INTO customer_analytics (customer_id,total_purchases,valid_returns,invalid_returns,trust_score,tag)
                VALUES (?,?,?,?,?,?)""", (customer_id, purchases, valid_ret, invalid_ret, score, tag))
        conn.commit()
    finally:
        conn.close()

# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth'))

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # ── LOGIN ──
        if form_type == 'login':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            if not username or not password:
                flash('Please enter username and password.', 'error')
                return render_template('auth.html', show='login')
            conn = get_db()
            user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            conn.close()
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'error')
                return render_template('auth.html', show='login')

        # ── SIGNUP ──
        elif form_type == 'signup':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            confirm = request.form.get('confirm_password', '').strip()
            if not all([username, email, password, confirm]):
                flash('Please fill all fields.', 'error')
                return render_template('auth.html', show='signup')
            if password != confirm:
                flash('Passwords do not match.', 'error')
                return render_template('auth.html', show='signup')
            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'error')
                return render_template('auth.html', show='signup')
            conn = get_db()
            if conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
                conn.close()
                flash('Username already exists.', 'error')
                return render_template('auth.html', show='signup')
            if conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
                conn.close()
                flash('Email already registered.', 'error')
                return render_template('auth.html', show='signup')
            conn.execute("INSERT INTO users (username,email,password_hash,role) VALUES (?,?,?,?)",
                         (username, email, generate_password_hash(password), 'user'))
            conn.commit()
            conn.close()
            flash('Account created! Please log in.', 'success')
            return render_template('auth.html', show='login')

    return render_template('auth.html', show='login')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth'))

# ─── DASHBOARD ───────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    total_bills = conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
    total_revenue = conn.execute("SELECT COALESCE(SUM(grand_total),0) FROM bills").fetchone()[0]
    inventory_value = conn.execute("SELECT COALESCE(SUM(price*qty),0) FROM products").fetchone()[0]
    low_stock_items = conn.execute("SELECT id,name,qty,category FROM products WHERE qty<5 AND status='active' ORDER BY qty").fetchall()
    pending_returns = conn.execute("SELECT COUNT(*) FROM returns WHERE status='pending'").fetchone()[0]
    recent_bills = conn.execute("""SELECT b.*,u.username as by_name FROM bills b
        LEFT JOIN users u ON b.created_by=u.id ORDER BY b.created_at DESC LIMIT 5""").fetchall()
    conn.close()
    stats = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_bills': total_bills,
        'total_revenue': round(float(total_revenue), 2),
        'total_inventory_value': round(float(inventory_value), 2),
        'low_stock_items': low_stock_items,
        'low_stock_count': len(low_stock_items),
        'pending_returns': pending_returns,
    }
    return render_template('dashboard.html', stats=stats, recent_bills=recent_bills)

# ─── PRODUCTS ────────────────────────────────────────────────────────────────
@app.route('/products')
@login_required
def product_list():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        category = request.form.get('category','').strip()
        price = request.form.get('price','0')
        tax = request.form.get('tax','0')
        qty = request.form.get('qty','0')
        status = request.form.get('status','active')
        if not all([name, category, price, tax, qty]):
            flash('Please fill all fields.', 'error')
            return render_template('product_form.html', action='Add', product=None)
        try:
            price, tax, qty = float(price), float(tax), int(qty)
        except ValueError:
            flash('Invalid price, tax or quantity.', 'error')
            return render_template('product_form.html', action='Add', product=None)
        conn = get_db()
        conn.execute("INSERT INTO products (name,category,price,tax,qty,status) VALUES (?,?,?,?,?,?)",
                     (name,category,price,tax,qty,status))
        conn.commit(); conn.close()
        flash(f'Product "{name}" added!', 'success')
        return redirect(url_for('product_list'))
    return render_template('product_form.html', action='Add', product=None)

@app.route('/products/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_product(pid):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not product:
        conn.close(); flash('Product not found.','error'); return redirect(url_for('product_list'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        category = request.form.get('category','').strip()
        price = request.form.get('price','0')
        tax = request.form.get('tax','0')
        qty = request.form.get('qty','0')
        status = request.form.get('status','active')
        try:
            price, tax, qty = float(price), float(tax), int(qty)
        except ValueError:
            flash('Invalid values.','error')
            return render_template('product_form.html', action='Edit', product=product)
        conn.execute("UPDATE products SET name=?,category=?,price=?,tax=?,qty=?,status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                     (name,category,price,tax,qty,status,pid))
        conn.commit(); conn.close()
        flash('Product updated!','success')
        return redirect(url_for('product_list'))
    conn.close()
    return render_template('product_form.html', action='Edit', product=product)

@app.route('/products/delete/<int:pid>', methods=['POST'])
@login_required
def delete_product(pid):
    conn = get_db()
    p = conn.execute("SELECT name FROM products WHERE id=?", (pid,)).fetchone()
    if p:
        conn.execute("DELETE FROM products WHERE id=?", (pid,))
        conn.commit()
        flash(f'Product "{p["name"]}" deleted.', 'success')
    conn.close()
    return redirect(url_for('product_list'))

# ─── BILLING ─────────────────────────────────────────────────────────────────
@app.route('/billing')
@login_required
def billing():
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE status='active' AND qty>0 ORDER BY name").fetchall()
    conn.close()
    return render_template('billing.html', products=products)

@app.route('/billing/add_item', methods=['POST'])
@login_required
def add_bill_item():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', 1, type=int)
    if not product_id or quantity <= 0:
        return jsonify({'error': 'Invalid product or quantity'}), 400
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id=? AND status='active'", (product_id,)).fetchone()
    if not product:
        conn.close(); return jsonify({'error': 'Product not found'}), 404
    if product['qty'] < quantity:
        conn.close(); return jsonify({'error': f'Only {product["qty"]} in stock'}), 400
    unit_price = float(product['price'])
    tax_rate = float(product['tax'])
    total_price = unit_price * quantity
    tax_amount = total_price * (tax_rate / 100)
    conn.close()
    return jsonify({'success': True, 'item': {
        'product_id': product['id'], 'name': product['name'],
        'quantity': quantity, 'unit_price': unit_price, 'tax_rate': tax_rate,
        'total_price': total_price, 'tax_amount': tax_amount,
        'grand_total': total_price + tax_amount
    }})

@app.route('/billing/save_bill', methods=['POST'])
@login_required
def save_bill():
    customer_name = request.form.get('customer_name','').strip()
    phone_number = request.form.get('phone_number','').strip()
    items_raw = request.form.get('items','')
    if not customer_name or not items_raw:
        return jsonify({'error': 'Customer name and items required'}), 400
    try:
        items_data = json.loads(items_raw)
        if not items_data: return jsonify({'error': 'No items'}), 400
    except:
        return jsonify({'error': 'Invalid items data'}), 400
    conn = get_db()
    try:
        tid = generate_transaction_id()
        total_amount = sum(i['total_price'] for i in items_data)
        total_tax = sum(i['tax_amount'] for i in items_data)
        grand_total = total_amount + total_tax
        cursor = conn.execute("INSERT INTO bills (transaction_id,customer_name,phone_number,total_amount,total_tax,grand_total,created_by) VALUES (?,?,?,?,?,?,?)",
                              (tid,customer_name,phone_number,total_amount,total_tax,grand_total,session['user_id']))
        bill_id = cursor.lastrowid
        for item in items_data:
            conn.execute("INSERT INTO bill_items (bill_id,product_id,product_name,quantity,unit_price,tax_rate,total_price) VALUES (?,?,?,?,?,?,?)",
                         (bill_id,item['product_id'],item['name'],item['quantity'],item['unit_price'],item['tax_rate'],item['total_price']))
            conn.execute("UPDATE products SET qty=qty-?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                         (item['quantity'],item['product_id']))
        conn.commit()
        customer = conn.execute("SELECT id FROM customers WHERE name=?", (customer_name,)).fetchone()
        if customer:
            try: update_customer_trust(customer['id'])
            except: pass
        bill = dict(conn.execute("SELECT b.*,u.username as created_by_name FROM bills b LEFT JOIN users u ON b.created_by=u.id WHERE b.id=?", (bill_id,)).fetchone())
        bill_items = [dict(r) for r in conn.execute("SELECT * FROM bill_items WHERE bill_id=?", (bill_id,)).fetchall()]
        conn.close()
        return jsonify({'success': True, 'bill_id': bill_id, 'transaction_id': tid,
                        'bill_details': bill, 'bill_items': bill_items})
    except Exception as e:
        conn.rollback(); conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/billing/invoices')
@login_required
def view_invoices():
    conn = get_db()
    invoices = conn.execute("SELECT b.*,u.username as created_by_name FROM bills b LEFT JOIN users u ON b.created_by=u.id ORDER BY b.created_at DESC").fetchall()
    conn.close()
    return render_template('invoices.html', invoices=invoices)

@app.route('/billing/invoice/<int:bill_id>')
@login_required
def view_invoice(bill_id):
    conn = get_db()
    bill = conn.execute("SELECT b.*,u.username as created_by_name FROM bills b LEFT JOIN users u ON b.created_by=u.id WHERE b.id=?", (bill_id,)).fetchone()
    if not bill:
        conn.close(); flash('Invoice not found.','error'); return redirect(url_for('view_invoices'))
    items = conn.execute("SELECT * FROM bill_items WHERE bill_id=?", (bill_id,)).fetchall()
    conn.close()
    return render_template('invoice_detail.html', bill=bill, items=items)

@app.route('/billing/invoice-display/<int:bill_id>')
@login_required
def display_invoice(bill_id):
    conn = get_db()
    bill = conn.execute("SELECT b.*,u.username as created_by_name FROM bills b LEFT JOIN users u ON b.created_by=u.id WHERE b.id=?", (bill_id,)).fetchone()
    if not bill:
        conn.close(); flash('Invoice not found.','error'); return redirect(url_for('view_invoices'))
    items = conn.execute("SELECT * FROM bill_items WHERE bill_id=?", (bill_id,)).fetchall()
    conn.close()
    return render_template('invoice_display.html', bill=bill, items=items)

@app.route('/billing/history')
@login_required
def bill_history():
    conn = get_db()
    bills = conn.execute("SELECT b.*,u.username as created_by_name FROM bills b LEFT JOIN users u ON b.created_by=u.id ORDER BY b.created_at DESC").fetchall()
    conn.close()
    return render_template('bill_history.html', bills=bills)

@app.route('/billing/search', methods=['GET', 'POST'])
@login_required
def transaction_search():
    result = None; error = None; searched_tid = None
    if request.method == 'POST':
        tid = request.form.get('tid','').strip().upper()
        searched_tid = tid
        if tid and not tid.startswith('TID'):
            tid = 'TID' + tid
        conn = get_db()
        bill = conn.execute("SELECT b.*,u.username as created_by_name FROM bills b LEFT JOIN users u ON b.created_by=u.id WHERE b.transaction_id=?", (tid,)).fetchone()
        if bill:
            items = conn.execute("SELECT * FROM bill_items WHERE bill_id=?", (bill['id'],)).fetchall()
            result = {'bill': dict(bill), 'items': [dict(i) for i in items]}
        else:
            error = True
        conn.close()
    return render_template('transaction_search.html', result=result, error=error, searched_tid=searched_tid)

# ─── CUSTOMER ANALYTICS ──────────────────────────────────────────────────────
@app.route('/analytics/customers')
@login_required
def customer_analytics():
    conn = get_db()
    customers = conn.execute("""SELECT c.id,c.name,c.phone,c.created_at as join_date,
        ca.total_purchases,ca.total_returns,ca.valid_returns,ca.invalid_returns,
        ca.trust_score,ca.tag,ca.last_activity
        FROM customers c LEFT JOIN customer_analytics ca ON c.id=ca.customer_id
        ORDER BY ca.trust_score DESC, c.name""").fetchall()
    total = len(customers)
    avg_score = sum(c['trust_score'] or 0 for c in customers) / total if total else 0
    tag_stats = {}
    for c in customers:
        t = c['tag'] or 'Unknown'
        tag_stats[t] = tag_stats.get(t,0) + 1
    conn.close()
    return render_template('customer_analytics.html', customers=customers,
        total_customers=total, avg_trust_score=round(avg_score,1),
        total_purchases=sum(c['total_purchases'] or 0 for c in customers),
        total_returns=sum(c['total_returns'] or 0 for c in customers),
        valid_returns=sum(c['valid_returns'] or 0 for c in customers),
        invalid_returns=sum(c['invalid_returns'] or 0 for c in customers),
        tag_stats=tag_stats)

@app.route('/analytics/customers/<int:cid>')
@login_required
def customer_detail(cid):
    conn = get_db()
    customer = conn.execute("""SELECT c.*,ca.total_purchases,ca.total_returns,ca.valid_returns,
        ca.invalid_returns,ca.trust_score,ca.tag,ca.last_activity
        FROM customers c LEFT JOIN customer_analytics ca ON c.id=ca.customer_id WHERE c.id=?""", (cid,)).fetchone()
    if not customer:
        conn.close(); flash('Customer not found.','error'); return redirect(url_for('customer_analytics'))
    bills = conn.execute("SELECT * FROM bills WHERE customer_name=? ORDER BY created_at DESC", (customer['name'],)).fetchall()
    total_spent = sum(b['grand_total'] for b in bills)
    conn.close()
    return render_template('customer_detail.html', customer=customer, bills=bills, total_spent=total_spent)

@app.route('/customers/<int:customer_id>/profile')
@login_required
def customer_profile(customer_id):
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    if not customer:
        conn.close(); flash('Not found.','error'); return redirect(url_for('customer_analytics'))
    analytics = conn.execute("SELECT * FROM customer_analytics WHERE customer_id=?", (customer_id,)).fetchone()
    purchases = conn.execute("""SELECT b.*,u.username as created_by_name FROM bills b
        LEFT JOIN users u ON b.created_by=u.id WHERE b.customer_name=? ORDER BY b.created_at DESC""", (customer['name'],)).fetchall()
    returns = conn.execute("""SELECT r.*,u.username as approved_by_name FROM returns r
        LEFT JOIN users u ON r.approved_by=u.id WHERE r.customer_name=? ORDER BY r.created_at DESC""", (customer['name'],)).fetchall()
    trust_score = analytics['trust_score'] if analytics else 0
    trust_tag = analytics['tag'] if analytics else 'Unknown'
    conn.close()
    return render_template('customer_profile.html', customer=customer, analytics=analytics,
        purchases=purchases, returns=returns,
        total_purchases=len(purchases), total_returns=len(returns),
        total_spent=sum(p['grand_total'] for p in purchases),
        total_returned_value=sum(r['total_amount'] for r in returns if r['status']=='approved'),
        trust_score=trust_score, trust_tag=trust_tag, is_banned=(trust_tag=='Banned'))

@app.route('/analytics/recalculate-trust-scores', methods=['POST'])
@login_required
def recalculate_trust_scores():
    conn = get_db()
    customers = conn.execute("SELECT id FROM customers").fetchall()
    conn.close()
    count = 0
    for c in customers:
        try: update_customer_trust(c['id']); count += 1
        except: pass
    return jsonify({'success': True, 'message': f'Recalculated {count} customers', 'updated_count': count})

# ─── RETURNS ─────────────────────────────────────────────────────────────────
@app.route('/returns')
@login_required
def returns_management():
    conn = get_db()
    returns = conn.execute("""SELECT r.*,u.username as approved_by_name,p.category as product_category
        FROM returns r LEFT JOIN users u ON r.approved_by=u.id
        LEFT JOIN products p ON r.product_id=p.id ORDER BY r.created_at DESC""").fetchall()
    total = len(returns)
    pending = len([r for r in returns if r['status']=='pending'])
    approved = len([r for r in returns if r['status']=='approved'])
    rejected = len([r for r in returns if r['status']=='rejected'])
    valid = len([r for r in returns if r['is_valid']==1])
    invalid = len([r for r in returns if r['is_valid']==0])
    conn.close()
    return render_template('returns_management.html', returns=returns,
        total_returns=total, pending_returns=pending, approved_returns=approved,
        rejected_returns=rejected, valid_returns=valid, invalid_returns=invalid)

@app.route('/returns/request', methods=['GET', 'POST'])
@login_required
def return_request():
    if request.method == 'POST':
        bill_id = request.form.get('bill_id')
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity','0')
        reason = request.form.get('reason','').strip()
        if not all([bill_id, product_id, quantity, reason]):
            flash('Please fill all fields.','error')
            return redirect(url_for('return_request'))
        try:
            quantity = int(quantity)
            if quantity <= 0: raise ValueError()
        except ValueError:
            flash('Invalid quantity.','error'); return redirect(url_for('return_request'))
        conn = get_db()
        bill = conn.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
        product = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        if not bill or not product:
            conn.close(); flash('Invalid bill or product.','error'); return redirect(url_for('return_request'))
        total = product['price'] * quantity
        conn.execute("""INSERT INTO returns (bill_id,transaction_id,customer_name,phone_number,product_id,product_name,quantity,unit_price,total_amount,reason)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (bill_id,bill['transaction_id'],bill['customer_name'],bill['phone_number'],
             product_id,product['name'],quantity,product['price'],total,reason))
        conn.commit(); conn.close()
        flash('Return request submitted!','success')
        return redirect(url_for('returns_management'))
    conn = get_db()
    bills = conn.execute("SELECT * FROM bills ORDER BY created_at DESC").fetchall()
    products = conn.execute("SELECT * FROM products WHERE status='active' ORDER BY name").fetchall()
    conn.close()
    return render_template('return_request.html', bills=bills, products=products)

@app.route('/returns/<int:rid>/approve', methods=['POST'])
@login_required
def approve_return(rid):
    is_valid = request.form.get('is_valid') == '1'
    notes = request.form.get('notes','')
    conn = get_db()
    ret = conn.execute("SELECT * FROM returns WHERE id=?", (rid,)).fetchone()
    if not ret:
        conn.close(); return jsonify({'error':'Not found'}), 404
    try:
        conn.execute("""UPDATE returns SET status='approved',is_valid=?,approved_by=?,
            approved_at=CURRENT_TIMESTAMP,notes=? WHERE id=?""",
            (is_valid, session['user_id'], notes, rid))
        if is_valid:
            conn.execute("UPDATE products SET qty=qty+?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                         (ret['quantity'], ret['product_id']))
        conn.commit()
        customer = conn.execute("SELECT id FROM customers WHERE name=?", (ret['customer_name'],)).fetchone()
        if customer:
            conn.close()
            try: update_customer_trust(customer['id'])
            except: pass
        else:
            conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback(); conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/returns/<int:rid>/reject', methods=['POST'])
@login_required
def reject_return(rid):
    notes = request.form.get('notes','')
    conn = get_db()
    ret = conn.execute("SELECT * FROM returns WHERE id=?", (rid,)).fetchone()
    if not ret:
        conn.close(); return jsonify({'error':'Not found'}), 404
    try:
        conn.execute("""UPDATE returns SET status='rejected',is_valid=0,approved_by=?,
            approved_at=CURRENT_TIMESTAMP,notes=? WHERE id=?""",
            (session['user_id'], notes, rid))
        conn.commit()
        customer = conn.execute("SELECT id FROM customers WHERE name=?", (ret['customer_name'],)).fetchone()
        if customer:
            conn.close()
            try: update_customer_trust(customer['id'])
            except: pass
        else:
            conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback(); conn.close()
        return jsonify({'error': str(e)}), 500

# ─── USERS (admin only) ──────────────────────────────────────────────────────
@app.route('/users')
@admin_required
def users():
    conn = get_db()
    users_list = conn.execute("SELECT id,username,email,role,created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('users.html', users=users_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
