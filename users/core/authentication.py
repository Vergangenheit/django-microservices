from typing import Dict, Optional

import jwt, datetime
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
from app import settings
from core.models import User, UserToken


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request: Request) -> Optional[User]:
        is_ambassador = 'api/ambassador' in request.path

        token: str = request.COOKIES.get('jwt')

        if not token:
            return None
        
        payload: Dict = JWTAuthentication.get_payload(token)

        if (is_ambassador and payload['scope'] != 'ambassador') or (not is_ambassador and payload['scope'] != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid Scope!')

        user = User.objects.get(pk=payload['user_id'])

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not UserToken.objects.filter(user_id=user.id, token=token, expired_at__gt=datetime.datetime.utcnow()).exists():
            raise exceptions.AuthenticationFailed('unauthenticated')
        return user, None

    @staticmethod
    def get_payload(token: str) -> Optional[Dict]:
        try:
            payload: Dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('unauthenticated')

        return payload

    @staticmethod
    def generate_jwt(id: str, scope) -> str:
        # TODO remove below
        print(f"scope is of type {scope}")
        payload = {
            'user_id': id,
            'scope': scope,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
