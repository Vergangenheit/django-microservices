from typing import Dict, List
from django.core.management import BaseCommand
from django_redis import get_redis_connection
from redis.client import StrictRedis

from core.services import UserService

from core.models import Order


class Command(BaseCommand):
    def handle(self, *args: List, **options: Dict):
        con: StrictRedis = get_redis_connection("default")

        users: Dict = UserService.get('users')
        ambassadors = filter(lambda a: a['is_ambassador'] == 1, users)

        for ambassador in ambassadors:
            name: str = ambassador['first_name'] + ' ' + ambassador['last_name']
            orders = Order.objects.filter(user_id=ambassador.get('id'))
            revenue = sum(order.total for order in orders)
            con.zadd('rankings', {name: float(revenue)})
