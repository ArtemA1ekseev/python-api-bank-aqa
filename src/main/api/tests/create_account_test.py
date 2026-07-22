import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.db.crud.account_crud import AccountCrudDb as Account


@pytest.mark.api
class TestCreateAccount:
    def test_create_account(
        self,
        db_session: Session,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest
    ) -> None:
        response: CreateAccountResponse = api_manager.user_steps.create_account(create_user_request)

        assert response.balance == 0, 'Баланс нового счёта должен быть равен 0 при создании'

        account_from_db = Account.get_account_by_id(db_session, response.id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == pytest.approx(0), 'Баланс счёта в БД должен быть равен 0 при создании'