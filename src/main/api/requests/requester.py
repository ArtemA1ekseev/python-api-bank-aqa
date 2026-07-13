from abc import ABC, abstractmethod
from typing import Dict, Callable


class BaseRequester(ABC):
    def __init__(self, request_spec: Dict[str, str], response_spec: Callable):
        self.headers = request_spec['headers']
        self.base_url = request_spec['base_url']
        self.response_spec = response_spec


class PostRequester(BaseRequester):
    @abstractmethod
    def post(self, model):
        pass


class GetRequester(BaseRequester):
    @abstractmethod
    def get(self, *args, **kwargs):
        pass
