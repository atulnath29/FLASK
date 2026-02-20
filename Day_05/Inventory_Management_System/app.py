from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------- MODEL -------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)

# Create DB
with app.app_context():
    db.create_all()

# ------------------- ROUTES -------------------

# Home / List Products
@app.route('/')
def index():
    search = request.args.get('search')
    
    if search:
        products = Product.query.filter(Product.name.contains(search)).all()
    else:
        products = Product.query.all()
        
    return render_template('index.html', products=products)

# Add Product
@app.route('/add', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        new_product = Product(
            name=request.form['name'],
            quantity=request.form['quantity'],
            price=request.form['price'],
            category=request.form['category']
        )
        db.session.add(new_product)
        db.session.commit()
        flash("Product Added Successfully!")
        return redirect(url_for('index'))
    
    return render_template('add_product.html')

# Update Product
@app.route('/update/<int:id>', methods=['GET','POST'])
def update_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = request.form['quantity']
        product.price = request.form['price']
        product.category = request.form['category']
        
        db.session.commit()
        flash("Product Updated Successfully!")
        return redirect(url_for('index'))

    return render_template('update_product.html', product=product)

# Delete Product
@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product Deleted Successfully!")
    return redirect(url_for('index'))

# Run
if __name__ == '__main__':
    app.run(debug=True)
