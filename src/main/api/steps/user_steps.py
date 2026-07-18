from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_transfer_request import AccountTransferRequest
from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def create_account(self, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.requests_created()
        ).post()
        return response

    def account_deposit(self, create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_ok()
        ).post(account_deposit_request)
        return response

    def get_transactions(self, create_user_request: CreateUserRequest, account_id: int):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.GET_TRANSACTIONS,
            ResponseSpecs.request_ok()
        ).get(account_id)
        return response

    def account_deposit_invalid(self, create_user_request, account_deposit_request):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_bad()
        ).post(account_deposit_request)
        return response

    def transfer(self, create_user_request: CreateUserRequest, account_transfer_request: AccountTransferRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.ACCOUNT_TRANSFER,
            ResponseSpecs.request_ok()
        ).post(account_transfer_request)
        return response

    def transfer_invalid(self, create_user_request: CreateUserRequest, account_transfer_request: AccountTransferRequest):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.ACCOUNT_TRANSFER,
            ResponseSpecs.unprocessable_entity()
        ).post(account_transfer_request)
        return response

    def credit_request(self, create_user_request: CreateUserRequest, create_credit_request: CreateCreditRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.requests_created()
        ).post(create_credit_request)
        return response

    def credit_repay(self, create_user_request: CreateUserRequest, credit_repay_request : CreditRepayRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_ok()
        ).post(credit_repay_request)
        return response

    def credit_repay_invalid(self, create_user_request: CreateUserRequest, credit_repay_request : CreditRepayRequest):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.unprocessable_entity()
        ).post(credit_repay_request)
        return response

    def credit_history(self, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_HISTORY,
            ResponseSpecs.request_ok()
        ).get()
        return response

    def credit_request_invalid(self, create_user_request, create_credit_request):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.not_found()
        ).post(create_credit_request)
        return response
