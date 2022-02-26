from typing import Dict

from django.core.cache import cache

from .serializers import LinkSerializer
from .models import Product, Order


def product_created(data: Dict):
    # we create a new product
    Product.objects.create(
        id=data.get('id'),
        title=data.get('title'),
        description=data.get('description'),
        image=data.get('image'),
        price=data.get('price'),
    )


def product_updated(data: Dict):
    product = Product.objects.get(pk=data['id'])

    product.title = data['title']
    product.description = data['description']
    product.image = data['image']
    product.price = data['price']
    product.save()


def product_deleted(data: Dict):
    Product.objects.filter(pk=data).delete()

def link_created(data: Dict):
    print(data)

    serializer = LinkSerializer(data={
        'id': data['id'],
        'user_id': data['user_id'],
        'code': data['code'],
        'products': list(p['id'] for p in data['products'])
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
