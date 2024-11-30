#client.py
import logging
import requests
from typing import Optional, Dict, List
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CartClient:
    def __init__(self):
        self.product_service_url = 'http://product-service:5001'
        self.base_url = 'http://cart-service:5003/api'

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def add_item(self, user_id: int, product_data: Dict) -> Optional[Dict]:
        try:
            product = self._validate_product(product_data['product_id'])
            if not product:
                return None

            response = requests.post(
                f"{self.base_url}/cart/items",
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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def update_quantity(self, user_id: int, item_id: int, quantity: int) -> Optional[Dict]:
        try:
            response = requests.put(
                f"{self.base_url}/cart/items/{item_id}",
                json={'quantity': quantity}
            )
            logger.info(f"Update quantity response: {response.status_code}")
            return response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            logger.error(f"Error updating quantity: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_cart(self, user_id: int) -> Optional[Dict]:
        try:
            response = requests.get(f"{self.base_url}/cart/{user_id}")
            if response.status_code == 200:
                return response.json()
            logger.warning(f"Get cart response: {response.status_code}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching cart: {e}")
            return None

    def _validate_product(self, product_id: int) -> Optional[Dict]:
        try:
            response = requests.get(f"{self.product_service_url}/api/products/{product_id}")
            return response.json() if response.status_code == 200 else None
        except requests.RequestException:
            return None