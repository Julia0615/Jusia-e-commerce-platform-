#product-service services.py
import boto3
from typing import List, Optional
from decimal import Decimal
from .models import db, Product
import os

class ProductService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET')

    def create_product(self, data: dict, image_file=None) -> Product:
        try:
            product = Product(
                name=data['name'],
                description=data.get('description'),
                price=Decimal(str(data['price'])),
                stock=data['stock'],
                category=data.get('category')
            )

            if image_file:
                image_url = self._upload_image(image_file, product.name)
                product.image_url = image_url

            db.session.add(product)
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise e

    def get_product(self, product_id: int) -> Optional[Product]:
        return db.session.get(Product, product_id)

    def get_all_products(self, category: Optional[str] = None) -> List[Product]:
        query = Product.query
        if category:
            query = query.filter_by(category=category)
        return query.all()

    def update_product(self, product_id: int, data: dict, image_file=None) -> Optional[Product]:
        try:
            product = self.get_product(product_id)
            if not product:
                return None

            for key, value in data.items():
                if hasattr(product, key):
                    if key == 'price':
                        value = Decimal(str(value))
                    setattr(product, key, value)

            if image_file:
                if product.image_url:
                    self._delete_image(product.image_url)
                image_url = self._upload_image(image_file, product.name)
                product.image_url = image_url

            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_product(self, product_id: int) -> bool:
        try:
            product = self.get_product(product_id)
            if not product:
                return False

            if product.image_url:
                self._delete_image(product.image_url)

            db.session.delete(product)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    def check_stock(self, product_id: int, quantity: int) -> bool:
        product = self.get_product(product_id)
        return product is not None and product.stock >= quantity

    def update_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        try:
            product = self.get_product(product_id)
            if not product:
                return None

            new_stock = product.stock + quantity
            if new_stock < 0:
                raise ValueError("Insufficient stock")

            product.stock = new_stock
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise e

    def _upload_image(self, image_file, product_name: str) -> str:
        try:
            file_ext = image_file.filename.split('.')[-1]
            key = f"products/{product_name}/{product_name}.{file_ext}"
            
            self.s3.upload_fileobj(
                image_file,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': image_file.content_type}
            )
            
            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        except Exception as e:
            raise Exception(f"Error uploading image: {str(e)}")

    def _delete_image(self, image_url: str) -> None:
        try:
            key = image_url.split('.amazonaws.com/')[-1]
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        except Exception as e:
            raise Exception(f"Error deleting image: {str(e)}")