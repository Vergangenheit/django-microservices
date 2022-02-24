import datetime
from typing import Dict

import jwt
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request, Empty

from app import settings
from core.models import User, UserToken
from .authentication import JWTAuthentication
from .serializers import UserSerializer
from rest_framework.serializers import ReturnDict


class RegisterAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Empty = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        email = request.data['email']
        password = request.data['password']
        scope = request.data['scope']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect Password!')

        if user.is_ambassador and scope == 'admin':
            raise exceptions.AuthenticationFailed('Unauthorized')

        token: str = JWTAuthentication.generate_jwt(user.id, scope)

        UserToken.objects.create(
            user_id=user.id,
            token=token,
            created_at=datetime.datetime.utcnow(),
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )

        return Response({
            'jwt': token
        })


class UserAPIView(APIView):

    def get(self, request: Request, scope: str = '') -> Response:

        token = request.COOKIES.get('jwt')

        if not token:
            return None

        payload: Dict = JWTAuthentication.get_payload(token)

        user: User = User.objects.get(pk=payload['user_id'])

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not UserToken.objects.filter(user_id=user.id, token=token,
                                        expired_at__gt=datetime.datetime.utcnow()).exists():
            raise exceptions.AuthenticationFailed('unauthenticated')

        scope_admin_user_ambassador = user.is_ambassador and payload['scope'] != 'ambassador'
        scope_ambassador_user_admin = not user.is_ambassador and payload['scope'] != 'admin'
        scope_path_different = payload['scope'] != scope

        if scope_admin_user_ambassador or scope_ambassador_user_admin or scope_path_different:
            raise exceptions.AuthenticationFailed('Unauthorized')

        return Response(UserSerializer(user).data)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        UserToken.objects.delete(user_id=request.user.id)

        return Response({
            'message': 'success'
        })


class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request: Request, pk=None) -> Response:
        user: User = request.user
        data: Dict = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        user.set_password(data['password'])
        user.save()
        return Response(UserSerializer(user).data)


class UsersAPIView(APIView):
    def get(self, _, pk: str = None) -> Response:
        if pk is None:
            return Response(UserSerializer(User.objects.all(), many=True).data)

        return Response(UserSerializer(User.objects.get(pk=pk)).data)
