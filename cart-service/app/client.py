#client.py
# app/client.py
import os
import logging
import requests
from typing import Optional, Dict, List
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CartClient:
    def __init__(self):
        self.product_service_url = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:5001')
        self.base_url = os.getenv('CART_SERVICE_URL', 'http://cart-service:5003')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def add_item(self, user_id: int, product_data: Dict, token: str) -> Optional[Dict]:
        try:
            product = self._validate_product(product_data['product_id'], token)
            if not product:
                return None

            response = requests.post(
                f"{self.base_url}/api/cart/items",
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'user_id': user_id,
                    'product_id': product_data['product_id'],
                    'price': product['price'],
                    'quantity': product_data.get('quantity', 1)
                }
            )
            logger.info(f"Add item response: {response.status_code}")
            return response.json() if response.status_code == 201 else None
        except requests.RequestException as e:
            logger.error(f"Error adding item to cart: {e}")
            return None

    def _validate_product(self, product_id: int, token: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.product_service_url}/api/products/{product_id}",
                headers={'Authorization': f'Bearer {token}'}
            )
            return response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            logger.error(f"Error validating product: {e}")
            return None