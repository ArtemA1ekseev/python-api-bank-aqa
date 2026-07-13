from http import HTTPStatus
from typing import Union

import requests
from requests import Response

from src.main.api.models.account_transfer_request import AccountTransferRequest
from src.main.api.models.account_transfer_response import AccountTransferResponse
from src.main.api.requests.requester import PostRequester


class AccountTransferRequester(PostRequester):
    def post(self, account_transfer_request: AccountTransferRequest) -> Union[AccountTransferResponse, Response]:
        url = f'{self.base_url}/account/transfer'
        response = requests.post(
            url=url,
            json=account_transfer_request.model_dump(),
            headers=self.headers,
        )
        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return AccountTransferResponse(**response.json())
        return response
