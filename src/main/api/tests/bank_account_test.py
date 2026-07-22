import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_transfer_request import AccountTransferRequest
from src.main.api.models.fixture_data import UserWithAccount, UserWithTwoAccounts
from src.main.api.utils.transaction_utils import find_transaction_by_type


@pytest.mark.api
class TestBankAccount:
    @pytest.mark.parametrize(
        "deposit_amount",
        [1000, 1000.5, 5000, 9000]
    )
    def test_bank_account_deposit_valid(
        self,
        api_manager: ApiManager,
        logged_user_with_account: UserWithAccount,
        deposit_amount: float,
        db_session: Session
    ) -> None:
        id_account = logged_user_with_account.account.id

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=deposit_amount)
        api_manager.user_steps.account_deposit(logged_user_with_account.user_request, account_deposit_request)

        response_account_transactions = api_manager.user_steps.get_transactions(
            logged_user_with_account.user_request, id_account
        )
        deposit = find_transaction_by_type(response_account_transactions.transactions, "deposit")

        assert response_account_transactions.balance == pytest.approx(deposit_amount), \
            'Баланс счёта после депозита не совпадает с ожидаемой суммой'
        assert deposit is not None, 'Транзакция депозита не найдена'
        assert deposit.amount == pytest.approx(deposit_amount), 'Сумма транзакции не совпадает с суммой депозита'

        account_from_db = Account.get_account_by_id(db_session, id_account)
        assert account_from_db.balance == pytest.approx(deposit_amount), \
            'Баланс счёта в БД не совпадает с суммой депозита'

    @pytest.mark.parametrize(
        "invalid_amount",
        [-100, 0, 1, 999, 999.99, 9001, 10000]
    )
    def test_bank_account_deposit_invalid_amount(
        self,
        api_manager: ApiManager,
        logged_user_with_account: UserWithAccount,
        invalid_amount: float,
        db_session: Session
    ) -> None:
        id_account = logged_user_with_account.account.id

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=invalid_amount)
        api_manager.user_steps.account_deposit_invalid(logged_user_with_account.user_request, account_deposit_request)

        account_from_db = Account.get_account_by_id(db_session, id_account)
        assert account_from_db.balance == pytest.approx(0), \
            'Баланс счёта в БД должен остаться равным 0 после отклонённого депозита'

    @pytest.mark.parametrize(
        "deposit_amount, transfer_amount",
        [
            (1000, 500),
            (5000, 2000),
            (9000, 9000),
        ]
    )
    def test_bank_account_transfer_valid(
        self,
        api_manager: ApiManager,
        logged_user_with_two_accounts: UserWithTwoAccounts,
        deposit_amount: float,
        transfer_amount: float,
        db_session: Session
    ) -> None:
        user_request = logged_user_with_two_accounts.user_request
        id_account_first = logged_user_with_two_accounts.first_account.id
        id_account_second = logged_user_with_two_accounts.second_account.id

        account_deposit_request = AccountDepositRequest(accountId=id_account_first, amount=deposit_amount)
        api_manager.user_steps.account_deposit(user_request, account_deposit_request)

        account_transfer_request = AccountTransferRequest(
            fromAccountId=id_account_first,
            toAccountId=id_account_second,
            amount=transfer_amount
        )
        api_manager.user_steps.transfer(user_request, account_transfer_request)

        transactions_first = api_manager.user_steps.get_transactions(user_request, id_account_first)
        transfer_out = find_transaction_by_type(transactions_first.transactions, "transfer_out")

        assert transactions_first.balance == pytest.approx(deposit_amount - transfer_amount), \
            'Баланс первого счёта после перевода не совпадает с ожидаемым'
        assert transfer_out is not None, 'Исходящая транзакция перевода не найдена'
        assert transfer_out.amount == pytest.approx(-transfer_amount), \
            'Сумма исходящего перевода не совпадает с ожидаемой'

        transactions_second = api_manager.user_steps.get_transactions(user_request, id_account_second)
        transfer_in = find_transaction_by_type(transactions_second.transactions, "transfer_in")

        assert transactions_second.balance == pytest.approx(transfer_amount), \
            'Баланс второго счёта после перевода не совпадает с ожидаемым'
        assert transfer_in is not None, 'Входящая транзакция перевода не найдена'
        assert transfer_in.amount == pytest.approx(transfer_amount), \
            'Сумма входящего перевода не совпадает с ожидаемой'

        account_first_from_db = Account.get_account_by_id(db_session, id_account_first)
        account_second_from_db = Account.get_account_by_id(db_session, id_account_second)
        assert account_first_from_db.balance == pytest.approx(deposit_amount - transfer_amount), \
            'Баланс первого счёта в БД не совпадает с ожидаемым'
        assert account_second_from_db.balance == pytest.approx(transfer_amount), \
            'Баланс второго счёта в БД не совпадает с ожидаемым'

    @pytest.mark.parametrize(
        "transfer_amount",
        [500, 1000, 5000, 10000]
    )
    def test_bank_account_transfer_invalid_insufficient_balance(
        self,
        api_manager: ApiManager,
        logged_user_with_two_accounts: UserWithTwoAccounts,
        transfer_amount: float,
        db_session: Session
    ) -> None:
        user_request = logged_user_with_two_accounts.user_request
        id_account_first = logged_user_with_two_accounts.first_account.id
        id_account_second = logged_user_with_two_accounts.second_account.id

        account_transfer_request = AccountTransferRequest(
            fromAccountId=id_account_first,
            toAccountId=id_account_second,
            amount=transfer_amount
        )
        api_manager.user_steps.transfer_invalid(user_request, account_transfer_request)

        account_first_from_db = Account.get_account_by_id(db_session, id_account_first)
        assert account_first_from_db.balance == pytest.approx(0), \
            'Баланс первого счёта в БД должен остаться равным 0 после отклонённого перевода'