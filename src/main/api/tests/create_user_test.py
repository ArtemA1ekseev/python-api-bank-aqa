import requests
import pytest


class TestCreateUser:
    def test_create_user_valid(self):
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
                "username": "Max434",
                "password": "Pas!sw0rd",
                "role": "ROLE_USER"
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        assert create_user_responce.status_code == 200
        assert create_user_responce.json().get('username') == "Max434"
        assert create_user_responce.json().get('role') == "ROLE_USER"

    @pytest.mark.parametrize(
        'username, password',
        [
            ('абв', 'Pas!sw0rd'),
            ('ab', 'Pas!sw0rd'),
            ('abv!', 'Pas!sw0rd'),
            ('Max111', 'Pas!sw0rф'),
            ('Max112', 'Pas!sw0'),
            ('Max113', 'pas!sw0rd'),
            ('Max113', 'PAS!SW0RD'),
            ('Max113', 'PASSW0RD'),
            ('Max113', 'PAS!SWRD'),

        ]
    )
    def test_create_user_invalid(self, username, password):
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

        token = login_admin_responce.json()['token']
        create_user_responce = requests.post(
            url='http://localhost:4111/api/admin/create',
            json={
                "username": username,
                "password": password,
                "role": "ROLE_USER"
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        assert create_user_responce.status_code == 400
