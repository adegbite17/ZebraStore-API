from . import app, db, bcrypt, jwt
from flask import request, jsonify, make_response
from .models import User, Product, CartItem, Order, OrderItem, Category
# from .forms import FormToRegister, PurchaseItemForm
# from flask_login import login_user, logout_user, login_required
import logging
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import requests
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

logging.basicConfig(level=logging.DEBUG)

@app.route('/favicon.ico')
def favicon():
    return "", 204


@app.route('/')
@app.route('/home')
def home_page_route():
    return jsonify({'message': 'Welcome to fazemart'}), 200


@app.route('/products', methods=['GET'])
def products_route():
    all_items = Product.query.all()
    if not all_items:
        return make_response(jsonify({'message': 'There are no products available, we are out of stock'}), 200)
    # Assuming Product has a to_dict() method for serialization
    return jsonify({'products': [item.convert_to_dict() for item in all_items]}), 200


@app.route('/signup', methods=['POST'])
def signup_route():
    try:
        # Handle JSON payload from the test
        if not request.is_json:
            return make_response(jsonify({'message': 'Invalid form submission'}), 400)
        data = request.get_json()
        required_fields = ['firstname', 'lastname', 'email', 'password', 'address', 'username']
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
            address=data['address']
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
    user_data = request.get_json(silent=True)  # Expect JSON request

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
def logout_page():
    # return redirect(url_for("home_page_route"))
    return make_response(jsonify({'message': 'You are have been logged out successfully'}), 200)


@app.route('/profile/<int:user_id>', methods=['PUT'])
@jwt_required()
def profile_page(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized access'}), 403
    try:
        user_data = request.get_json()
        user = User.query.get_or_404(user_id)
        user.username = user_data.get('username', user.username)
        user.email = user_data.get('email', user.email)
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
    cart_item = CartItem(user_id=current_user_id, product_id=data['product_id'], quantity=data['quantity'])
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item added to cart',
                    'cart_item': cart_item.convert_to_dict()}), 201


@app.route('/api/cart/get', methods=['GET'])
@jwt_required()
def get_cart_items():
    current_user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.convert_to_dict() for item in cart_items]), 200


@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    current_user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user_id).first_or_404()  # Ensure user owns item
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item has been removed'}), 200


@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order_page():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    data = request.get_json()

    cart_items = CartItem.query.filter_by(user_id=current_user_id).all()

    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400


    if 'shipping_address' not in data:
        return jsonify({'message': 'shipping_address is required'}), 400

    total_cost = sum(item.product.price * item.quantity for item in cart_items)
    delivery_fee = 7000 if cart_items else 0
    total_amount = total_cost + delivery_fee

    cost_breakdown = {'Total amount of Items': total_cost,
                      'Delivery fee': delivery_fee,
                      'Total amount': total_amount}

    # Flutterwave payment payload
    tx_ref = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    payment_data = {
        "tx_ref": tx_ref,
        "amount": total_amount,
        "currency": "NGN",
        "redirect_url": "http://localhost:3000/payment-callback",
        "payment_options": "card,banktransfer",
        "customer": {
            "email": data.get('email', current_user.email),
            "phonenumber": data.get('phone', ''),
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
            owner=current_user_id  # Link to current user
        )
        db.session.add(order)
        db.session.commit()
        # Convert cart items to order items
        for cart_item in cart_items:
            order_item = OrderItem(
                quantity=cart_item.quantity,
                price=cart_item.product.price,  # Use product price at time of purchase
                order_id=order.id,
                product_id=cart_item.product_id
            )
            db.session.add(order_item)

        # Clear cart after creating order (optional, move to payment verification if preferred)
        CartItem.query.filter_by(user_id=current_user_id).delete()
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


@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    orders = Order.query.filter_by(owner=current_user_id).all()  # Add user_id filter if needed
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


# Payment verification endpoint
@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    data = request.get_json()
    tx_ref = data.get('tx_ref')

    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}"
    }

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
                # Optionally clear cart items
                db.session.commit()
                return jsonify({'message': 'Payment verified successfully'}), 200
            return jsonify({'error': 'Order not found'}), 404
        return jsonify({'error': 'Payment not successful'}), 400
    return jsonify({'error': 'Payment verification failed'}), response.status_code
# if __name__ == '__main__':
# app.run(debug=True, port=5000)
