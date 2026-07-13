from typing import Union

import requests
from requests import Response

from src.main.api.models.account_transactions_response import AccountTransactionsResponse
from src.main.api.requests.requester import GetRequester


class AccountTransactionsRequester(GetRequester):
    def get(self, account_id: int) -> Union[AccountTransactionsResponse, Response]:
        url = f'{self.base_url}/account/transactions/{account_id}'
        response = requests.get(
            url=url,
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code == 200:
            return AccountTransactionsResponse(**response.json())
        return response
