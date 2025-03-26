# test_search.py
import pytest
from backend import app, db, Product, Category
from datetime import datetime


# Pytest fixture for app setup
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add test data
            cat1 = Category(id=1, name="Electronics")
            cat2 = Category(id=2, name="Clothing")
            db.session.add_all([cat1, cat2])

            product1 = Product(
                name="Test Phone",
                description="A smartphone",
                price=299.99,
                stock=10,
                category_id=1,
                created_at=datetime.utcnow(),
                image_url="http://example.com/phone.jpg"
            )
            product2 = Product(
                name="Test Shirt",
                description="Cotton t-shirt",
                price=19.99,
                stock=5,
                category_id=2,
                created_at=datetime.utcnow(),
                image_url="http://example.com/shirt.jpg"
            )
            db.session.add_all([product1, product2])
            db.session.commit()

        yield client

        # Cleanup
        with app.app_context():
            db.session.remove()
            db.drop_all()


def test_basic_search(client):
    """Test basic search functionality"""
    response = client.get('/api/search?q=test')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 2
    assert data['total'] == 2


def test_search_by_name(client):
    """Test searching by specific product name"""
    response = client.get('/api/search?q=phone')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 1
    assert data['products'][0]['name'] == "Test Phone"


def test_search_by_category(client):
    """Test filtering by category_id"""
    response = client.get('/api/search?category_id=1')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 1
    assert data['products'][0]['category_id'] == 1


def test_price_filter(client):
    """Test price range filtering"""
    response = client.get('/api/search?min_price=50&max_price=300')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 1
    assert data['products'][0]['name'] == "Test Phone"


def test_pagination(client):
    """Test pagination functionality"""
    response = client.get('/api/search?page=1&per_page=1')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 1
    assert data['pages'] == 2
    assert data['current_page'] == 1


def test_sorting(client):
    """Test sorting functionality"""
    response = client.get('/api/search?sort_by=price&sort_order=asc')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert data['products'][0]['price'] == 19.99  # Cheaper item first


def test_empty_results(client):
    """Test search with no matching results"""
    response = client.get('/api/search?q=nonexistent')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 0
    assert data['total'] == 0


def test_invalid_parameters(client):
    """Test handling of invalid parameters"""
    response = client.get('/api/search?page=-1')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 0
    assert data['total'] == 0
    assert data['pages'] == 0

    # Additional test for invalid per_page
    response = client.get('/api/search?per_page=-5')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == 0
    assert data['total'] == 0
    assert data['pages'] == 0


def test_response_format(client):
    """Test response includes all expected fields"""
    response = client.get('/api/search?q=phone')
    data = response.get_json()
    product = data['products'][0]

    expected_fields = ['id', 'name', 'description', 'price', 'stock',
                       'category_id', 'created_at', 'image_url', 'category_name']

    assert response.status_code == 200
    assert data['success'] is True
    assert all(field in product for field in expected_fields)


# Example of parameterized test
@pytest.mark.parametrize("query, expected_count", [
    ("phone", 1),
    ("test", 2),
    ("nonexistent", 0),
])
def test_search_variations(client, query, expected_count):
    """Test multiple search terms with expected result counts"""
    response = client.get(f'/api/search?q={query}')
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['products']) == expected_count