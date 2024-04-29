from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Define the database models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category', lazy='dynamic')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('ProductSource', backref='seller', lazy='dynamic')

class ProductSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    categories = Category.query.all()
    products = Product.query.all()
    sellers = Seller.query.all()
    product_sources = ProductSource.query.all()
    return render_template('index.html', categories=categories, products=products, sellers=sellers, product_sources=product_sources)

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    price = float(request.form['price'])
    category_id = int(request.form['category_id'])
    product = Product(name=name, price=price, category_id=category_id)
    db.session.add(product)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_seller', methods=['POST'])
def add_seller():
    name = request.form['name']
    seller = Seller(name=name)
    db.session.add(seller)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_product_source', methods=['POST'])
def add_product_source():
    product_id = int(request.form['product_id'])
    seller_id = int(request.form['seller_id'])
    quantity = int(request.form['quantity'])
    product_source = ProductSource(product_id=product_id, seller_id=seller_id, quantity=quantity)
    db.session.add(product_source)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_cate.html', category=category)

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.category_id = int(request.form['category_id'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/edit_seller/<int:id>', methods=['GET', 'POST'])
def edit_seller(id):
    seller = Seller.query.get_or_404(id)
    if request.method == 'POST':
        seller.name = request.form['name']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_seller.html', seller=seller)

@app.route('/edit_product_source/<int:id>', methods=['GET', 'POST'])
def edit_product_source(id):
    product_source = ProductSource.query.get_or_404(id)
    products = Product.query.all()
    sellers = Seller.query.all()

    if request.method == 'POST':
        # Update the product_source instance with the form data
        product_source.product_id = request.form['product_id']
        product_source.seller_id = request.form['seller_id']
        product_source.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_product_source.html', product_source=product_source, products=products, sellers=sellers)


@app.route('/delete_category/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_seller/<int:id>', methods=['POST'])
def delete_seller(id):
    seller = Seller.query.get_or_404(id)
    db.session.delete(seller)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_product_source/<int:id>', methods=['POST'])
def delete_product_source(id):
    product_source = ProductSource.query.get_or_404(id)
    db.session.delete(product_source)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/assets_chart')
def assets_chart():
    products = Product.query.all()
    categories = {c.name: 0 for c in Category.query.all()}
    for product in products:
        categories[product.category.name] += product.price
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(categories.keys(), categories.values())
    ax.set_title('Current Assets by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Value')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return render_template('charts.html', image_base64=image_base64)


if __name__ == '__main__':
    app.run(debug=True)