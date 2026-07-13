import uuid
import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_transfer_request import AccountTransferRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.requests.account_deposit_requester import AccountDepositRequester
from src.main.api.requests.account_transactions_requester import AccountTransactionsRequester
from src.main.api.requests.account_transfer_requester import AccountTransferRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.login_user_requester import LoginUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestBankAccount:
    @pytest.mark.parametrize(
        "deposit_amount",
        [
            1000,
            1000.5,
            5000,
            9000
        ]
    )
    def test_bank_account_deposit_valid(self, deposit_amount):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_USER')

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        login_user_request = LoginUserRequest(username=username, password='Pas!sw0rd')

        LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_ok()
        ).post(login_user_request)

        response_create_account = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post()

        id_account = response_create_account.id
        assert id_account is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=deposit_amount)

        AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        response_get_transactions = AccountTransactionsRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get(id_account)

        assert response_get_transactions.balance == deposit_amount

        transactions = response_get_transactions.transactions
        assert len(transactions) == 1

        transaction = transactions[0]
        assert transaction.type == "deposit"
        assert transaction.amount == deposit_amount
        assert transaction.toAccountId == id_account
        assert transaction.transactionId is not None
        assert transaction.createdAt is not None

    @pytest.mark.parametrize(
        "invalid_amount",
        [
            -100,
            0,
            1,
            999,
            999.99,
            9001,
            10000
        ]
    )
    def test_bank_account_deposit_invalid_amount_below_minimum(self, invalid_amount):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_USER')

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        login_user_request = LoginUserRequest(username=username, password='Pas!sw0rd')

        LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_ok()
        ).post(login_user_request)

        response_create_account = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post()

        id_account = response_create_account.id
        assert id_account is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=invalid_amount)

        AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_bad()
        ).post(account_deposit_request)

        response_get_transactions = AccountTransactionsRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get(id_account)

        assert response_get_transactions.balance == 0
        assert len(response_get_transactions.transactions) == 0

    @pytest.mark.parametrize(
        "deposit_amount, transfer_amount",
        [
            (1000, 500),
            (5000, 2000),
            (9000, 9000),
        ]
    )
    def test_bank_account_transfer_valid(self, deposit_amount, transfer_amount):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_USER')

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        login_user_request = LoginUserRequest(username=username, password='Pas!sw0rd')

        LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_ok()
        ).post(login_user_request)

        response_create_account_first = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post()

        id_account_first = response_create_account_first.id
        assert id_account_first is not None

        response_create_account_second = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post()

        id_account_second = response_create_account_second.id
        assert id_account_second is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account_first, amount=deposit_amount)

        AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        account_transfer_request = AccountTransferRequest(fromAccountId=id_account_first, toAccountId=id_account_second,
                                                          amount=transfer_amount)

        AccountTransferRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_transfer_request)

        response_get_transactions_first = AccountTransactionsRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get(id_account_first)

        assert response_get_transactions_first.id == id_account_first
        assert response_get_transactions_first.balance == pytest.approx(deposit_amount - transfer_amount)

        transactions = response_get_transactions_first.transactions
        assert len(transactions) == 2

        transfer = next(t for t in transactions if t.type == "transfer_out")
        deposit = next(t for t in transactions if t.type == "deposit")

        assert transfer.amount == pytest.approx(-transfer_amount)
        assert transfer.fromAccountId == id_account_first
        assert transfer.toAccountId == id_account_second
        assert transfer.transactionId is not None
        assert transfer.createdAt is not None

        assert deposit.amount == pytest.approx(deposit_amount)
        assert deposit.fromAccountId is None
        assert deposit.toAccountId == id_account_first
        assert deposit.transactionId is not None
        assert deposit.createdAt is not None

        response_get_transactions_second = AccountTransactionsRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get(id_account_second)

        assert response_get_transactions_second.id == id_account_second
        assert response_get_transactions_second.balance == pytest.approx(transfer_amount)

        transactions = response_get_transactions_second.transactions
        assert len(transactions) == 1

        transaction = transactions[0]
        assert transaction.type == "transfer_in"
        assert transaction.amount == pytest.approx(transfer_amount)
        assert transaction.fromAccountId == id_account_first
        assert transaction.toAccountId == id_account_second
        assert transaction.transactionId is not None
        assert transaction.createdAt is not None

    @pytest.mark.parametrize(
        "transfer_amount",
        [
            500,
            1000,
            5000,
            10000,
        ]
    )
    def test_bank_account_transfer_invalid_insufficient_balance(self, transfer_amount):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_USER')

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        login_user_request = LoginUserRequest(username=username, password='Pas!sw0rd')

        LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_ok()
        ).post(login_user_request)

        response_create_account_first = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post()

        id_account_first = response_create_account_first.id
        assert id_account_first is not None

        response_create_account_second = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post()

        id_account_second = response_create_account_second.id
        assert id_account_second is not None

        account_transfer_request = AccountTransferRequest(fromAccountId=id_account_first, toAccountId=id_account_second,
                                                          amount=transfer_amount)

        AccountTransferRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.unprocessable_entity()
        ).post(account_transfer_request)

        account_transfer_response = AccountTransactionsRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get(id_account_first)

        assert account_transfer_response.balance == 0
        assert len(account_transfer_response.transactions) == 0
