from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    qty = db.Column(db.Integer)
    price = db.Column(db.Float)

with app.app_context():
    db.create_all()



@app.route("/api/products")
def api_products():
    search = request.args.get("search")

    if search:
        products = Product.query.filter(Product.name.contains(search)).all()
    else:
        products = Product.query.all()

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "qty": p.qty,
            "price": p.price
        })
    return jsonify(data)




@app.route("/api/products", methods=["POST"])
def api_add():
    data = request.get_json()
    p = Product(name=data["name"], qty=data["qty"], price=data["price"])
    db.session.add(p)
    db.session.commit()
    return jsonify({"message":"added"})



@app.route("/api/update/<int:id>", methods=["PATCH"])
def api_update(id):
    p = Product.query.get(id)
    data = request.get_json()
    p.qty += data["change"]
    db.session.commit()
    return jsonify({"message":"updated"})




@app.route("/api/delete/<int:id>", methods=["DELETE"])
def api_delete(id):
    Product.query.filter_by(id=id).delete()
    db.session.commit()
    return jsonify({"message":"deleted"})




@app.route("/")
def home():
    return render_template("index.html")

app.run(debug=True)
