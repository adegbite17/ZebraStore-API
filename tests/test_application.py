import pytest
import json
from flask import url_for
from flask_testing import TestCase
from backend import app, db, User, Product, Category, CartItem, Order, \
    OrderItem  # Adjust import based on your structure
import requests_mock
import os
from datetime import datetime
import psycopg2


# Test client setup
class TestBase(TestCase):
    def create_app(self):
        # database_path = r'C:\Users\USER\sqlite\fazemart.db'
        # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SECRET_KEY'] = 'c6f444bd3ed1'
        app.config['FLUTTERWAVE_SECRET_KEY'] = 'FLWSECK_TEST-c559611b2da9d557e7854416e17cb208-X'
        app.config['FLUTTERWAVE_PUBLIC_KEY'] = 'FLWPUBK_TEST-94f249780c523996043addef2efe367c-X'

        app.config['FLUTTERWAVE_BASE_URL'] = 'https://api.flutterwave.com/v3'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = 'c3dfa3abce72222115a0c31dc73ad885'
        return app

    def setUp(self):
        db.create_all()
        # Add a test user
        self.user = User(
            firstname="John",
            lastname="Doe",
            username="johndoe",
            email="john@example.com",
            address="123 Test St",
            phone='08148827209'
        )
        self.user.set_password("password123")  # Assuming set_password hashes the password
        db.session.add(self.user)
        db.session.commit()

        # Add a test category and product
        self.category = Category(name="Electronics")
        db.session.add(self.category)
        db.session.commit()

        self.product = Product(
            name="Test Product",
            description="A test product",
            price=100.0,
            category_id=self.category.id
        )
        db.session.add(self.product)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def get_token(self):
        response = self.client.post(
            '/login',
            data=json.dumps({'username': 'johndoe', 'password': 'password123'}),
            content_type='application/json'
        )
        return response.json['access_token']


# Test cases
class TestAPI(TestBase):
    def test_favicon(self):
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.status_code, 204)

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Welcome To Zebra Store'})

    def test_products_empty(self):
        Product.query.delete()  # Clear products
        db.session.commit()
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'There are no products available, we are out of stock'})

    def test_products_list(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.json)
        self.assertEqual(len(response.json['products']), 1)
        self.assertEqual(response.json['products'][0]['name'], 'Test Product')

    def test_signup_success(self):
        data = {
            'firstname': 'Jane',
            'lastname': 'Doe',
            'username': 'janedoe',
            'email': 'jane@example.com',
            'address': '456 Test St',
            'password': 'password456',
            'phone': '08148827209'
        }
        response = self.client.post('/signup', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('access_token', response.json)
        self.assertEqual(response.json['message'], 'Account created successfully, Welcome janedoe')

    def test_signup_missing_fields(self):
        data = {'username': 'janedoe', 'password': 'password456'}
        response = self.client.post('/signup', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Missing required fields')

    def test_signup_duplicate(self):
        data = {
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'address': '123 Test St',
            'password': 'password123',
            'phone': '08180246587'
        }
        response = self.client.post('/signup', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Email or username already exists')

    def test_login_success(self):
        data = {'username': 'johndoe', 'password': 'password123'}
        response = self.client.post('/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
        self.assertEqual(response.json['message'], 'you have been logged in, welcome johndoe')

    def test_login_invalid(self):
        data = {'username': 'johndoe', 'password': 'wrongpassword'}
        response = self.client.post('/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid credentials')

    # def test_login_get_method(self):
    #    response = self.client.get('/login')
    #    self.assertEqual(response.status_code, 405)
    #    self.assertEqual(response.json['message'], 'This endpoint only accepts post request in order to login')

    def test_logout(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/logout', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'You have been logged out successfully')

    def test_profile_update(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        data = {'username': 'johnupdated', 'email': 'john.updated@example.com', 'password': 'Deboye10'}
        response = self.client.put(f'/profile/{self.user.id}', data=json.dumps(data), headers=headers,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Profile updated successfully')

    def test_profile_unauthorized(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.put('/profile/999', headers=headers, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json['message'], 'Unauthorized access')

    def test_search_products(self):
        response = self.client.get('/api/search?q=Test&page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(len(response.json['products']), 1)
        self.assertEqual(response.json['products'][0]['name'], 'Test Product')

    def test_search_invalid_pagination(self):
        response = self.client.get('/api/search?page=-1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(response.json['products'], [])

    def test_add_to_cart(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        category = Category(name='Test Category')  # Add category
        db.session.add(category)
        db.session.commit()
        product = Product(name='Test Product', price=10.0, stock=5, category_id=category.id)
        db.session.add(product)
        db.session.commit()
        #cart_item = CartItem(product_id=product.id, quantity=1, user_id=self.user.id)
        #db.session.add(cart_item)
        #db.session.commit()
        data = {'product_id': product.id, 'quantity': 2}
        response = self.client.post('/api/cart/add', data=json.dumps(data), headers=headers,
                                    content_type='application/json')
        print(f"Status: {response.status_code}, Response: {response.get_json()}")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Item added to cart')
        self.assertEqual(response.json['cart_item']['quantity'], 2)

    def test_add_to_cart_missing_fields(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}

        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()
        product = Product(name='Test Product', price=10.0, stock=5, category_id=category.id)
        db.session.add(product)
        db.session.commit()
        data = {'product_id': product.id}
        response = self.client.post('/api/cart/add', data=json.dumps(data), headers=headers,
                                    content_type='application/json')
        print(f"Status: {response.status_code}, Response: {response.get_json()}")  # Debug
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Missing required fields')

    def test_get_cart_items(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()
        product = Product(name='Test Product', price=10.0, stock=5, category_id=category.id)
        db.session.add(product)
        db.session.commit()
        cart_item = CartItem(product_id=product.id, quantity=1, user_id=self.user.id)
        db.session.add(cart_item)
        db.session.commit()
        response = self.client.get('/api/cart/get', headers=headers)
        print(f"Status: {response.status_code}, Response: {response.get_json()}")  # Debug
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_delete_cart_item(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        cart_item = CartItem(product_id=1, quantity=1, user_id=1)
        db.session.add(cart_item)
        db.session.commit()
        response = self.client.delete(f'/api/cart/{cart_item.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Item has been removed')

    def test_create_order(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}

        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()
        product = Product(name='Test Product', price=10.0, stock=5, category_id=category.id)
        db.session.add(product)
        db.session.commit()
        cart_item = CartItem(product_id=product.id, quantity=1, user_id=self.user.id)
        db.session.add(cart_item)
        db.session.commit()
        data = {'shipping_address': '123 Test St'}  # Add required fields

        with requests_mock.Mocker() as m:
            m.post('https://api.flutterwave.com/v3/payments', json={'data': {'link': 'payment-link'}}, status_code=200)
            response = self.client.post('/api/orders', data=json.dumps(data), headers=headers,
                                        content_type='application/json')
            print(f"Status: {response.status_code}, Response: {response.get_json()}")  # Debug
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json['message'], 'Order created')
            self.assertIn('payment_link', response.json)

    def test_create_order_empty_cart(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        # Send a valid payload to reach the cart check
        response = self.client.post('/api/orders',
                                    data=json.dumps({'shipping_address': '123 Test St'}),
                                    headers=headers,
                                    content_type='application/json')
        print(f"Status: {response.status_code}, Response: {response.get_json()}")  # Debug
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Cart is empty')

    def test_get_orders(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        order = Order(total_amount=100.0, payment_ref='test_ref', status='Pending', owner=1,
                      shipping_address='123 Test St')
        db.session.add(order)
        db.session.commit()
        response = self.client.get('/api/orders', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['orders']), 1)

    def test_verify_payment_success(self):
        order = Order(total_amount=100.0, payment_ref='test_ref', status='Pending', owner=1,
                      shipping_address='123 Test St')
        db.session.add(order)
        db.session.commit()

        with requests_mock.Mocker() as m:
            m.get('https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref=test_ref',
                  json={'data': {'status': 'successful'}}, status_code=200)
            response = self.client.post('/api/verify-payment', data=json.dumps({'tx_ref': 'test_ref'}),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['message'], 'Payment verified successfully')

    def test_verify_payment_not_found(self):
        with requests_mock.Mocker() as m:
            m.get('https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref=invalid_ref',
                  json={'data': {'status': 'successful'}}, status_code=200)
            response = self.client.post('/api/verify-payment', data=json.dumps({'tx_ref': 'invalid_ref'}),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json['error'], 'Order not found')


if __name__ == '__main__':
    pytest.main()