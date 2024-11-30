# app/models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
from pytz import UTC  # Import pytz for timezone-aware datetime

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='PENDING')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))  # Use pytz.UTC
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def __init__(self, user_id: int, total_amount: float):
        self.user_id = user_id
        self.total_amount = Decimal(str(total_amount))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, product_id: int, quantity: int, price: float):
        self.product_id = product_id
        self.quantity = quantity
        self.price = Decimal(str(price))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': float(self.price),
            'subtotal': float(self.price * self.quantity)
        }
