# app/clients.py
import logging
import requests
from typing import List, Optional, Dict
from tenacity import retry, stop_after_attempt, wait_fixed

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ServiceClient:
    def __init__(self):
        self.user_service_url = 'http://user-service:5000'
        self.product_service_url = 'http://product-service:5001'
        self.cart_service_url = 'http://cart-service:5003'

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def validate_user(self, user_id: int, token: str) -> bool:
        try:
            response = requests.get(
                f"{self.user_service_url}/api/users/{user_id}/validate",
                headers={'Authorization': token}
            )
            logger.info(f"Validate user response: {response.status_code}")
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Error validating user: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_product_details(self, product_id: int) -> Optional[Dict]:
        try:
            response = requests.get(f"{self.product_service_url}/api/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            logger.warning(f"Product details response: {response.status_code}, {response.text}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching product details: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_cart_items(self, user_id: int, token: str) -> Optional[List[Dict]]:
        try:
            response = requests.get(
                f"{self.cart_service_url}/api/cart/{user_id}",
                headers={'Authorization': token}
            )
            if response.status_code == 200:
                return response.json().get('items', [])
            logger.warning(f"Cart items response: {response.status_code}, {response.text}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching cart items: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def clear_cart(self, user_id: int) -> bool:
        try:
            response = requests.delete(f"{self.cart_service_url}/api/cart/{user_id}")
            logger.info(f"Clear cart response: {response.status_code}")
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Error clearing cart: {e}")
            return False
