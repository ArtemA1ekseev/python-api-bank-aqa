import uuid

import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.requests.account_deposit_requester import AccountDepositRequester
from src.main.api.requests.account_transactions_requester import AccountTransactionsRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_credit_requester import CreateCreditRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.credit_history_requester import CreditHistoryRequester
from src.main.api.requests.credit_repay_requester import CreditRepayRequester
from src.main.api.requests.login_user_requester import LoginUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestBankCredit:
    @pytest.mark.parametrize(
        "credit_amount, term_months",
        [
            (5000, 12),
            (7000, 24),
            (9000, 36),
        ]
    )
    def test_account_credit_request_valid(self, credit_amount, term_months):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')

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

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=credit_amount,
                                                      termMonths=term_months)

        response_create_credit = CreateCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post(response_credit_request)

        id_credit = response_create_credit.creditId
        assert id_credit is not None
        assert response_create_credit.id == id_account
        assert response_create_credit.amount == pytest.approx(credit_amount)
        assert response_create_credit.termMonths == term_months
        assert response_create_credit.balance == pytest.approx(credit_amount)

        response_credit_history = CreditHistoryRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get()

        assert response_credit_history.userId is not None

        credits = response_credit_history.credits
        assert len(credits) == 1

        credit = credits[0]
        assert credit.creditId == id_credit
        assert credit.accountId == id_account
        assert credit.amount == pytest.approx(credit_amount)
        assert credit.termMonths == term_months
        assert credit.balance == pytest.approx(-credit_amount)
        assert credit.createdAt is not None

        response_account_transactions = AccountTransactionsRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get(id_account)

        assert response_account_transactions.id == id_account
        assert response_account_transactions.number is not None
        assert response_account_transactions.balance == pytest.approx(credit_amount)

        transactions = response_account_transactions.transactions
        assert len(transactions) == 1

        transaction = transactions[0]
        assert transaction.transactionId is not None
        assert transaction.type == "credit_issuance"
        assert transaction.amount == pytest.approx(credit_amount)
        assert transaction.fromAccountId is None
        assert transaction.toAccountId == id_account
        assert transaction.createdAt is not None

    def test_account_credit_request_invalid_second_credit_while_active(self):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')

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

        response_credit_request_first = CreateCreditRequest(accountId=id_account_first, amount=5000,
                                                            termMonths=12)

        CreateCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post(response_credit_request_first)

        response_credit_request_second = CreateCreditRequest(accountId=id_account_second, amount=5000,
                                                             termMonths=12)

        CreateCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.not_found()
        ).post(response_credit_request_second)

        response_credit_history = CreditHistoryRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get()

        assert len(response_credit_history.credits) == 1
        assert response_credit_history.credits[0].accountId == id_account_first

    def test_account_credit_repay_valid(self):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')

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

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000,
                                                      termMonths=12)

        response_create_credit = CreateCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post(response_credit_request)

        id_credit = response_create_credit.creditId
        assert id_credit is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)

        AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account, amount=9000)

        response_credit_repay = CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(credit_repay_request)

        assert response_credit_repay.amountDeposited == 9000
        assert response_credit_repay.creditId == id_credit

        response_account_transactions = AccountTransactionsRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get(id_account)

        assert response_account_transactions.balance == pytest.approx(9000)

        transactions = response_account_transactions.transactions
        assert len(transactions) == 3

        repayment_transactions = [t for t in transactions if t.type == "credit_repayment"]
        assert len(repayment_transactions) == 1

        repayment = repayment_transactions[0]
        assert repayment.amount == pytest.approx(-9000)
        assert repayment.fromAccountId == id_account
        assert repayment.toAccountId is None
        assert repayment.transactionId is not None
        assert repayment.createdAt is not None

        response_credit_history = CreditHistoryRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get()

        credits = response_credit_history.credits
        assert len(credits) == 1

        credit = credits[0]
        assert credit.creditId == id_credit
        assert credit.balance == pytest.approx(0)

    def test_account_credit_repay_invalid_partial_amount(self):
        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')

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

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000,
                                                      termMonths=12)

        response_create_credit = CreateCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.requests_created()
        ).post(response_credit_request)

        id_credit = response_create_credit.creditId
        assert id_credit is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)

        AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account, amount=4000)

        CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.unprocessable_entity()
        ).post(credit_repay_request)

        response_credit_history = CreditHistoryRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).get()

        credits = response_credit_history.credits
        assert len(credits) == 1

        credit = credits[0]
        assert credit.creditId == id_credit
        assert credit.balance == pytest.approx(-9000)
