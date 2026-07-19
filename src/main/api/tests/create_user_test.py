import pytest

from sqlalchemy.orm import Session
from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.db.crud.user_crud import UserCrudDb as User


@pytest.mark.api
class TestCreateUser:
    @pytest.mark.parametrize(
        'create_user_request',
        [RandomModelGenerator.generate(CreateUserRequest)],
    )
    def test_create_user_valid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session
    ) -> None:
        response: CreateUserResponse = api_manager.admin_steps.create_user(create_user_request)

        assert create_user_request.username == response.username, \
            'Username в ответе не совпадает с отправленным при создании пользователя'
        assert create_user_request.role == response.role, \
            'Role в ответе не совпадает с отправленной при создании пользователя'

        user_from_db = User.get_user_by_username(db_session, create_user_request.username)
        assert user_from_db is not None, 'Созданного пользователя нет в БД'
        assert user_from_db.username == create_user_request.username, \
            'Username пользователя в БД не совпадает с отправленным'
        assert user_from_db.role == create_user_request.role, \
            'Role пользователя в БД не совпадает с отправленной'

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
    def test_create_user_invalid(
        self,
        db_session: Session,
        username: str,
        password: str,
        api_manager: ApiManager
    ) -> None:
        create_user_request = CreateUserRequest(username=username, password=password, role='RoleUSer')
        api_manager.admin_steps.create_invalid_user(create_user_request)

        user_from_db = User.get_user_by_username(db_session, create_user_request.username)
        assert user_from_db is None, 'Пользователь создан, хотя запрос был невалидным — ошибка!'