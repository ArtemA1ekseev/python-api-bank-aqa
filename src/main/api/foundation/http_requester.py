from src.main.api.foundation.endpoint import Endpoint
from typing import Dict, Callable


"""
                    HttpRequester
                         ▲
          ┌──────────────┴──────────────┐
          │                             │
          │                             │
   CrudRequester              ValidateCrudRequester
          │                             │
          │                             │
   Отправляет HTTP            Использует CrudRequester,
   запросы                    а затем превращает JSON
                               в объект модели
"""
class HttpRequester:
    def __init__(self, request_spec: Dict, endpoint: Endpoint, response_spec: Callable):
        self.request_spec = request_spec
        self.endpoint = endpoint
        self.response_spec = response_spec