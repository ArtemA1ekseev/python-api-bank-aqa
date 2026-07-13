from typing import Union

import requests
from requests import Response

from src.main.api.models.credit_history_response import CreditHistoryResponse
from src.main.api.requests.requester import GetRequester


class CreditHistoryRequester(GetRequester):
    def get(self) -> Union[CreditHistoryResponse, Response]:
        url = f'{self.base_url}/credit/history'
        response = requests.get(
            url=url,
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code == 200:
            return CreditHistoryResponse(**response.json())
        return response
