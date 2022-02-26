from typing import Callable
from rest_framework.request import Request
from rest_framework.response import Response
from .services import UserService
from typing import Dict


class AuthMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: Request) -> Response:
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        try:
            user: Dict = UserService.get('user/ambassador', headers=request.headers)
        except:
            user = None

        request.user_ms = user

        return self.get_response(request)
