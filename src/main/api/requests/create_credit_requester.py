from http import HTTPStatus
from typing import Union

import requests
from requests import Response

from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_credit_response import CreateCreditResponse
from src.main.api.requests.requester import PostRequester


class CreateCreditRequester(PostRequester):
    def post(self, create_credit_request: CreateCreditRequest) -> Union[CreateCreditResponse, Response]:
        url = f'{self.base_url}/credit/request'
        response = requests.post(
            url=url,
            json=create_credit_request.model_dump(),
            headers=self.headers,
        )
        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return CreateCreditResponse(**response.json())
        return response
