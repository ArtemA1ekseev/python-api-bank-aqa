import requests
import pytest

@pytest.mark.api
class TestCreateAccount:
    def test_create_account(self):
        login_admin_responce = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/json'
            }
        )

        assert login_admin_responce.status_code == 200
        token = login_admin_responce.json().get('token')

        create_user_responce = requests.post(
            url='http://localhost:4111/api/admin/create',
            json={
                "username": "Max2001",
                "password": "Pas!sw0rd",
                "role": "ROLE_USER"
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        assert create_user_responce.status_code == 200

        login_user_responce = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": "Max2001",
                "password": "Pas!sw0rd",
            },
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/json'
            }
        )

        assert login_user_responce.status_code == 200
        token = login_user_responce.json().get('token')

        create_account_responce = requests.post(
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        assert create_account_responce.status_code == 201
        assert create_account_responce.json().get('balance') == 0