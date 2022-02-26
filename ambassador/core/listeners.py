from typing import Dict

from django.core.cache import cache

from core.models import Product, Order


def clear_cache():
    for key in cache.keys('*'):
        if 'products_frontend' in key:
            cache.delete(key)
    cache.delete('products_backend')


def product_created(data: Dict):
    clear_cache()
    # we create a new product
    Product.objects.create(
        id=data.get('id'),
        title=data.get('title'),
        description=data.get('description'),
        image=data.get('image'),
        price=data.get('price'),
    )


def product_updated(data: Dict):
    clear_cache()

    product = Product.objects.get(pk=data['id'])

    product.title = data['title']
    product.description = data['description']
    product.image = data['image']
    product.price = data['price']
    product.save()


def product_deleted(data: Dict):
    clear_cache()
    Product.objects.filter(pk=data).delete()


def order_created(data: Dict):
    order = Order()
    order.id = data['id']
    order.code = data['code']
    order.user_id = data['user_id']
    order.total = sum(item['ambassador_revenue'] for item in data['order_items'])
    order.save()
