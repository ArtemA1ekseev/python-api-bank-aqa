from typing import Union

import requests
from requests import Response

from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.requests.requester import PostRequester


class LoginUserRequester(PostRequester):
    def post(self, login_user_requests: LoginUserRequest) -> Union[LoginUserResponse, Response]:
        url = f'{self.base_url}/auth/token/login'
        response = requests.post(
            url=url,
            json=login_user_requests.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return LoginUserResponse(**response.json())
