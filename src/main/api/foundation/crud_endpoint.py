from typing import Protocol, Optional, Union

from requests import Response

from src.main.api.models.base_model import BaseModel

"""
Описание интерфейса
Его задача — описать, какие методы обязан иметь любой CRUD Endpoint.
Это называется структурная типизация (structural typing).

Если у класса есть методы post, get, delete с подходящими сигнатурами — 
он автоматически считается совместимым с CrudEndpoint, даже если нигде 
явно не написано class CrudRequester(CrudEndpoint).
"""
class CrudEndpoint(Protocol):
    def post(self, model: Optional[BaseModel]) -> Union[BaseModel, Response]: ...

    def get(self, user_id: int) -> Union[BaseModel, Response]: ...

    def delete(self, user_id: int) -> Union[BaseModel, Response]: ...
