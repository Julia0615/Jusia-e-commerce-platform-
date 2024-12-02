# intergration_test.py
import pytest
from app.models import CartItem

def test_add_item_to_cart(client, auth_headers):
    # Test adding an item
    response = client.post('/api/cart/items',
        headers=auth_headers,
        json={
            'product_id': 1,
            'price': 99.99,
            'quantity': 2
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['quantity'] == 2
    assert float(data['price']) == 99.99

def test_get_cart(client, auth_headers):
    # Add item first
    client.post('/api/cart/items',
        headers=auth_headers,
        json={
            'product_id': 1,
            'price': 99.99,
            'quantity': 2
        }
    )
    
    # Test getting cart
    response = client.get('/api/cart/1', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) >= 1

def test_update_quantity(client, auth_headers):
    # Add item first
    post_response = client.post('/api/cart/items',
        headers=auth_headers,
        json={
            'product_id': 1,
            'price': 99.99,
            'quantity': 2
        }
    )
    item_id = post_response.get_json()['id']
    
    # Test updating quantity
    response = client.put(f'/api/cart/items/{item_id}',
        headers=auth_headers,
        json={'quantity': 3}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['quantity'] == 3

def test_clear_cart(client, auth_headers):
    response = client.delete('/api/cart/1', headers=auth_headers)
    assert response.status_code == 200