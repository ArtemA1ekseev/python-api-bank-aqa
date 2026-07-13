import pytest

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreateUser:
    def test_create_user_valid(self):
        create_user_request = CreateUserRequest(username='Max44141', password='Pas!sw0rd', role='ROLE_USER')

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        assert create_user_request.username == response.username
        assert create_user_request.role == response.role

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
        create_user_request = CreateUserRequest(username=username, password=password, role='RoleUSer')

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_bad()
        ).post(create_user_request)
