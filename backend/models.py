from datetime import datetime
from . import bcrypt, db
from flask_login import UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash


# User model for customers and admins
class User(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def convert_to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'address': self.address
        }


# Product Category model
class Category(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text())

    # Relationship
    products = db.relationship('Product', backref='category', lazy=True)


# Product model
class Product(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text())
    price = db.Column(db.Float(), nullable=False)
    stock = db.Column(db.Integer(), default=0)
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    image_url = db.Column(db.String(255))
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='ordered_product', lazy=True)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    def convert_to_dict(self):
        return {'id': self.id, 'name': self.name,
                'description': self.description,
                'price': self.price, 'stock': self.stock,
                'category_id': self.category_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'image_url': self.image_url}


# Order model
class Order(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    total_amount = db.Column(db.Float(), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Processing, Shipped, Delivered
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    shipping_address = db.Column(db.Text(), nullable=False)
    payment_ref = db.Column(db.String(100))
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    # Relationship
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

# Junction table for Order and CartItem (many-to-many)
# order_items = db.Table('order_items',
#                       db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
#                       db.Column('cart_item_id', db.Integer, db.ForeignKey('cart_item.id'), primary_key=True)
#                       )


# Order Item model (connects orders with products)
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer(), primary_key=True)
    quantity = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Float(), nullable=False)  # Price at time of purchase
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.utcnow)
    # order = db.relationship('Order', backref='order_items', lazy=True)
    # product = db.relationship('Product', backref='order_items', lazy=True)


# Cart Item model for shopping cart
class CartItem(db.Model):

    __tablename__ = 'cart_items'

    id = db.Column(db.Integer(), primary_key=True)
    quantity = db.Column(db.Integer(), default=1)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    # orders = db.Column(db.Integer(), db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'), nullable=False)

    def convert_to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'user_id': self.user_id
        }

    # Relationship
    # product = db.relationship('Product', backref='cart_items', lazy=True)
