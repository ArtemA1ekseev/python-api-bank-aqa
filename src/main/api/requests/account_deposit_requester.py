from http import HTTPStatus
from typing import Union

import requests
from requests import Response

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_deposit_response import AccountDepositResponse
from src.main.api.requests.requester import PostRequester


class AccountDepositRequester(PostRequester):
    def post(self, account_deposit_request: AccountDepositRequest) -> Union[AccountDepositResponse, Response]:
        url = f'{self.base_url}/account/deposit'
        response = requests.post(
            url=url,
            json=account_deposit_request.model_dump(),
            headers=self.headers,
        )
        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return AccountDepositResponse(**response.json())
        return response
