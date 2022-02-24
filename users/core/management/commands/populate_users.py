from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time
from django.db.models.query import QuerySet

from core.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        users: QuerySet = User.objects.using('old').all()

        for user in users:
            User.objects.create(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password=user.password,
                is_ambassador=user.is_ambassador
            )
