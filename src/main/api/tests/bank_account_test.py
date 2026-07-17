import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_transfer_request import AccountTransferRequest


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
    def test_bank_account_deposit_valid(self, api_manager, create_user_request, deposit_amount):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account = api_manager.user_steps.create_account(create_user_request)
        id_account = response_create_account.id
        assert id_account is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=deposit_amount)
        api_manager.user_steps.account_deposit(create_user_request, account_deposit_request)

        response_account_transactions = api_manager.user_steps.get_transactions(create_user_request, id_account)

        assert response_account_transactions.balance == pytest.approx(deposit_amount)
        transactions = response_account_transactions.transactions
        assert len(transactions) == 1
        transaction = transactions[0]
        assert transaction.type == "deposit"
        assert transaction.amount == pytest.approx(deposit_amount)
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
    def test_bank_account_deposit_invalid_amount(self, api_manager, create_user_request, invalid_amount):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account = api_manager.user_steps.create_account(create_user_request)
        id_account = response_create_account.id
        assert id_account is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=invalid_amount)
        api_manager.user_steps.account_deposit_invalid(create_user_request, account_deposit_request)

        response_account_transactions = api_manager.user_steps.get_transactions(create_user_request, id_account)

        assert response_account_transactions.balance == 0
        assert len(response_account_transactions.transactions) == 0

    @pytest.mark.parametrize(
        "deposit_amount, transfer_amount",
        [
            (1000, 500),
            (5000, 2000),
            (9000, 9000),
        ]
    )
    def test_bank_account_transfer_valid(self, api_manager, create_user_request, deposit_amount, transfer_amount):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account_first = api_manager.user_steps.create_account(create_user_request)
        id_account_first = response_create_account_first.id
        assert id_account_first is not None

        response_create_account_second = api_manager.user_steps.create_account(create_user_request)
        id_account_second = response_create_account_second.id
        assert id_account_second is not None

        account_deposit_request = AccountDepositRequest(accountId=id_account_first, amount=deposit_amount)
        api_manager.user_steps.account_deposit(create_user_request, account_deposit_request)

        account_transfer_request = AccountTransferRequest(fromAccountId=id_account_first, toAccountId=id_account_second,
                                                          amount=transfer_amount)
        api_manager.user_steps.transfer(create_user_request, account_transfer_request)

        response_get_transactions_first = api_manager.user_steps.get_transactions(create_user_request, id_account_first)
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

        response_get_transactions_second = api_manager.user_steps.get_transactions(create_user_request,
                                                                                   id_account_second)

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
    def test_bank_account_transfer_invalid_insufficient_balance(self, api_manager, create_user_request,
                                                                transfer_amount):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account_first = api_manager.user_steps.create_account(create_user_request)
        id_account_first = response_create_account_first.id
        assert id_account_first is not None

        response_create_account_second = api_manager.user_steps.create_account(create_user_request)
        id_account_second = response_create_account_second.id
        assert id_account_second is not None

        account_transfer_request = AccountTransferRequest(fromAccountId=id_account_first, toAccountId=id_account_second,
                                                          amount=transfer_amount)
        api_manager.user_steps.transfer_invalid(create_user_request, account_transfer_request)

        account_transfer_response = api_manager.user_steps.get_transactions(create_user_request, id_account_first)

        assert account_transfer_response.balance == 0
        assert len(account_transfer_response.transactions) == 0
