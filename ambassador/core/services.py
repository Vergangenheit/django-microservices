import requests
from typing import Dict, List


class UserService:
    endpoint: str = 'http://users-ms:8000/api/'

    @staticmethod
    def get(path: str, **kwargs: Dict) -> Dict:
        headers = kwargs.get('headers', [])
        return requests.get(UserService.endpoint + path, headers=headers).json()

    @staticmethod
    def post(path: str, **kwargs: Dict) -> Dict:
        headers: List = kwargs.get('headers', [])
        data: List = kwargs.get('data', [])
        return requests.post(UserService.endpoint + path, data=data, headers=headers).json()

    @staticmethod
    def put(path: str, **kwargs: Dict) -> Dict:
        headers: List = kwargs.get('headers', [])
        data: List = kwargs.get('data', [])
        return requests.put(UserService.endpoint + path, data=data, headers=headers).json()
