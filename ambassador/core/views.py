import json
import math
import random
import string
import time
from typing import Dict, List
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import UserService
from .models import Product, Link, Order
from django.core.cache import cache
from django_redis import get_redis_connection
from redis.client import StrictRedis
from app.producer import producer
from .serializers import ProductSerializer, LinkSerializer


class RegisterAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict = request.data
        data['is_ambassador'] = True

        response: Dict = UserService.post(path='register', data=data)

        return Response(response)


class LoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict = request.data
        data['scope'] = 'ambassador'

        res: Dict = UserService.post(path='login', data=data)

        response = Response()
        response.set_cookie(key='jwt', value=res['jwt'], httponly=True)
        response.data = {
            'message': 'success'
        }

        return response


class UserAPIView(APIView):

    def get(self, request: Request) -> Response:
        user = request.user_ms
        orders = Order.objects.filter(user_id=user.get('id'))
        user['revenue'] = sum(order.total for order in orders)

        return Response(user)


class LogoutAPIView(APIView):

    def post(self, request: Request) -> Response:
        UserService.post(path='logout', headers=request.headers)
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        return response


class ProfileInfoAPIView(APIView):

    def put(self, request: Request, pk: str = None) -> Response:
        return Response(UserService.put(path='users/info', data=request.data))


class ProfilePasswordAPIView(APIView):

    def put(self, request: Request, pk: str = None) -> Response:
        return Response(UserService.put(path='users/password', data=request.data))


class ProductFrontendAPIView(APIView):
    @method_decorator(cache_page(60 * 60 * 2, key_prefix='products_frontend'))
    def get(self, _):
        time.sleep(2)
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductBackendAPIView(APIView):

    def get(self, request):
        products = cache.get('products_backend')
        if not products:
            time.sleep(2)
            products = list(Product.objects.all())
            cache.set('products_backend', products, timeout=60 * 30)  # 30 min

        s = request.query_params.get('s', '')
        if s:
            products = list([
                p for p in products
                if (s.lower() in p.title.lower()) or (s.lower() in p.description.lower())
            ])

        total = len(products)

        sort = request.query_params.get('sort', None)
        if sort == 'asc':
            products.sort(key=lambda p: p.price)
        elif sort == 'desc':
            products.sort(key=lambda p: p.price, reverse=True)

        per_page = 9
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * per_page
        end = page * per_page

        data = ProductSerializer(products[start:end], many=True).data
        return Response({
            'data': data,
            'meta': {
                'total': total,
                'page': page,
                'last_page': math.ceil(total / per_page)
            }
        })


class LinkAPIView(APIView):

    def post(self, request: Request) -> Response:
        user: Dict = request.user_ms

        serializer = LinkSerializer(data={
            'user_id': user.get('id'),
            'code': ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
            'products': request.data['products']
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        json_data: str = json.dumps(serializer.data)
        producer.produce('admin_topic', key="link_created", value=json_data)
        producer.produce('checkout_topic', key="link_created", value=json_data)

        return Response(serializer.data)


class StatsAPIView(APIView):

    def get(self, request):
        user: Dict = request.user_ms

        links = Link.objects.filter(user_id=user.get('id'))

        return Response([self.format(link) for link in links])

    def format(self, link):
        orders = Order.objects.filter(code=link.code, complete=1)

        return {
            'code': link.code,
            'count': len(orders),
            'revenue': sum(o.ambassador_revenue for o in orders)
        }


class RankingsAPIView(APIView):

    def get(self, request: Request) -> Response:
        con: StrictRedis = get_redis_connection("default")

        rankings: List = con.zrevrangebyscore('rankings', min=0, max=10000, withscores=True)

        return Response({
            r[0].decode("utf-8"): r[1] for r in rankings
        })
