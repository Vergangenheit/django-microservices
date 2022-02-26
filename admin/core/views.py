import json
from typing import Dict
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ProductSerializer, LinkSerializer, OrderSerializer
from .models import Product, Link, Order
from .services import UserService
from django.db.models.query import QuerySet
from app.producer import producer


class RegisterAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict = request.data
        data['is_ambassador'] = False

        response: Dict = UserService.post(path='register', data=data)

        return Response(response)


class LoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict = request.data
        data['scope'] = 'admin'

        res: Dict = UserService.post(path='login', data=data)

        response = Response()
        response.set_cookie(key='jwt', value=res['jwt'], httponly=True)
        response.data = {
            'message': 'success'
        }

        return response


class UserAPIView(APIView):

    def get(self, request: Request) -> Response:
        return Response(request.user_ms)


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


class AmbassadorAPIView(APIView):

    def get(self, _) -> Response:
        users: Dict = UserService.get('users')
        return Response(filter(lambda a: a['is_ambassador'] == 1, users))


class ProductGenericAPIView(
    generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin
):
    queryset: QuerySet = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)

        return self.list(request)

    def post(self, request: Request) -> Response:
        response: Response = self.create(request)
        json_data: str = json.dumps(response.data)
        producer.produce('ambassador_topic', key='product_created', value=json_data)
        producer.produce('checkout_topic', key='product_created', value=json_data)
        return response

    def put(self, request: Request, pk=None) -> Response:
        response: Response = self.partial_update(request, pk)
        json_data: str = json.dumps(response.data)
        producer.produce('ambassador_topic', key='product_updated', value=json_data)
        producer.produce('checkout_topic', key='product_updated', value=json_data)
        return response

    def delete(self, request: Request, pk=None) -> Response:
        response: Response = self.destroy(request, pk)
        json_data: str = json.dumps(response.data)
        producer.produce('ambassador_topic', key='product_deleted', value=json_data)
        producer.produce('checkout_topic', key='product_deleted', value=json_data)
        return response


class LinkAPIView(APIView):

    def get(self, request: Request, pk=None) -> Response:
        links: QuerySet = Link.objects.filter(user_id=pk)
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data)


class OrderAPIView(APIView):

    def get(self, request: Request) -> Response:
        orders: QuerySet = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
