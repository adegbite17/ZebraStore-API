# test_admin.py
import pytest
import jwt
from datetime import datetime, timedelta
from backend import app, db, User, Order, Product, Category  # Adjust import path
import psycopg2

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # database_path = r'C:\Users\USER\sqlite\fazemart.db'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/ZebraStore'
    app.config['SECRET_KEY'] = 'c6f444bd3ed1'
    app.config['FLUTTERWAVE_SECRET_KEY'] = 'FLWSECK_TEST-c559611b2da9d557e7854416e17cb208-X'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Test data
            admin = User(
                email="admin@example.com", firstname="Admin", lastname="User",
                address="123 Admin St", username="admin", is_admin=True
            )
            admin.set_password("adminpass")  # Use password setter instead of set_password()
            user = User(
                email="user@example.com", firstname="Regular", lastname="User",
                address="456 User St", username="user", is_admin=False
            )
            user.set_password("userpass")  # Use password setter
            db.session.add_all([admin, user])
            db.session.commit()

            category = Category(id=1, name="Electronics", description="Tech stuff")
            product = Product(
                name="Phone", price=299.99, stock=10, description="Smartphone",
                category_id=1, image_url="http://example.com/phone.jpg"
            )
            order = Order(
                total_amount=299.99, status="Pending", shipping_address="123 Admin St",
                owner=admin.id  # Assuming admin.id will be 1 after commit
            )
            db.session.add_all([category, product, order])
            db.session.commit()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture
def admin_token(client):
    with app.app_context():
        admin = User.query.filter_by(email="admin@example.com").first()
        token = jwt.encode(
            {'user_id': admin.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            app.config['SECRET_KEY'], algorithm='HS256'
        )
        return token

@pytest.fixture
def user_token(client):
    with app.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            app.config['SECRET_KEY'], algorithm='HS256'
        )
        return token

def test_admin_login_success(client):
    response = client.post('/admin/login', json={'email': 'admin@example.com', 'password': 'adminpass'})
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Login successful'
    assert 'token' in data

def test_admin_login_invalid_credentials(client):
    response = client.post('/admin/login', json={'email': 'admin@example.com', 'password': 'wrongpass'})
    assert response.status_code == 401
    assert response.get_json()['message'] == 'Invalid credentials or not an admin'

def test_admin_login_missing_fields(client):
    response = client.post('/admin/login', json={'email': 'admin@example.com'})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Email and password are required'

def test_admin_logout(client, admin_token):
    response = client.post('/admin/logout', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Logged out successfully'

def test_admin_logout_no_token(client):
    response = client.post('/admin/logout')
    assert response.status_code == 401
    assert response.get_json()['message'] == 'Token is missing'

def test_update_order_status(client, admin_token):
    response = client.put(
        '/admin/orders/1',
        json={'status': 'Shipped'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Order updated successfully'
    assert data['new_status'] == 'Shipped'
    with app.app_context():
        order = Order.query.get(1)
        assert order.status == 'Shipped'

def test_update_order_status_invalid(client, admin_token):
    response = client.put(
        '/admin/orders/1',
        json={'status': 'Invalid'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Invalid status value'

def test_get_all_orders(client, admin_token):
    response = client.get('/admin/orders', headers={'Authorization': f'Bearer {admin_token}'})
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['orders']) == 1
    assert data['orders'][0]['status'] == 'Pending'
    assert data['total'] == 1

def test_get_all_orders_unauthorized(client, user_token):
    response = client.get('/admin/orders', headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 403
    assert response.get_json()['message'] == 'Admin access required'

def test_updating_product(client, admin_token):
    response = client.put(
        '/admin/products/1',
        json={'name': 'Updated Phone', 'price': 349.99, 'stock': 15},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Product updated successfully'
    with app.app_context():
        product = Product.query.get(1)
        assert product.name == 'Updated Phone'
        assert product.price == 349.99
        assert product.stock == 15

def test_updating_product_invalid_price(client, admin_token):
    response = client.put(
        '/admin/products/1',
        json={'price': -10},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Invalid price'

def test_creating_product(client, admin_token):
    response = client.post(
        '/admin/products',
        json={
            'name': 'New Product', 'price': 99.99, 'stock': 5,
            'description': 'New item', 'category_id': 1
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    data = response.get_json()
    assert response.status_code == 201
    assert data['message'] == 'Product created successfully'
    assert 'product_id' in data
    with app.app_context():
        product = Product.query.get(data['product_id'])
        assert product.name == 'New Product'

def test_creating_product_missing_fields(client, admin_token):
    response = client.post(
        '/admin/products',
        json={'name': 'Incomplete'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Missing required fields'