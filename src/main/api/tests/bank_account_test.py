import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_transfer_request import AccountTransferRequest
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestBankAccount:
    @pytest.mark.parametrize(
        "deposit_amount",
        [1000, 1000.5, 5000, 9000]
    )
    def test_bank_account_deposit_valid(self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        deposit_amount: float,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account = api_manager.user_steps.create_account(create_user_request)
        id_account = response_create_account.id
        assert id_account is not None, 'Счёт не создан, id отсутствует в ответе'

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=deposit_amount)
        api_manager.user_steps.account_deposit(create_user_request, account_deposit_request)

        response_account_transactions = api_manager.user_steps.get_transactions(create_user_request, id_account)

        assert response_account_transactions.balance == pytest.approx(deposit_amount), \
            'Баланс счёта после депозита не совпадает с ожидаемой суммой'
        transactions = response_account_transactions.transactions
        assert len(transactions) == 1, 'Количество транзакций после депозита не равно 1'
        transaction = transactions[0]
        assert transaction.type == "deposit", 'Тип транзакции не соответствует депозиту'
        assert transaction.amount == pytest.approx(deposit_amount), 'Сумма транзакции не совпадает с суммой депозита'
        assert transaction.toAccountId == id_account, 'Счёт-получатель транзакции не совпадает с ожидаемым'
        assert transaction.transactionId is not None, 'ID транзакции отсутствует'
        assert transaction.createdAt is not None, 'Дата создания транзакции отсутствует'

        account_from_db = Account.get_account_by_id(db_session, id_account)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == pytest.approx(deposit_amount), \
            'Баланс счёта в БД не совпадает с суммой депозита'

        transactions_from_db = Transaction.get_transactions_by_account_id(db_session, id_account)
        assert len(transactions_from_db) == 1, 'Количество транзакций в БД не равно 1'
        assert transactions_from_db[0].transaction_type == "deposit", \
            'Тип транзакции в БД не соответствует депозиту'

    @pytest.mark.parametrize(
        "invalid_amount",
        [-100, 0, 1, 999, 999.99, 9001, 10000]
    )
    def test_bank_account_deposit_invalid_amount(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        invalid_amount: float,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account = api_manager.user_steps.create_account(create_user_request)
        id_account = response_create_account.id
        assert id_account is not None, 'Счёт не создан, id отсутствует в ответе'

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=invalid_amount)
        api_manager.user_steps.account_deposit_invalid(create_user_request, account_deposit_request)

        response_account_transactions = api_manager.user_steps.get_transactions(create_user_request, id_account)

        assert response_account_transactions.balance == 0, \
            'Баланс счёта должен остаться равным 0 после отклонённого депозита'
        assert len(response_account_transactions.transactions) == 0, \
            'Транзакций быть не должно после отклонённого депозита'

        account_from_db = Account.get_account_by_id(db_session, id_account)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == pytest.approx(0), \
            'Баланс счёта в БД должен остаться равным 0 после отклонённого депозита'

        transactions_from_db = Transaction.get_transactions_by_account_id(db_session, id_account)
        assert len(transactions_from_db) == 0, 'В БД не должно быть транзакций после отклонённого депозита'

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
        create_user_request: CreateUserRequest,
        deposit_amount: float,
        transfer_amount: float,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account_first = api_manager.user_steps.create_account(create_user_request)
        id_account_first = response_create_account_first.id
        assert id_account_first is not None, 'Первый счёт не создан, id отсутствует в ответе'

        response_create_account_second = api_manager.user_steps.create_account(create_user_request)
        id_account_second = response_create_account_second.id
        assert id_account_second is not None, 'Второй счёт не создан, id отсутствует в ответе'

        account_deposit_request = AccountDepositRequest(accountId=id_account_first, amount=deposit_amount)
        api_manager.user_steps.account_deposit(create_user_request, account_deposit_request)

        account_transfer_request = AccountTransferRequest(fromAccountId=id_account_first,
                                                          toAccountId=id_account_second,
                                                          amount=transfer_amount)
        api_manager.user_steps.transfer(create_user_request, account_transfer_request)

        response_get_transactions_first = api_manager.user_steps.get_transactions(create_user_request, id_account_first)
        assert response_get_transactions_first.id == id_account_first, \
            'ID первого счёта в транзакциях не совпадает с ожидаемым'
        assert response_get_transactions_first.balance == pytest.approx(deposit_amount - transfer_amount), \
            'Баланс первого счёта после перевода не совпадает с ожидаемым'

        transactions = response_get_transactions_first.transactions
        assert len(transactions) == 2, 'Количество транзакций первого счёта не равно 2'

        transfer = next(t for t in transactions if t.type == "transfer_out")
        deposit = next(t for t in transactions if t.type == "deposit")

        assert transfer.amount == pytest.approx(-transfer_amount), 'Сумма исходящего перевода не совпадает с ожидаемой'
        assert transfer.fromAccountId == id_account_first, 'Счёт-отправитель перевода не совпадает с ожидаемым'
        assert transfer.toAccountId == id_account_second, 'Счёт-получатель перевода не совпадает с ожидаемым'
        assert transfer.transactionId is not None, 'ID транзакции перевода отсутствует'
        assert transfer.createdAt is not None, 'Дата создания транзакции перевода отсутствует'

        assert deposit.amount == pytest.approx(deposit_amount), 'Сумма депозита не совпадает с ожидаемой'
        assert deposit.fromAccountId is None, 'Поле fromAccountId должно быть пустым для депозита'
        assert deposit.toAccountId == id_account_first, 'Счёт-получатель депозита не совпадает с ожидаемым'
        assert deposit.transactionId is not None, 'ID транзакции депозита отсутствует'
        assert deposit.createdAt is not None, 'Дата создания транзакции депозита отсутствует'

        response_get_transactions_second = api_manager.user_steps.get_transactions(create_user_request,
                                                                                   id_account_second)

        assert response_get_transactions_second.id == id_account_second, \
            'ID второго счёта в транзакциях не совпадает с ожидаемым'
        assert response_get_transactions_second.balance == pytest.approx(transfer_amount), \
            'Баланс второго счёта после перевода не совпадает с ожидаемым'

        transactions = response_get_transactions_second.transactions
        assert len(transactions) == 1, 'Количество транзакций второго счёта не равно 1'

        transaction = transactions[0]
        assert transaction.type == "transfer_in", 'Тип транзакции не соответствует входящему переводу'
        assert transaction.amount == pytest.approx(transfer_amount), 'Сумма входящего перевода не совпадает с ожидаемой'
        assert transaction.fromAccountId == id_account_first, 'Счёт-отправитель входящего перевода не совпадает'
        assert transaction.toAccountId == id_account_second, 'Счёт-получатель входящего перевода не совпадает'
        assert transaction.transactionId is not None, 'ID транзакции входящего перевода отсутствует'
        assert transaction.createdAt is not None, 'Дата создания транзакции входящего перевода отсутствует'

        account_first_from_db = Account.get_account_by_id(db_session, id_account_first)
        assert account_first_from_db is not None, 'Первый счёт не найден в БД'
        assert account_first_from_db.balance == pytest.approx(deposit_amount - transfer_amount), \
            'Баланс первого счёта в БД не совпадает с ожидаемым'

        account_second_from_db = Account.get_account_by_id(db_session, id_account_second)
        assert account_second_from_db is not None, 'Второй счёт не найден в БД'
        assert account_second_from_db.balance == pytest.approx(transfer_amount), \
            'Баланс второго счёта в БД не совпадает с ожидаемым'

        transactions_first_from_db = Transaction.get_transactions_by_account_id(db_session, id_account_first)
        assert len(transactions_first_from_db) == 2, 'Количество транзакций первого счёта в БД не равно 2'

    @pytest.mark.parametrize(
        "transfer_amount",
        [500, 1000, 5000, 10000]
    )
    def test_bank_account_transfer_invalid_insufficient_balance(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        transfer_amount: float,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_user_request)

        response_create_account_first = api_manager.user_steps.create_account(create_user_request)
        id_account_first = response_create_account_first.id
        assert id_account_first is not None, 'Первый счёт не создан, id отсутствует в ответе'

        response_create_account_second = api_manager.user_steps.create_account(create_user_request)
        id_account_second = response_create_account_second.id
        assert id_account_second is not None, 'Второй счёт не создан, id отсутствует в ответе'

        account_transfer_request = AccountTransferRequest(fromAccountId=id_account_first,
                                                          toAccountId=id_account_second,
                                                          amount=transfer_amount)
        api_manager.user_steps.transfer_invalid(create_user_request, account_transfer_request)

        account_transfer_response = api_manager.user_steps.get_transactions(create_user_request, id_account_first)

        assert account_transfer_response.balance == 0, \
            'Баланс первого счёта должен остаться равным 0 после отклонённого перевода'
        assert len(account_transfer_response.transactions) == 0, \
            'Транзакций быть не должно после отклонённого перевода'

        account_first_from_db = Account.get_account_by_id(db_session, id_account_first)
        assert account_first_from_db is not None, 'Первый счёт не найден в БД'
        assert account_first_from_db.balance == pytest.approx(0), \
            'Баланс первого счёта в БД должен остаться равным 0 после отклонённого перевода'

        transactions_from_db = Transaction.get_transactions_by_account_id(db_session, id_account_first)
        assert len(transactions_from_db) == 0, 'В БД не должно быть транзакций после отклонённого перевода'