from django.core.management import BaseCommand
from random import randrange
from django.db.models.query import QuerySet
from django.db import connections
from core.models import Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        # here we need to use raw swl queries
        with connections['old'].cursor() as cursor:
            cursor.execute("SELECT * FROM core_order WHERE complete = 1")
            orders: QuerySet = cursor.fetchall()

            for order in orders:
                cursor.execute("SELECT * FROM core_orderitem WHERE order_id = '" + str(order[0]) + "' ")
                order_items: QuerySet = cursor.fetchall()

                Order.objects.create(
                    id=order[0],
                    code=order[2],
                    user_id=order[14],
                    total=sum(item[5] for item in order_items)
                )
