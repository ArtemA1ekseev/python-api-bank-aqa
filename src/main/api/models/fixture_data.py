from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest


class UserWithAccount(BaseModel):
    user_request: CreateUserRequest
    account: CreateAccountResponse


class UserWithTwoAccounts(BaseModel):
    user_request: CreateUserRequest
    first_account: CreateAccountResponse
    second_account: CreateAccountResponse