# from venv import create
#
# import requests
# import pytest
#
# from src.main.api.models.create_user_request import CreateUserRequest
# from src.main.api.models.create_user_responce import CreateUserResponce
# from src.main.api.models.login_user_request import LoginUserRequest
#
#
# @pytest.mark.api
# class TestCreateUser:
#     def test_create_user_valid(self):
#         login_user_request = LoginUserRequest(username='admin', password='123456')
#         login_admin_responce = requests.post(
#             url='http://localhost:4111/api/auth/token/login',
#             json=login_user_request.model_dump(),
#             headers={
#                 'Content-Type': 'application/json',
#                 'accept': 'application/json'
#             }
#         )
#
#         assert login_admin_responce.status_code == 200
#         token = login_admin_responce.json().get('token')
#         create_user_request = CreateUserRequest(username='Max434', password='Pas!sw0rd', role='ROLE_USER')
#         responce = requests.post(
#             url='http://localhost:4111/api/admin/create',
#             json=create_user_request.model_dump(),
#             headers={
#                 'Content-Type': 'application/json',
#                 'Authorization': f'Bearer {token}'
#             }
#         )
#
#         assert responce.status_code == 200
#         create_user_responce = CreateUserResponce(**responce.json())
#         assert create_user_request.username == create_user_responce.username
#         assert create_user_request.role == create_user_responce.role
#
#     @pytest.mark.parametrize(
#         'username, password',
#         [
#             ('абв', 'Pas!sw0rd'),
#             ('ab', 'Pas!sw0rd'),
#             ('abv!', 'Pas!sw0rd'),
#             ('Max111', 'Pas!sw0rф'),
#             ('Max112', 'Pas!sw0'),
#             ('Max113', 'pas!sw0rd'),
#             ('Max113', 'PAS!SW0RD'),
#             ('Max113', 'PASSW0RD'),
#             ('Max113', 'PAS!SWRD'),
#
#         ]
#     )
#     def test_create_user_invalid(self, username, password):
#         login_user_request = LoginUserRequest(username='admin', password='123456')
#         login_admin_responce = requests.post(
#             url='http://localhost:4111/api/auth/token/login',
#             json=login_user_request.model_dump(),
#             headers={
#                 'Content-Type': 'application/json',
#                 'accept': 'application/json'
#             }
#         )
#
#         token = login_admin_responce.json()['token']
#
#         create_user_request = CreateUserRequest(username=username, password=password, role='RoleUSer')
#
#         create_user_responce = requests.post(
#             url='http://localhost:4111/api/admin/create',
#             json=create_user_request.model_dump(),
#             headers={
#                 'Content-Type': 'application/json',
#                 'Authorization': f'Bearer {token}'
#             }
#         )
#
#         assert create_user_responce.status_code == 400
