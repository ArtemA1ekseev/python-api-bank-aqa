from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_responce import LoginUserResponce


class RequestSpecs:
    BASE_URL = 'http://localhost:4111/api'
    @staticmethod
    def base_headers():
        return {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

    @staticmethod
    def auth_headers(username: str, password: str):
        request = LoginUserRequest(username=username, password=password)
        responce = request.post(
            url='http://localhost:4111/api/auth/token/login',
            json=request.model_dump(),
            headers=RequestSpecs.base_headers()
        )
        if responce.status_code == 200:
            responce_data = LoginUserResponce(**responce.json())
            token = responce_data.token
            headers = RequestSpecs.base_headers()
            headers['Authorization'] = f'Bearer {token}'
            return {
                'headers': headers,
                'base_url': RequestSpecs.BASE_URL
            }
        raise Exception('Failed to login')
