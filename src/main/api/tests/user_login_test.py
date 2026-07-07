# import requests
# import pytest
#
# from src.main.api.models.create_user_request import CreateUserRequest
# from src.main.api.models.login_user_request import LoginUserRequest
# from src.main.api.models.login_user_responce import LoginUserResponce
#
#
# @pytest.mark.api
# class TestUserLogin:
#     def test_login_admin(self):
#         login_user_request = LoginUserRequest(username='admin', password='123456')
#         responce = requests.post(
#             url='http://localhost:4111/api/auth/token/login',
#             json=login_user_request.model_dump(),
#             headers={
#                 'Content-Type': 'application/json',
#                 'accept': 'application/json'
#             }
#         )
#
#         assert responce.status_code == 200
#         login_user_responce = LoginUserResponce(**responce.json())
#
#         assert login_user_request.username == login_user_responce.user.username
#         assert login_user_responce.user.role == 'Role_Admin'
#
#     def test_login_user(self):
#         login_user_request = LoginUserRequest(username='admin', password='123456')
#
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
#
#         create_user_request = CreateUserRequest(username='Max1111', password='Pas!sw0rd', role='ROLE_USER')
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
#         assert create_user_responce.status_code == 200
#
#         login_user_request = LoginUserRequest(username='Max1111', password='Pas!sw0rd')
#
#         responce = requests.post(
#             url='http://localhost:4111/api/auth/token/login',
#             json=login_user_request.model_dump(),
#             headers={
#                 'accept': 'application/json',
#                 'Content-Type': 'application/json'
#             }
#         )
#
#         assert responce.status_code == 200
#         login_user_responce = LoginUserResponce(**responce.json())
#
#         assert login_user_request.username == login_user_responce.user.username
#         assert login_user_responce.user.role == 'ROLE_USER'