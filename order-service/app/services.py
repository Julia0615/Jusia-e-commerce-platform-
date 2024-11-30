# app/services.py
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from .clients import ServiceClient
from .models import db, Order, OrderItem
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class OrderService:
    def __init__(self):
        self.client = ServiceClient()

    def create_order(self, user_id: int, token: str) -> Optional[Order]:
        try:
            # Validate user
            if not self.client.validate_user(user_id, token):
                raise ValueError("Invalid user or token")

            # Get cart items
            cart_items = self.client.get_cart_items(user_id, token)
            if not cart_items:
                raise ValueError("Cart is empty")

            # Calculate total amount and create order
            total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
            order = Order(user_id=user_id, total_amount=total_amount, status='pending')

            # Add items to the order
            for item in cart_items:
                order_item = OrderItem(
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                order.items.append(order_item)

            # Save the order in a transaction
            with db.session.begin_nested():
                db.session.add(order)
                db.session.commit()

            # Clear the cart
            self.client.clear_cart(user_id)
            return order

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise ve
        except SQLAlchemyError as db_error:
            db.session.rollback()
            logger.error(f"Database error: {db_error}")
            raise db_error
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            db.session.rollback()
            raise e

    def get_order(self, order_id: int, user_id: int) -> Optional[Order]:
        try:
            order = Order.query.filter_by(id=order_id, user_id=user_id).first()
            if not order:
                logger.warning(f"Order not found: order_id={order_id}, user_id={user_id}")
            return order
        except Exception as e:
            logger.error(f"Error retrieving order: {e}")
            return None

    def get_user_orders(self, user_id: int) -> List[Order]:
        try:
            orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
            return orders
        except Exception as e:
            logger.error(f"Error retrieving user orders: {e}")
            return []

    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        try:
            if status not in ['pending', 'processing', 'completed', 'canceled']:
                raise ValueError("Invalid order status")

            order = Order.query.get(order_id)
            if not order:
                logger.warning(f"Order not found: {order_id}")
                return None

            order.status = status
            db.session.commit()
            return order

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise ve
        except SQLAlchemyError as db_error:
            db.session.rollback()
            logger.error(f"Database error: {db_error}")
            raise db_error
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            db.session.rollback()
            raise e
