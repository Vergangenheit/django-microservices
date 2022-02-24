import json
import os
import django
from typing import Dict
from confluent_kafka import Consumer
from confluent_kafka.cimpl import Message
from secrets.secrets import sasl_password

from .models import Order, OrderItem

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from .serializers import LinkSerializer


def link_created(data: Dict):
    # TODO remove below
    print(data)
    try:
        serializer = LinkSerializer(data={
            'id': data['id'],
            'user_id': data['user_id'],
            'code': data['code'],
            'products': data['products']
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
    except:
        print('error happened')

def order_created(data: Dict):
    order = Order()
    order.code = data.get('code')
    order.user_id = data.get('user_id')
    order.ambassador_email = data.get('email')
    order.first_name = data['first_name']
    order.last_name = data['last_name']
    order.email = data['email']
    order.address = data['address']
    order.country = data['country']
    order.city = data['city']
    order.zip = data['zip']
    order.save()

    for item in data['order_items']:
        order_item = OrderItem()
        # order_item.id = item['id']
        order_item.order = order
        order_item.product_title = item['product_title']
        order_item.price = item['price']
        order_item.quantity = item['quantity']
        order_item.ambassador_revenue = item['ambassador_revenue']
        order_item.admin_revenue = item['admin_revenue']
        order_item.save()



