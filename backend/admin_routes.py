import jwt   # json web token, for secured authentication and information exchange
from . import app, db
from flask import jsonify, request, redirect, g, abort
from datetime import datetime, timedelta
from .models import User, Product, OrderItem, Order, Category
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
import psycopg2


# Authentication functionality middleware
def admin_required(f):
    """
        Decorator to restrict access to admin users only.

        Verifies the presence and validity of a JWT token in the Authorization header, ensuring the
        token corresponds to an admin user. Sets the authenticated user in Flask’s g object for use
        in the decorated route.

        Parameters
        ----------
        f : callable
            The function to decorate.

        Returns
        -------
        callable
            The wrapped function with admin access enforcement.

        Responses
        ---------
        - On success: Proceeds to the decorated function.
        - On missing token (401): {"message": "Token is missing"}
        - On invalid token format (401): {"message": "Invalid token format"}
        - On expired token (401): {"message": "Token has expired"}
        - On invalid token (401): {"message": "Invalid token"}
        - On non-admin user (403): {"message": "Admin access required"}
        - On authentication error (500): {"message": "Authentication error: <error>"}

        Notes
        -----
        Requires Flask, Flask-JWT, and a User model with an is_admin attribute.
        Expects the token in the format 'Bearer <token>' in the Authorization header.
        Uses app.config['SECRET_KEY'] for token decoding (not Flask-JWT-Extended’s JWT_SECRET_KEY).
        Stores the authenticated user in g.current_user for downstream use.
        """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            if not auth_header.startswith('Bearer'):
                return jsonify({'message': 'Invalid token format'}), 401
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
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

    return decorated


# Admin Login Route
@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Authenticate an admin user and issue a JWT token.

        Expects a JSON payload with email and password. Verifies the credentials against the User
        model, ensuring the user is an admin, and returns a JWT token upon successful login.

        Request:
            request.json (dict): JSON payload with required fields:
                - email (str): The admin’s email address.
                - password (str): The admin’s password.

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {
                    "message": "Login successful",
                    "token": str
                  }
                  Example: {
                    "message": "Login successful",
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                  }
                - On missing/invalid fields (400): {"message": "Email and password are required"}
                - On invalid email format (400): {"message": "Invalid email format"}
                - On invalid credentials/not admin (401): {"message": "Invalid credentials or not an admin"}
                - On error (500): {"message": "Error during login: <error>"}

        Notes:
            - Requires Flask and PyJWT for token generation.
            - Uses app.config['SECRET_KEY'] for JWT encoding (not Flask-JWT-Extended’s JWT_SECRET_KEY).
            - Token expires after 1 hour (configurable via timedelta).
            - Assumes User model has check_password_correction() and is_admin attributes.
        """
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

        token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        return jsonify({'message': 'Login successful', 'token': token}), 200

    except Exception as e:
        return jsonify({'message': f'Error during login: {str(e)}'}), 500


# Admin Logout Route (Client-side token invalidation)
@app.route('/admin/logout', methods=['POST'])
@admin_required
def admin_logout():
    """Confirm admin logout for the client.

        Requires a valid admin JWT token in the Authorization header via the admin_required decorator.
        Since JWT is stateless, this endpoint does not invalidate the token server-side; it simply
        confirms the logout action, expecting the client to discard the token.

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {"message": "Logged out successfully"}
                  Example: {"message": "Logged out successfully"}

        Notes:
            - Requires the admin_required decorator, which enforces admin-only access and validates the JWT.
            - Logout is a client-side operation; the server does not blacklist or invalidate the token.
            - Inherits error responses from admin_required (e.g., 401 for invalid token, 403 for non-admin).
        """
    # Since JWT is stateless, logout is handled client-side by discarding the token.
    # This route just confirms the action for the client.
    return jsonify({'message': 'Logged out successfully'}), 200


# Admin route to update the status of customers order
@app.route('/admin/orders/<int:order_id>', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """Update the status of an order as an admin.

        Requires a valid admin JWT token in the Authorization header via the admin_required decorator.
        Updates the status of the specified order to a new value from a predefined list of valid statuses,
        and records the update timestamp.

        Args:
            order_id (int): The ID of the order to update, extracted from the URL.

        Request:
            request.json (dict): JSON payload with required field:
                - status (str): The new status for the order (e.g., 'Pending', 'Processing', 'Shipped', 'Delivered').

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {
                    "message": "Order updated successfully",
                    "order_id": int,
                    "new_status": str
                  }
                  Example: {
                    "message": "Order updated successfully",
                    "order_id": 1,
                    "new_status": "Shipped"
                  }
                - On missing status (400): {"message": "Status is required"}
                - On invalid status (400): {"message": "Invalid status value"}
                - On order not found (404): Automatically raised by get_or_404()
                - On error (500): {"message": "Error updating order: <error>"}

        Notes:
            - Requires the admin_required decorator, which enforces admin-only access and validates the JWT.
            - Valid statuses are: 'Pending', 'Processing', 'Shipped', 'Delivered'.
            - Updates the order’s updated_at field to the current UTC time.
            - Inherits error responses from admin_required (e.g., 401 for invalid token, 403 for non-admin).
        """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid request body'}), 400

        status = data.get('status')  # e.g., 'Pending', 'Processing', 'Shipped', 'Delivered'
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
    """Retrieve a paginated list of all orders for admin review.

        Requires a valid admin JWT token in the Authorization header via the admin_required decorator.
        Fetches all orders with their associated user details, supporting pagination via query parameters.

        Query Parameters:
            - page (int, optional): The page number to retrieve (default: 1).
            - per_page (int, optional): The number of orders per page (default: 10).

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {
                    "orders": [order_dict, ...],
                    "total": int,
                    "pages": int,
                    "current_page": int
                  }
                  where order_dict contains:
                    - id (int): Order ID.
                    - user_id (int): ID of the user who placed the order.
                    - username (str): Username of the order’s owner.
                    - status (str): Order status (e.g., 'Pending').
                    - total_amount (float): Total cost of the order.
                    - created_at (str): ISO-formatted creation timestamp.
                  Example: {
                    "orders": [{
                      "id": 1,
                      "user_id": 2,
                      "username": "john_doe",
                      "status": "Pending",
                      "total_amount": 17000.0,
                      "created_at": "2025-04-07T12:00:00"
                    }],
                    "total": 1,
                    "pages": 1,
                    "current_page": 1
                  }
                - On invalid pagination (400): {"message": "Invalid pagination parameters"}
                - On error (500): {"message": "Error fetching orders: <error>"}

        Notes:
            - Requires the admin_required decorator, which enforces admin-only access and validates the JWT.
            - Joins the Order and User tables to include username in the response.
            - Pagination is handled by SQLAlchemy’s paginate(); error_out=False ensures empty pages return an empty list.
            - Inherits error responses from admin_required (e.g., 401 for invalid token, 403 for non-admin).
        """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        if page < 1 or per_page < 1:
            return jsonify({'message': 'Invalid pagination parameters'}), 400

        # Modernized SQLAlchemy query to avoid LegacyAPIWarning
        pagination = db.session.query(Order).join(User).paginate(
            page=page, per_page=per_page, error_out=False
        )
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
    """Update an existing product’s details as an admin.

        Requires a valid admin JWT token in the Authorization header via the admin_required decorator.
        Updates the specified product’s attributes (name, price, stock, description) with provided values,
        leaving unchanged any fields not included in the request. Validates price and stock values.

        Args:
            product_id (int): The ID of the product to update, extracted from the URL.

        Request:
            request.json (dict): JSON payload with optional fields:
                - name (str, optional): New product name (defaults to current name).
                - price (int or float, optional): New price (must be non-negative).
                - stock (int, optional): New stock quantity (must be a non-negative integer).
                - description (str, optional): New description (defaults to current description).

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {
                    "message": "Product updated successfully",
                    "product_id": int
                  }
                  Example: {
                    "message": "Product updated successfully",
                    "product_id": 1
                  }
                - On invalid price (400): {"message": "Invalid price"}
                - On invalid stock (400): {"message": "Invalid stock"}
                - On product not found (404): Automatically raised by get_or_404()
                - On error (500): {"message": "Error updating product: <error>"}

        Notes:
            - Requires the admin_required decorator, which enforces admin-only access and validates the JWT.
            - Updates the product’s updated_at field to the current UTC time.
            - Price must be a non-negative number (int or float); stock must be a non-negative integer.
            - Fields not provided in the request retain their current values.
            - Inherits error responses from admin_required (e.g., 401 for invalid token, 403 for non-admin).
        """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid request body'}), 400

        # Modernized SQLAlchemy to avoid LegacyAPIWarning
        product = db.session.get(Product, product_id) or abort(404)

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
    """Create a new product as an admin.

    Requires a valid admin JWT token in the Authorization header via the admin_required decorator.
    Creates a new product with the provided details, validating required fields, data types, and category.

    Request:
        request.json (dict): JSON payload with required fields:
            - name (str): The name of the product.
            - price (int or float): The price of the product (must be non-negative).
            - stock (int): The initial stock quantity (must be a non-negative integer).
            - description (str): The product description.
            - category_id (int): The ID of the product’s category (must exist in Category table).

    Returns:
        tuple: A JSON response and HTTP status code.
            - On success (201): {
                "message": "Product created successfully",
                "product_id": int
              }
              Example: {
                "message": "Product created successfully",
                "product_id": 1
              }
            - On invalid request (400): {"message": "Invalid request body"}
            - On missing fields (400): {"message": "Missing required fields"}
            - On invalid price (400): {"message": "Invalid price"}
            - On invalid stock (400): {"message": "Invalid stock"}
            - On invalid category_id (400): {"message": "Invalid category_id"}
            - On error (500): {"message": "Error creating product: <error>"}

    Notes:
        - Requires the admin_required decorator, which enforces admin-only access and validates the JWT.
        - Sets the product’s created_at field to the current UTC time.
        - Price must be a non-negative number (int or float); stock must be a non-negative integer.
        - Validates category_id against the Category table; assumes Category model exists.
        - Inherits error responses from admin_required (e.g., 401 for invalid token, 403 for non-admin).
    """
    try:
        # Force JSON parsing and handle invalid cases explicitly
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'message': 'Invalid request body'}), 400

        required_fields = ['name', 'price', 'stock', 'description', 'category_id']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400

        if not isinstance(data['price'], (int, float)) or data['price'] < 0:
            return jsonify({'message': 'Invalid price'}), 400
        if not isinstance(data['stock'], int) or data['stock'] < 0:
            return jsonify({'message': 'Invalid stock'}), 400

        # Validate category_id (modernized SQLAlchemy)
        category = db.session.get(Category, data['category_id'])
        if not category:
            return jsonify({'message': 'Invalid category_id'}), 400

        product = Product(
            name=data['name'],
            price=data['price'],
            stock=data['stock'],
            description=data['description'],
            category_id=data['category_id'],
            created_at=datetime.utcnow()
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'product_id': product.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500