import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.fixture_data import UserWithAccount, UserWithTwoAccounts


@pytest.fixture
def create_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request


@pytest.fixture
def create_credit_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    user_request.role = 'ROLE_CREDIT_SECRET'
    api_manager.admin_steps.create_user(user_request)
    return user_request


@pytest.fixture
def logged_user_with_account(api_manager, create_user_request) -> UserWithAccount:
    api_manager.admin_steps.login_user(create_user_request)
    account = api_manager.user_steps.create_account(create_user_request)
    return UserWithAccount(user_request=create_user_request, account=account)


@pytest.fixture
def logged_user_with_two_accounts(api_manager, create_user_request) -> UserWithTwoAccounts:
    api_manager.admin_steps.login_user(create_user_request)
    first_account = api_manager.user_steps.create_account(create_user_request)
    second_account = api_manager.user_steps.create_account(create_user_request)
    return UserWithTwoAccounts(user_request=create_user_request, first_account=first_account, second_account=second_account)


@pytest.fixture
def logged_credit_user_with_account(api_manager, create_credit_user_request) -> UserWithAccount:
    api_manager.admin_steps.login_user(create_credit_user_request)
    account = api_manager.user_steps.create_account(create_credit_user_request)
    return UserWithAccount(user_request=create_credit_user_request, account=account)


@pytest.fixture
def logged_credit_user_with_two_accounts(api_manager, create_credit_user_request) -> UserWithTwoAccounts:
    api_manager.admin_steps.login_user(create_credit_user_request)
    first_account = api_manager.user_steps.create_account(create_credit_user_request)
    second_account = api_manager.user_steps.create_account(create_credit_user_request)
    return UserWithTwoAccounts(user_request=create_credit_user_request, first_account=first_account, second_account=second_account)