from typing import List, Dict
from django.core.management import BaseCommand
from random import randrange
from core.models import Product
from django.db.models.query import QuerySet


class Command(BaseCommand):
    def handle(self, *args: List, **options: Dict):
        products: QuerySet = Product.objects.using('old').all()

        for product in products:
            Product.objects.create(
                id=product.id,
                title=product.title,
                description=product.description,
                image=product.image,
                price=product.price
            )
