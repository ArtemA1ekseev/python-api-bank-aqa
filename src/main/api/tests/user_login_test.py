import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.db.crud.user_crud import UserCrudDb as User
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse


@pytest.mark.api
class TestUserLogin:
    def test_login_admin(self, api_manager: ApiManager, db_session: Session) -> None:
        login_user_request = LoginUserRequest(username='admin', password='123456')
        response: LoginUserResponse = api_manager.admin_steps.login_user(login_user_request)

        assert login_user_request.username == response.user.username, \
            'Username в ответе при логине администратора не совпадает с отправленным'
        assert response.user.role == 'ROLE_ADMIN', \
            'Role в ответе при логине администратора не равна ROLE_ADMIN'

        user_from_db = User.get_user_by_username(db_session, login_user_request.username)
        assert user_from_db is not None, 'Администратор не найден в БД'
        assert user_from_db.role == 'ROLE_ADMIN', 'Role администратора в БД не равна ROLE_ADMIN'

    def test_login_user(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session
    ) -> None:
        response: LoginUserResponse = api_manager.admin_steps.login_user(create_user_request)

        assert create_user_request.username == response.user.username, \
            'Username в ответе при логине пользователя не совпадает с отправленным'
        assert response.user.role == 'ROLE_USER', \
            'Role в ответе при логине пользователя не равна ROLE_USER'

        user_from_db = User.get_user_by_username(db_session, create_user_request.username)
        assert user_from_db is not None, 'Пользователь не найден в БД'
        assert user_from_db.username == create_user_request.username, \
            'Username пользователя в БД не совпадает с отправленным'
        assert user_from_db.role == 'ROLE_USER', 'Role пользователя в БД не равна ROLE_USER'