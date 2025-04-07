from . import app, db, bcrypt, jwt
from flask import request, jsonify, make_response
from .models import User, Product, CartItem, Order, OrderItem, Category
# from .forms import FormToRegister, PurchaseItemForm
# from flask_login import login_user, logout_user, login_required
import logging
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import requests
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt

logging.basicConfig(level=logging.DEBUG)

@app.route('/favicon.ico')
def favicon():
    """Handle requests for the favicon.ico file by returning an empty response.

        This endpoint prevents 404 errors from browsers requesting a favicon by returning
        a "No Content" response. No favicon is served.

        Returns:
            tuple: An empty string and HTTP status code 204 (No Content).
        """
    return "", 204


@app.route('/')
@app.route('/home')
def home_page_route():
    """Display a welcome message for the Zebra Store API.

        Returns:
            tuple: A JSON response with a welcome message and HTTP status code 200.
                Example: {"message": "Welcome To Zebra Store"}
        """
    return jsonify({'message': 'Welcome To Zebra Store'}), 200


@app.route('/products', methods=['GET'])
def products_route():
    """Retrieve a list of all products in the Zebra Store.

        Queries the database for all products and returns them as a JSON list.
        If no products are available, returns a message indicating the store is out of stock.

        Returns:
            tuple: A JSON response and HTTP status code 200.
                - If products exist: {"products": [product_dict, ...]}
                  where product_dict is the result of Product.convert_to_dict().
                  Example: {"products": [{"id": 1, "name": "Zebra Shirt", "price": 19.99}]}
                - If no products: {"message": "There are no products available, we are out of stock"}

        Notes:
            Assumes the Product model has a convert_to_dict() method that returns a dictionary
            representation of the product (e.g., {"id": int, "name": str, "price": float}).
        """
    all_items = Product.query.all()
    if not all_items:
        return make_response(jsonify({'message': 'There are no products available, we are out of stock'}), 200)
    # Assuming Product has a to_dict() method for serialization
    return jsonify({'products': [item.convert_to_dict() for item in all_items]}), 200


@app.route('/signup', methods=['POST'])
def signup_route():
    """Create a new user account with the provided details.

        Expects a JSON payload with user information. Validates required fields, checks for duplicate
        email or username, and creates a new user in the database. Returns an access token upon success.

        Args:
            request.json (dict): JSON payload containing:
                - firstname (str): User's first name.
                - lastname (str): User's last name.
                - email (str): User's email address.
                - password (str): User's password.
                - address (str): User's address.
                - username (str): User's chosen username.
                - phone (str): User's phone number.

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (201): {"message": str, "access_token": str, "user": {"username": str, "email": str}}
                  Example: {"message": "Account created successfully, Welcome jdoe", "access_token": "...", "user": {"username": "jdoe", "email": "jdoe@example.com"}}
                - On invalid JSON (400): {"message": "Invalid form submission"}
                - On missing fields (400): {"message": "Missing required fields"}
                - On duplicate email/username (400): {"message": "Email or username already exists"}
                - On server error (500): {"message": "Error creating user", "error": str}

        Raises:
            IntegrityError: If a database constraint (e.g., unique email/username) is violated.
            Exception: For unexpected errors during user creation.

        Notes:
            - Requires the User model to have a set_password() method for hashing the password.
            - Uses Flask-JWT-Extended for access token generation via create_access_token().
        """
    try:
        # Handle JSON payload from the test
        if not request.is_json:
            return make_response(jsonify({'message': 'Invalid form submission'}), 400)
        data = request.get_json()
        required_fields = ['firstname', 'lastname', 'email', 'password', 'address', 'username', 'phone']
        if not all(k in data for k in required_fields):
            return make_response(jsonify({
                'message': 'Missing required fields'
            }), 400)

        if User.query.filter_by(email=data['email']).first() or User.query.filter_by(
                username=data['username']).first():
            return make_response(jsonify({'message': 'Email or username already exists'}), 400)

        user_to_create = User(
            firstname=data['firstname'],  # Map 'name' to 'username',
            lastname=data['lastname'],
            username=data['username'],
            email=data['email'],  # Map 'email' to 'email_address'
            address=data['address'],
            phone=data['phone']
        )
        user_to_create.set_password(data['password'])
        db.session.add(user_to_create)
        db.session.commit()
        access_token = create_access_token(identity=user_to_create.id)
        return make_response(jsonify({
            'message': f'Account created successfully, Welcome {user_to_create.username}',
            'access_token': access_token,
            'user': {
                'username': user_to_create.username,
                'email': user_to_create.email
            }
        }), 201)

    except IntegrityError:
        db.session.rollback()
        return make_response(jsonify({
            'message': 'Email or username already exists'
        }), 400)

    except Exception as e:
        db.session.rollback()
        print(f'Error: {str(e)}')
        return make_response(jsonify({
            'message': 'Error creating user',
            'error': str(e)
        }), 500)


@app.route('/api/search', methods=['GET'])
def search_products():
    """Search for products based on query parameters with filtering, sorting, and pagination.

        Retrieves products matching the provided search criteria, including optional filters for
        category, price range, and sorting preferences. Results are paginated and include category names.

        Args:
            request.args (dict): Query parameters:
                - q (str, optional): Search term to match against product name or description. Default: ''.
                - category_id (int, optional): Filter by category ID.
                - min_price (float, optional): Minimum price filter.
                - max_price (float, optional): Maximum price filter.
                - page (int, optional): Page number for pagination. Default: 1.
                - per_page (int, optional): Number of products per page. Default: 10.
                - sort_by (str, optional): Field to sort by ('price', 'created_at', 'name'). Default: 'created_at'.
                - sort_order (str, optional): Sort direction ('asc' or 'desc'). Default: 'desc'.
        Returns:
        tuple: A JSON response and HTTP status code.
            - On success (200): {
                "success": True,
                "products": [product_dict, ...],
                "total": int,
                "pages": int,
                "current_page": int
              }
              where product_dict includes product details (from convert_to_dict()) plus 'category_name'.
              Example: {
                "success": True,
                "products": [{"id": 1, "name": "Zebra Shirt", "price": 19.99, "category_name": "Clothing"}],
                "total": 1,
                "pages": 1,
                "current_page": 1
              }
            - On invalid pagination (200): {
                "success": True,
                "products": [],
                "total": 0,
                "pages": 0,
                "current_page": int
              }
            - On error (500): {"success": False, "error": str}

    Raises:
        Exception: For unexpected errors during query execution or database access.
    Notes:
        - Assumes Product and Category models with a convert_to_dict() method on Product.
        - Uses SQLAlchemy for querying and pagination.
        - Case-insensitive search with ILIKE for name and description.
    """

    try:
        # Get query parameters
        query = request.args.get('q', '')
        category_id = request.args.get('category_id', type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'created_at')  # Options: price, created_at, name
        sort_order = request.args.get('sort_order', 'desc')  # asc or desc

        # Validate pagination parameters
        if page < 1 or per_page < 1:
            return jsonify({
                'success': True,
                'products': [],
                'total': 0,
                'pages': 0,
                'current_page': page
            })

        # Base query with join to category
        search_query = Product.query.join(Category)

        # Apply search term filter
        if query:
            search_term = f'%{query}%'
            search_query = search_query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        # Apply category filter
        if category_id:
            search_query = search_query.filter(Product.category_id == category_id)

        # Apply price filters
        if min_price is not None:
            search_query = search_query.filter(Product.price >= min_price)
        if max_price is not None:
            search_query = search_query.filter(Product.price <= max_price)

        # Apply sorting
        sort_column = {
            'price': Product.price,
            'created_at': Product.created_at,
            'name': Product.name
        }.get(sort_by, Product.created_at)

        if sort_order.lower() == 'asc':
            search_query = search_query.order_by(sort_column.asc())
        else:
            search_query = search_query.order_by(sort_column.desc())

        # Apply pagination
        pagination = search_query.paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items

        # Format results using your convert_to_dict method
        results = [product.convert_to_dict() for product in products]

        # Add category name to results
        for product in results:
            category = db.session.get(Category, product['category_id'])
            product['category_name'] = category.name if category else None

        return jsonify({
            'success': True,
            'products': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/login', methods=['POST'])
def account_login():
    """Authenticate a user and return an access token upon successful login.

        Expects a JSON payload with username and password. Validates credentials against the database
        and issues an access token if correct.

        Args:
            request.json (dict): JSON payload containing:
                - username (str): The user's username.
                - password (str): The user's password.

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {
                    "message": str,
                    "access_token": str,
                    "user": {"username": str}
                  }
                  Example: {
                    "message": "you have been logged in, welcome jdoe",
                    "access_token": "jwt_token_here",
                    "user": {"username": "jdoe"}
                  }
                - On failure (401): {"message": "Invalid credentials"}

        Notes:
            - Assumes the User model has a check_password_correction() method for password verification.
            - Uses Flask-JWT-Extended for access token generation via create_access_token().
            - Does not handle exceptions explicitly; assumes JSON parsing errors result in a 400 from Flask.
        """
    user_data = request.get_json(silent=True)
    if not user_data or 'username' not in user_data or 'password' not in user_data:
        return make_response(jsonify({'message': 'Invalid request'}), 400)
    username = user_data['username']
    password = user_data['password']
    user_to_login = User.query.filter_by(username=username).first()
    if user_to_login and user_to_login.check_password_correction(attempted_password=password):
        access_token = create_access_token(identity=str(user_to_login.id))
        return make_response(jsonify({'message': f'you have been logged in, welcome {user_to_login.username}',
                                      'access_token': access_token,
                                      'user': {'username': user_to_login.username}}), 200)
    return make_response(jsonify({'message': 'Invalid credentials'}), 401)

@app.route('/logout', methods=['GET'])
@jwt_required()
def logout_page():
    """Log out the authenticated user.

    Requires a valid JWT token in the Authorization header. Verifies the token’s identity
    but does not currently blacklist the token.

    Returns:
        tuple: A JSON response and HTTP status code.
            - On success (200): {"message": "You have been logged out successfully"}
            - On unauthorized (403): {"message": "Unauthorized access"} (if identity check fails)
            - On error (500): {"message": "Error during logout: <error>"}

    Notes:
        - Token blacklisting (e.g., via Redis) is not implemented here but could be added.
    """
    current_user_id = int(get_jwt_identity())  # Get the user ID from the token
    try:
        # For now, no specific user lookup or blacklisting; just confirm identity is valid
        user = User.query.get_or_404(current_user_id)  # Optional: Verify user exists
        # Future enhancement: Blacklist the token here (e.g., store jti in Redis)
        return jsonify({'message': 'You have been logged out successfully'}), 200

    except Exception as e:
        return jsonify({'message': f'Error during logout: {str(e)}'}), 500


@app.route('/profile/<int:user_id>', methods=['PUT'])
@jwt_required()
def profile_page(user_id):
    """Update the authenticated user's profile.

        Requires a valid JWT token in the Authorization header. Updates the user’s profile details
        if the token’s identity matches the provided user_id. Allows partial updates to username,
        email, address, phone, and password.

        Args:
            user_id (int): The ID of the user to update, extracted from the URL.

        Request:
            request.json (dict): JSON payload with optional fields:
                - username (str): New username (defaults to current if omitted).
                - email (str): New email address (defaults to current if omitted).
                - address (str): New address (defaults to current if omitted).
                - phone (str): New phone number (defaults to current if omitted).
                - password (str): New password (hashed via set_password if provided).

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {"message": "Profile updated successfully"}
                  Example: {"message": "Profile updated successfully"}
                - On unauthorized (403): {"message": "Unauthorized access"}
                - On error (500): {"message": "Error updating profile: <error>"}

        Raises:
            Exception: For database errors or unexpected issues during update.

        Notes:
            - Requires Flask-JWT-Extended for JWT authentication.
            - Uses User.query.get_or_404(), which raises a 404 if the user_id is invalid (caught as an Exception).
            - Updates the 'updated_at' field to the current UTC time on success.
        """
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized access'}), 403
    try:
        user_data = request.get_json()
        user = User.query.get_or_404(user_id)
        user.username = user_data.get('username', user.username)
        user.email = user_data.get('email', user.email)
        user.address = user_data.get('address', user.address)
        user.phone = user_data.get('phone', user.phone)

        if 'password' in user_data:
            user.set_password(user_data['password'])

        user.updated_at = datetime.utcnow()

        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating profile: {str(e)}'}), 500


FLUTTERWAVE_SECRET_KEY = 'FLWSECK_TEST-c559611b2da9d557e7854416e17cb208-X'
FLUTTERWAVE_PUBLIC_KEY = 'FLWPUBK_TEST-94f249780c523996043addef2efe367c-X'
FLUTTERWAVE_BASE_URL = 'https://api.flutterwave.com/v3'


@app.route('/api/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart_page():
    """Add a product to the authenticated user's cart.

        Requires a valid JWT token in the Authorization header. Adds a specified quantity of a product
        to the user’s cart if the product exists and has sufficient stock.

        Request:
            request.json (dict): JSON payload with required fields:
                - product_id (int): The ID of the product to add to the cart.
                - quantity (int): The number of items to add.

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (201): {
                    "message": "Item added to cart",
                    "cart_item": dict
                  }
                  Example: {
                    "message": "Item added to cart",
                    "cart_item": {"id": 1, "user_id": 1, "product_id": 2, "quantity": 3}
                  }
                - On missing fields (400): {"message": "Missing required fields"}
                - On product not found (404): {"message": "Product not found"}
                - On insufficient stock (400): {"message": "Insufficient stock"}

        Notes:
            - Requires Flask-JWT-Extended for JWT authentication.
            - Assumes the CartItem model has a convert_to_dict() method for serialization.
            - Does not handle exceptions explicitly beyond stock and product checks.
        """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if 'product_id' not in data or 'quantity' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    # quantity = data.get('quantity', 1)  # Default to 1 if not provided
    if product.stock < data['quantity']:
        return jsonify({'message': 'Insufficient stock'}), 400
    try:
        cart_item = CartItem(user_id=current_user_id, product_id=data['product_id'], quantity=data['quantity'])
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item added to cart',
                        'cart_item': cart_item.convert_to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding to cart: {str(e)}'}), 500


@app.route('/api/cart/get', methods=['GET'])
@jwt_required()
def get_cart_items():
    """Retrieve all items in the authenticated user's cart.

        Requires a valid JWT token in the Authorization header. Returns a list of cart items
        associated with the authenticated user.

        Returns:
            tuple: A JSON response and HTTP status code 200.
                - Response: List of cart item dictionaries.
                  Example: [
                    {"id": 1, "user_id": 1, "product_id": 2, "quantity": 3},
                    {"id": 2, "user_id": 1, "product_id": 3, "quantity": 1}
                  ]
                - If empty: [] (empty list)

        Notes:
            - Requires Flask-JWT-Extended for JWT authentication.
            - Assumes the CartItem model has a convert_to_dict() method for serialization.
            - Returns an empty list if no cart items exist for the user.
        """
    current_user_id = get_jwt_identity()
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user_id).all()
        return jsonify([item.convert_to_dict() for item in cart_items]), 200
    except Exception as e:
        return jsonify({'message': f'Error retrieving cart items: {str(e)}'}), 500


@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    """Remove a specific item from the authenticated user's cart.

        Requires a valid JWT token in the Authorization header. Deletes the cart item with the
        specified ID if it belongs to the authenticated user.

        Args:
            item_id (int): The ID of the cart item to delete, extracted from the URL.

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {"message": "Item has been removed"}
                  Example: {"message": "Item has been removed"}
                - On not found or unauthorized (404): Automatically raised by first_or_404()

        Notes:
            - Requires Flask-JWT-Extended for JWT authentication.
            - Uses CartItem.query.filter_by().first_or_404() to ensure the item exists and belongs to the user.
            - Does not handle additional exceptions beyond the 404 check.
        """
    current_user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user_id).first_or_404()  # Ensure user owns item
    try:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item has been removed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error removing item: {str(e)}'}), 500


@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order_page():
    """Create an order from the authenticated user's cart and initialize payment.

    Requires a valid JWT token in the Authorization header. Converts the user’s cart items into
    an order, calculates the total amount including delivery fee, and initiates a payment request
    via Flutterwave. Cart clearing is deferred to payment verification.

    Request:
        request.json (dict): JSON payload with required and optional fields:
            - shipping_address (str): The delivery address for the order (required).
            - email (str, optional): Customer email (defaults to user’s email).
            - phone (str, optional): Customer phone number (defaults to user’s phone).

    Returns:
        tuple: A JSON response and HTTP status code.
            - On success (201): {
                "message": "Order created",
                "order": {
                    "id": int,
                    "total_amount": float,
                    "status": str,
                    "created_at": str,
                    "items": [{"id": int, "product_id": int, "price": float, "quantity": int}, ...]
                },
                "payment_link": str
              }
            - On empty cart (400): {"message": "Cart is empty"}
            - On missing shipping_address (400): {"message": "shipping_address is required"}
            - On invalid request (400): {"message": "Invalid request body"}
            - On payment failure (varies): {"error": "Payment initialization failed"}
            - On error (500): {"message": "Error creating order: <error>"}

    Notes:
        - Requires Flask-JWT-Extended for JWT authentication and the requests library for Flutterwave API calls.
        - Delivery fee is fixed at 7000 NGN if cart is non-empty.
        - Cart is not cleared here; defer to payment verification (e.g., /api/verify-payment).
        - Assumes FLUTTERWAVE_SECRET_KEY and FLUTTERWAVE_BASE_URL are configured in the app.
    """
    current_user_id = get_jwt_identity()
    try:
        current_user = User.query.get(current_user_id)
        cart_items = CartItem.query.filter_by(user_id=current_user_id).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid request body'}), 400

        if 'shipping_address' not in data:
            return jsonify({'message': 'shipping_address is required'}), 400

        total_cost = sum(item.product.price * item.quantity for item in cart_items)
        delivery_fee = 7000 if cart_items else 0
        total_amount = total_cost + delivery_fee

        cost_breakdown = {
            'Total amount of Items': total_cost,
            'Delivery fee': delivery_fee,
            'Total amount': total_amount
        }

        tx_ref = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        payment_data = {
            "tx_ref": tx_ref,
            "amount": total_amount,
            "currency": "NGN",
            "redirect_url": "http://localhost:3000/payment-callback",
            "payment_options": "card,banktransfer",
            "customer": {
                "email": data.get('email', current_user.email),
                "phonenumber": data.get('phone', current_user.phone),
                "name": f"{current_user.firstname} {current_user.lastname}"
            },
            "customizations": {
                "title": "Store Order Payment",
                "description": "Payment for items in cart"
            }
        }

        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{FLUTTERWAVE_BASE_URL}/payments",
            json=payment_data,
            headers=headers
        )

        if response.status_code == 200:
            payment_response = response.json()
            order = Order(
                total_amount=total_amount,
                payment_ref=tx_ref,
                status='Pending',
                shipping_address=data.get('shipping_address', current_user.address),
                owner=current_user_id
            )
            db.session.add(order)
            db.session.commit()

            for cart_item in cart_items:
                order_item = OrderItem(
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    order_id=order.id,
                    product_id=cart_item.product_id
                )
                db.session.add(order_item)
            db.session.commit()

            return jsonify({
                'message': 'Order created',
                'order': {
                    'id': order.id,
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'items': [{'id': item.id,
                               'product_id': item.product_id,
                               'price': item.price,
                               'quantity': item.quantity}
                              for item in order.order_items]
                },
                'payment_link': payment_response['data']['link']
            }), 201
        else:
            return jsonify({'error': 'Payment initialization failed'}), response.status_code

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating order: {str(e)}'}), 500

@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Retrieve all orders for the authenticated user.

        Requires a valid JWT token in the Authorization header. Returns a list of orders
        owned by the authenticated user, including details of each order and its items.

        Returns:
            tuple: A JSON response and HTTP status code 200.
                - Response: {"orders": [order_dict, ...]}
                  where order_dict contains:
                    - id (int): Order ID.
                    - total_amount (float): Total cost of the order.
                    - status (str): Order status (e.g., 'Pending').
                    - created_at (str): ISO-formatted creation timestamp.
                    - items (list): List of order item dictionaries with id, product_id, price, and quantity.
                  Example: {
                    "orders": [{
                      "id": 1,
                      "total_amount": 17000.0,
                      "status": "Pending",
                      "created_at": "2025-04-07T12:00:00",
                      "items": [{"id": 1, "product_id": 2, "price": 10000.0, "quantity": 1}]
                    }]
                  }
                - If no orders: {"orders": []} (empty list)

        Notes:
            - Requires Flask-JWT-Extended for JWT authentication.
            - Filters orders by the owner field matching the authenticated user’s ID.
            - Assumes Order model has an order_items relationship for item details.
        """
    current_user_id = get_jwt_identity()
    try:
        orders = Order.query.filter_by(owner=current_user_id).all()
        return jsonify({'orders': [{
            'id': order.id,
            'total_amount': order.total_amount,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'items': [{'id': item.id,
                       'product_id': item.product_id,
                       'price': item.price,
                       'quantity': item.quantity} for item in order.order_items]
        } for order in orders]}), 200
    except Exception as e:
        return jsonify({'message': f'Error retrieving orders: {str(e)}'}), 500


# Payment verification endpoint
@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    """Verify a payment transaction and update the corresponding order status.

        Expects a JSON payload with a transaction reference (tx_ref). Queries the Flutterwave API to
        verify the payment status and updates the associated order to 'completed' if successful.

        Request:
            request.json (dict): JSON payload with required field:
                - tx_ref (str): The transaction reference to verify.

        Returns:
            tuple: A JSON response and HTTP status code.
                - On success (200): {"message": "Payment verified successfully"}
                  Example: {"message": "Payment verified successfully"}
                - On order not found (404): {"error": "Order not found"}
                - On unsuccessful payment (400): {"error": "Payment not successful"}
                - On verification failure (varies): {"error": "Payment verification failed"}

        Notes:
            - Requires the requests library for Flutterwave API calls.
            - Assumes FLUTTERWAVE_SECRET_KEY and FLUTTERWAVE_BASE_URL are configured in the app.
            - Updates order status to 'completed' if payment is verified; does not clear cart items by default.
            - Does not require JWT authentication (public endpoint).
        """
    try:
        data = request.get_json()
        if not data or 'tx_ref' not in data:
            return jsonify({'error': 'Missing tx_ref'}), 400
        tx_ref = data['tx_ref']

        headers = {"Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}"}
        response = requests.get(
            f"{FLUTTERWAVE_BASE_URL}/transactions/verify_by_reference?tx_ref={tx_ref}",
            headers=headers
        )

        if response.status_code == 200:
            verification_data = response.json()
            if verification_data['data']['status'] == 'successful':
                order = Order.query.filter_by(payment_ref=tx_ref).first()
                if order:
                    order.status = 'completed'
                    db.session.commit()
                    return jsonify({'message': 'Payment verified successfully'}), 200
                return jsonify({'error': 'Order not found'}), 404
            return jsonify({'error': 'Payment not successful'}), 400
        return jsonify({'error': 'Payment verification failed'}), response.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error verifying payment: {str(e)}'}), 500
# if __name__ == '__main__':
# app.run(debug=True, port=5000)
