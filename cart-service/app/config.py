# app/config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@cart-db:5432/carts')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv('REDIS_URL', 'redis://cart-cache:6379/0')
    SESSION_TYPE = 'redis'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'e1a00e39bd827b47334cff98872e82ac4568ea673115f88b04769f89714d6a1a')