import jwt   # json web token, for secured authentication and information exchange
from . import app, db
from flask import jsonify, request, redirect, g
from datetime import datetime, timedelta
from .models import User, Product, OrderItem, Order
from functools import wraps
import psycopg2


# Authentication functionality middleware
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')  # Authorization passkey
        if not auth_header:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            if not auth_header.startswith('Bearer'):
                return jsonify({'message': 'Invalid token format'}), 401
            token = auth_header.split(" ")[1]  # retrieves the second part/value of my authorization key pass string
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # decode and verify a json web token in flask application
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user or not current_user.is_admin:
                return jsonify({'message': 'Admin access required'}), 403
            g.current_user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401

        except (jwt.InvalidTokenError, IndexError):
            return jsonify({'message': 'Invalid token'}), 401

        except Exception as e:
            return jsonify({'message': f'Authentication error: {str(e)}'}), 500
        return f(*args, **kwargs)

    return decorated


# Admin Login Route
@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'message': 'Email and password are required'}), 400

        email = data['email']
        password = data['password']

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        if '@' not in email:
            return jsonify({'message': 'Invalid email format'}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password_correction(attempted_password=password) or not user.is_admin:
            return jsonify({'message': 'Invalid credentials or not an admin'}), 401

        # Create JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error during login: {str(e)}'}), 500


# Admin Logout Route (Client-side token invalidation)
@app.route('/admin/logout', methods=['POST'])
@admin_required
def admin_logout():
    # Since JWT is stateless, logout is handled client-side by discarding the token.
    # This route just confirms the action for the client.
    return jsonify({'message': 'Logged out successfully'}), 200


# Admin route to update the status of customers order
@app.route('/admin/orders/<int:order_id>', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    try:
        data = request.get_json()
        status = data.get('status')  # example., ready for delivery, payment_received
        valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']

        if not status:
            return jsonify({'message': 'Status is required'}), 400
        if status not in valid_statuses:
            return jsonify({'message': 'Invalid status value'}), 400
        order = Order.query.get_or_404(order_id)
        order.status = status
        order.updated_at = datetime.utcnow()

        db.session.commit()
        return jsonify({
            'message': 'Order updated successfully',
            'order_id': order_id,
            'new_status': status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating order: {str(e)}'}), 500


# Admin route to get all customers order
@app.route('/admin/orders', methods=['GET'])
@admin_required
def get_all_orders():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        if page < 1 or per_page < 1:
            return jsonify({'message': 'Invalid pagination parameters'}), 400
        pagination = Order.query.join(User).paginate(page=page, per_page=per_page, error_out=False)
        orders = pagination.items
        orders_list = [{
            'id': order.id,
            'user_id': order.owner,
            'username': order.user.username,
            'status': order.status,
            'total_amount': order.total_amount,
            'created_at': order.created_at.isoformat()
        } for order in orders]
        return jsonify({
            'orders': orders_list,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching orders: {str(e)}'}), 500

# Admin route to update product in the market
@app.route('/admin/products/<int:product_id>', methods=['PUT'])
@admin_required
def updating_product(product_id):
    try:
        data = request.get_json()
        product = Product.query.get_or_404(product_id)
        product.name = data.get('name', product.name)
        if 'price' in data:
            if not isinstance(data['price'], (int, float)) or data['price'] < 0:
                return jsonify({'message': 'Invalid price'}), 400
            product.price = data['price']
        if 'stock' in data:
            if not isinstance(data['stock'], int) or data['stock'] < 0:
                return jsonify({'message': 'Invalid stock'}), 400
            product.stock = data['stock']
        product.description = data.get('description', product.description)
        product.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Product updated successfully', 'product_id': product_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating product: {str(e)}'}), 500

# Admin route to add new product to the market
@app.route('/admin/products', methods=['POST'])
@admin_required
def creating_product():
    try:
        data = request.get_json()
        required_fields = ['name', 'price', 'stock', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        if not isinstance(data['price'], (int, float)) or data['price'] < 0:
            return jsonify({'message': 'Invalid price'}), 400
        if not isinstance(data['stock'], int) or data['stock'] < 0:
            return jsonify({'message': 'Invalid stock'}), 400
        product = Product(
            name=data['name'],
            price=data['price'],
            stock=data['stock'],
            description=data['description'],
            category_id = data['category_id'],
            created_at=datetime.utcnow()
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'product_id': product.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500