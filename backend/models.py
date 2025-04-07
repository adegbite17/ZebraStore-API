from datetime import datetime
from . import bcrypt, db
from flask_login import UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash


# User model for customers and admins
class User(db.Model):
    """Represents a user in the Fazemart application.

        Stores user authentication and profile information, including their orders and cart items.
        Supports admin status for role-based access control.

        Attributes:
            id (int): Unique identifier for the user (primary key).
            email (str): User’s email address (unique, max 120 characters, required).
            password_hash (str): Hashed password for authentication (max 128 characters, required).
            firstname (str): User’s first name (max 50 characters, required).
            lastname (str): User’s last name (max 50 characters, required).
            address (str): User’s shipping address (max 250 characters, required).
            username (str): User’s unique username (max 50 characters, required).
            phone (str): User’s phone number (max 100 characters, required).
            is_admin (bool): Indicates if the user has admin privileges (default: False).
            created_at (datetime): Timestamp of user creation (default: UTC now).
            updated_at (datetime): Timestamp of last update (updated on change, UTC now).

        Relationships:
            orders (List[Order]): List of orders placed by the user (lazy-loaded).
            cart_items (List[CartItem]): List of items in the user’s cart (lazy-loaded).
        """

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

    def set_password(self, password):
        """Hash and set the user’s password.

                Args:
                    password (str): The plaintext password to hash and store.

                Notes:
                    Uses bcrypt to generate a secure password hash, stored in password_hash.
                """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        """Verify if the provided password matches the stored hash.

                Args:
                    attempted_password (str): The plaintext password to check.

                Returns:
                    bool: True if the password matches, False otherwise.
                """
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def convert_to_dict(self):
        """Convert user data to a dictionary for API responses.

                Returns:
                    dict: A dictionary containing user details excluding sensitive fields.
                        - id (int): User ID.
                        - username (str): User’s username.
                        - email (str): User’s email.
                        - firstname (str): User’s first name.
                        - lastname (str): User’s last name.
                        - address (str): User’s address.

                Notes:
                    Excludes password_hash, is_admin, and timestamps for security/privacy.
                """
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
    """Represents a product category in the Fazemart application.

        Groups products into categories for organization and browsing.

        Attributes:
            id (int): Unique identifier for the category (primary key).
            name (str): Category name (unique, max 50 characters, required).
            description (str): Optional description of the category (unlimited length).

        Relationships:
            products (List[Product]): List of products in this category (lazy-loaded).
        """

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text())

    # Relationship
    products = db.relationship('Product', backref='category', lazy=True)


# Product model
class Product(db.Model):
    """Represents a product available for purchase in the Fazemart application.

        Stores product details, stock, and relationships to categories, cart items, and order items.

        Attributes:
            id (int): Unique identifier for the product (primary key).
            name (str): Product name (max 100 characters, required).
            description (str): Product description (unlimited length, optional).
            price (float): Product price (required).
            stock (int): Available stock quantity (default: 0).
            category_id (int): Foreign key to the Category table (required).
            created_at (datetime): Timestamp of product creation (default: UTC now).
            image_url (str): URL to the product image (max 255 characters, optional).
            updated_at (datetime): Timestamp of last update (updated on change, UTC now).

        Relationships:
            cart_items (List[CartItem]): List of cart items referencing this product (lazy-loaded).
            order_items (List[OrderItem]): List of order items referencing this product (lazy-loaded).
        """

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
        """Convert product data to a dictionary for API responses.

                Returns:
                    dict: A dictionary containing product details.
                        - id (int): Product ID.
                        - name (str): Product name.
                        - description (str): Product description.
                        - price (float): Product price.
                        - stock (int): Available stock.
                        - category_id (int): Category ID.
                        - created_at (str): ISO-formatted creation timestamp (or None if unset).
                        - image_url (str): URL to the product image (or None if unset).

                Notes:
                    Used in API responses to expose product information to the frontend.
                """
        return {'id': self.id, 'name': self.name,
                'description': self.description,
                'price': self.price, 'stock': self.stock,
                'category_id': self.category_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'image_url': self.image_url}


# Order model
class Order(db.Model):
    """Represents a customer order in the Fazemart application.

        Tracks order details, status, and relationships to users and order items.

        Attributes:
            id (int): Unique identifier for the order (primary key).
            total_amount (float): Total cost of the order (required).
            status (str): Order status (max 20 characters, default: 'Pending').
                Valid values: 'Pending', 'Processing', 'Shipped', 'Delivered'.
            created_at (datetime): Timestamp of order creation (default: UTC now).
            shipping_address (str): Shipping address for the order (required, unlimited length).
            payment_ref (str): Payment reference or transaction ID (max 100 characters, optional).
            owner (int): Foreign key to the User table (required).
            updated_at (datetime): Timestamp of last update (updated on change, UTC now).

        Relationships:
            order_items (List[OrderItem]): List of items in this order (lazy-loaded).
        """

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
    """Represents an item within an order in the Fazemart application.

        Connects orders to products, storing quantity and price at purchase time.

        Attributes:
            id (int): Unique identifier for the order item (primary key).
            quantity (int): Number of units ordered (required).
            price (float): Price per unit at the time of purchase (required).
            order_id (int): Foreign key to the Order table (required).
            product_id (int): Foreign key to the Product table (required).
            updated_at (datetime): Timestamp of last update (updated on change, UTC now).

        Relationships:
            order (Order): The order this item belongs to (backref-enabled, lazy-loaded).
            ordered_product (Product): The product ordered (backref-enabled, lazy-loaded).
        """
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
    """Represents an item in a user’s shopping cart in the Fazemart application.

        Tracks the quantity of a product a user intends to purchase.

        Attributes:
            id (int): Unique identifier for the cart item (primary key).
            quantity (int): Number of units in the cart (default: 1).
            user_id (int): Foreign key to the User table (optional, nullable).
            product_id (int): Foreign key to the Product table (required).

        Relationships:
            user (User): The user who owns this cart item (backref-enabled, lazy-loaded).
            product (Product): The product in the cart (backref-enabled, lazy-loaded).
        """

    __tablename__ = 'cart_items'

    id = db.Column(db.Integer(), primary_key=True)
    quantity = db.Column(db.Integer(), default=1)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    # orders = db.Column(db.Integer(), db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'), nullable=False)

    def convert_to_dict(self):
        """Convert cart item data to a dictionary for API responses.

                Returns:
                    dict: A dictionary containing cart item details.
                        - id (int): Cart item ID.
                        - product_id (int): ID of the product in the cart.
                        - quantity (int): Number of units.
                        - user_id (int): ID of the user owning the cart (or None if unset).

                Notes:
                    Used in API responses to expose cart information to the frontend.
                """

        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'user_id': self.user_id
        }

    # Relationship
    # product = db.relationship('Product', backref='cart_items', lazy=True)
