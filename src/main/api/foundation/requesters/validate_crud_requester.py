from typing import Optional

import allure

from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.models.base_model import BaseModel

"""
CrudRequester
    |
    | возвращает
    ↓
requests.Response (сырой ответ)


ValidateCrudRequester
    |
    | превращает
    ↓

CreateUserResponse / LoginResponse / AccountResponse
"""
class ValidateCrudRequester(HttpRequester):
    def __init__(self, request_spec, endpoint, response_spec):
        super().__init__(request_spec, endpoint, response_spec)
        self.crud_requester = CrudRequester(
            request_spec=request_spec,
            endpoint=endpoint,
            response_spec=response_spec
        )

    def _validate(self, response) -> BaseModel:
        with allure.step(f"Validated response as {self.endpoint.value.response_model.__name__}"):
            allure.attach(
                f"Validated Model response: {self.endpoint.value.response_model.__name__}",
                "Validation info",
                allure.attachment_type.TEXT
            )
        return self.endpoint.value.response_model.model_validate(response.json())

    def post(self, model: Optional[BaseModel] = None) -> BaseModel:
        response = self.crud_requester.post(model)
        return self._validate(response)

    def delete(self, user_id: int):
        response = self.crud_requester.delete(user_id)
        return self._validate(response)

    def get(self, entity_id: Optional[int] = None) -> BaseModel:
        response = self.crud_requester.get(entity_id)
        return self._validate(response)

