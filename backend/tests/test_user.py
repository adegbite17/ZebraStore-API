import pytest
from backend import app, bcrypt, db
from flask_login import login_user
from backend.models import *
from datetime import datetime
from flask import session
import json
from unittest.mock import patch


@pytest.fixture
def app_fixture():
    # Configure the existing app for testing
    app.config['TESTING'] = True
    database_path = r'C:\Users\USER\sqlite\fazemart.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'  # In-memory database
    app.config['SECRET_KEY'] = 'c6f444bd3ed1'  # Ensure session works
    app.config['FLUTTERWAVE_SECRET_KEY'] = 'FLWSECK_TEST-c559611b2da9d557e7854416e17cb208-X'
    yield app


@pytest.fixture
def db_fixture(app_fixture):
    with app_fixture.app_context():
        db.create_all()  # Create tables
        yield db
        db.drop_all()  # Clean up


@pytest.fixture
def client(app_fixture):
    return app_fixture.test_client()


def test_create_user(client):
    response = client.post('http://127.0.0.1:5000/signup',
                           json={'firstname': 'Michal', 'lastname': 'Uche',
                                 'username': 'KIng',
                                 'email': 'azeezadegbite01@gmail.com',
                                 'address': '181 Kirikiri road olodi apapa, lagos',
                                 'password': 'Deboye10'})
    assert response.status_code == 201
    assert isinstance(response.json, dict)


def test_login_user(client):
    response = client.post('http://127.0.0.1:5000/login', json={'username': 'KIng', 'password': 'Deboye10'})
    assert response.status_code == 201


def test_logout_user(client):
    response = client.get('http://127.0.0.1:5000/logout')
    assert response.status_code == 200


def test_home_page(client):
    response = client.get('http://127.0.0.1:5000/home')
    assert response.status_code == 200


def test_product_route(client):
    class MockUser:
        is_authenticated = True
        is_active = True
        is_anonymous = False
        def get_id(self):
            return "1"

    with app.app_context():
        login_user(MockUser())
    response = client.get('/products')
    assert response.status_code == 200


@pytest.fixture
def test_user(db_fixture):
    user = User(
        id=1,
        username='KIng',
        email='azeezadegbite01@gmail.com',
        password_hash=bcrypt.generate_password_hash('Deboye10').decode('utf-8'),
        firstname='Azeez',
        lastname='Adegbite',
        address='181 Kirikiri road olodi apapa, lagos',
        is_admin=False,
        created_at=datetime.utcnow()
    )
    db_fixture.session.add(user)
    db_fixture.session.commit()
    yield user


def test_profile_page_update_success(client, test_user):
    with client.session_transaction() as sess:
        # Ensure the session persists for the client request
        sess['_user_id'] = str(test_user.id)  # Manually set the user ID in the session

    # Test updating the profile
    update_data = {
        'username': 'Prince',
        'email': 'boye17@icloud.com',
        'password': 'Adeboye10'
    }
    response = client.put('/profile/1', json=update_data, content_type='application/json')

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Profile updated successfully'
    assert data['user_id'] == 1

    # Verify the database was updated
    with app.app_context():
        updated_user = User.query.get(1)
        assert updated_user.username == 'Prince'
        assert updated_user.email == 'boye17@icloud.com'
        assert bcrypt.check_password_hash(updated_user.password_hash, 'Adeboye10')
        assert updated_user.created_at is not None


# Mock Flutterwave response (since we can't hit the real API in tests)
def mock_flutterwave_payment_response(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self._json = {
                "status": "success",
                "data": {"link": "https://mock-payment-link.com"}
            }

        def json(self):
            return self._json

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)


def mock_flutterwave_verify_response(monkeypatch, status="successful"):
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self._json = {
                "status": "success",
                "data": {"status": status}
            }

        def json(self):
            return self._json

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)


@pytest.fixture
def test_product(db_fixture):
    category = Category(id=1, name='New gadgets')
    product = Product(
        name='Phone',
        description='A smartphone',
        price=50000.0,
        stock=10,
        category_id=category.id,
        created_at=datetime.utcnow(),
        image_url='https://res.cloudinary.com/jimshapedcoding/image/upload/v1597332609/android-icon-192x192_ove2a7.png'
    )
    db_fixture.session.add(product)
    db_fixture.session.commit()
    yield product


@pytest.fixture
def login_user(client, test_user, monkeypatch):
    # Mock Flask-Login's current_user
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    monkeypatch.setattr("flask_login.current_user", test_user)
    yield test_user


def test_add_to_cart_page(client, login_user, test_product):
    data = {'product_id': test_product.id, 'quantity': 2}
    response = client.post('/api/cart/add', json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == 'Items added to cart'
    assert json_data['cart_item']['product_id'] == test_product.id
    assert json_data['cart_item']['quantity'] == 2
    assert json_data['cart_item']['product']['name'] == test_product.name


def test_add_to_cart_missing_fields(client, login_user):
    data = {'product_id': 1}  # Missing quantity
    response = client.post('/api/cart/add', json=data)
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Missing required fields'


def test_add_to_cart_invalid_product(client, login_user):
    data = {'product_id': 999, 'quantity': 1}  # Non-existent product
    response = client.post('/api/cart/add', json=data)
    assert response.status_code == 404  # get_or_404 raises 404


def test_get_cart_items(client, login_user, test_product, db_fixture):
    cart_item = CartItem(product_id=test_product.id, quantity=1, user_id=login_user.id)
    db_fixture.session.add(cart_item)
    db_fixture.session.commit()

    response = client.get('/api/cart/get')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['cart_items']) == 1
    assert json_data['cart_items'][0]['product_id'] == test_product.id
    assert json_data['cart_items'][0]['quantity'] == 1


def test_get_cart_items_empty(client, login_user):
    response = client.get('/api/cart/get')
    assert response.status_code == 200
    assert len(response.get_json()['cart_items']) == 0


def test_get_cart_items_unauthenticated(client):
    response = client.get('/api/cart/get')  # No login_user fixture
    assert response.status_code == 401  # Assuming login_required returns 401


def test_delete_item(client, login_user, test_product, db_fixture):
    cart_item = CartItem(product_id=test_product.id, quantity=1, user_id=login_user.id)
    db_fixture.session.add(cart_item)
    db_fixture.session.commit()

    response = client.delete(f'/api/cart/{cart_item.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Item has been removed'
    assert CartItem.query.get(cart_item.id) is None

def test_delete_cart_item_not_found(client, login_user):
    response = client.delete('/api/cart/999')  # Non-existent item
    assert response.status_code == 404  # first_or_404 raises 404

def test_delete_cart_item_unauthenticated(client):
    response = client.delete('/api/cart/1')  # No login_user fixture
    assert response.status_code == 401  # Assuming login_required returns 401


@patch('requests.post')  # Mock Flask's request.post (used in your endpoint)
def test_create_order_success(mock_post, client, login_user, test_product, db_fixture):
    cart_item = CartItem(product_id=test_product.id, quantity=2, user_id=login_user.id)
    db_fixture.session.add(cart_item)
    db_fixture.session.commit()

    # Mock Flutterwave response
    mock_response = type('Response', (), {'status_code': 200, 'json': lambda self: {
        'status': 'success',
        'data': {'link': 'https://flutterwave.com/pay/123'}
    }})()
    mock_post.return_value = mock_response

    data = {'email': 'test@example.com', 'phone': '1234567890',
            'shipping_address': '181 kirikiri road olodi apapa lagos'}
    response = client.post('/api/orders', json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == 'Order created'
    assert json_data['payment_link'] == 'https://flutterwave.com/pay/123'
    assert Order.query.count() == 1
    assert CartItem.query.count() == 0  # Cart cleared

def test_create_order_empty_cart(client, login_user):
    response = client.post('/api/orders', json={})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Cart is empty'


@patch('requests.post')
def test_create_order_payment_failure(mock_post, client, login_user, test_product, db_fixture):
    cart_item = CartItem(product_id=test_product.id, quantity=1, user_id=login_user.id)
    db_fixture.session.add(cart_item)
    db_fixture.session.commit()

    mock_response = type('Response', (), {'status_code': 500, 'json': lambda: {}})()
    mock_post.return_value = mock_response

    response = client.post('/api/orders', json={})
    assert response.status_code == 500
    assert response.get_json()['error'] == 'Payment initialization failed'


def test_get_orders_success(client, login_user, test_product, db_fixture):
    order = Order(total_amount=17000,
                  payment_ref="order_123",
                  status="Pending",
                  owner=login_user.id,
                  shipping_address="181 Kirikiri road olodi apapa")
    db_fixture.session.add(order)
    db_fixture.session.commit()
    order_item = OrderItem(quantity=1, price=1000, order_id=order.id, product_id=test_product.id)
    db_fixture.session.add(order_item)
    db_fixture.session.commit()

    response = client.get('/api/orders', headers={'Accept': 'application/json'})
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response data: {response.get_data(as_text=True)}")

    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['orders']) == 1
    assert json_data['orders'][0]['total_amount'] == 17000
    assert json_data['orders'][0]['items'][0]['product_id'] == test_product.id

def test_get_orders_empty(client, login_user):
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.get_json()['orders']) == 0


@patch('requests.get')  # Mock Flask's request.get
def test_verify_payment_success(mock_get, client, login_user, db_fixture):
    order = Order(total_amount=17000,
                  payment_ref="order_123",
                  status="Pending",
                  owner=login_user.id,
                  shipping_address="181 Kirikiri road olodi apapa")
    db_fixture.session.add(order)
    db_fixture.session.commit()

    mock_response = type('Response', (), {'status_code': 200, 'json': lambda self: {
        'data': {'status': 'successful'}
    }})()
    mock_get.return_value = mock_response

    data = {'tx_ref': 'order_123'}
    response = client.post('/api/verify-payment', json=data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Payment verified successfully'
    updated_order = Order.query.get(order.id)
    assert updated_order.status == 'completed'

@patch('requests.get')
def test_verify_payment_failed(mock_get, client, login_user):
    mock_response = type('Response', (), {'status_code': 200, 'json': lambda self: {
        'data': {'status': 'failed'}
    }})()
    mock_get.return_value = mock_response

    data = {'tx_ref': 'order_123'}
    response = client.post('/api/verify-payment', json=data)
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Payment not successful'