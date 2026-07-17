import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest


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
    def test_account_credit_request_valid(self, api_manager, create_credit_user_request, credit_amount, term_months):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account = api_manager.user_steps.create_account(create_credit_user_request)
        id_account = response_create_account.id
        assert id_account is not None

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=credit_amount,
                                                      termMonths=term_months)

        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request,
                                                                       response_credit_request)

        id_credit = response_create_credit.creditId
        assert id_credit is not None
        assert response_create_credit.id == id_account
        assert response_create_credit.amount == pytest.approx(credit_amount)
        assert response_create_credit.termMonths == term_months
        assert response_create_credit.balance == pytest.approx(credit_amount)

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

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

        response_account_transactions = api_manager.user_steps.get_transactions(create_credit_user_request, id_account)

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

    def test_account_credit_request_invalid_second_credit_while_active(self, api_manager, create_credit_user_request):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account_first = api_manager.user_steps.create_account(create_credit_user_request)
        id_account_first = response_create_account_first.id
        assert id_account_first is not None

        response_create_account_second = api_manager.user_steps.create_account(create_credit_user_request)
        id_account_second = response_create_account_second.id
        assert id_account_second is not None

        response_credit_request_first = CreateCreditRequest(accountId=id_account_first, amount=5000,
                                                            termMonths=12)
        api_manager.user_steps.credit_request(create_credit_user_request, response_credit_request_first)

        response_credit_request_second = CreateCreditRequest(accountId=id_account_second, amount=5000,
                                                             termMonths=12)
        api_manager.user_steps.credit_request_invalid(create_credit_user_request, response_credit_request_second)

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

        assert len(response_credit_history.credits) == 1
        assert response_credit_history.credits[0].accountId == id_account_first

    def test_account_credit_repay_valid(self, api_manager, create_credit_user_request):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account = api_manager.user_steps.create_account(create_credit_user_request)
        id_account = response_create_account.id
        assert id_account is not None

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000,
                                                      termMonths=12)

        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request,
                                                                       response_credit_request)
        id_credit = response_create_credit.creditId
        assert id_credit is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)
        api_manager.user_steps.account_deposit(create_credit_user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account, amount=9000)

        response_credit_repay = api_manager.user_steps.credit_repay(create_credit_user_request, credit_repay_request)

        assert response_credit_repay.amountDeposited == 9000
        assert response_credit_repay.creditId == id_credit

        response_account_transactions = api_manager.user_steps.get_transactions(create_credit_user_request, id_account)

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

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

        credits = response_credit_history.credits
        assert len(credits) == 1

        credit = credits[0]
        assert credit.creditId == id_credit
        assert credit.balance == pytest.approx(0)

    def test_account_credit_repay_invalid_partial_amount(self, api_manager, create_credit_user_request):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account = api_manager.user_steps.create_account(create_credit_user_request)
        id_account = response_create_account.id
        assert id_account is not None

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000,
                                                      termMonths=12)

        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request,
                                                                       response_credit_request)
        id_credit = response_create_credit.creditId
        assert id_credit is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)

        api_manager.user_steps.account_deposit(create_credit_user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account,
                                                  amount=4000)

        api_manager.user_steps.credit_repay_invalid(create_credit_user_request, credit_repay_request)

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

        credits = response_credit_history.credits
        assert len(credits) == 1

        credit = credits[0]
        assert credit.creditId == id_credit
        assert credit.balance == pytest.approx(-9000)
