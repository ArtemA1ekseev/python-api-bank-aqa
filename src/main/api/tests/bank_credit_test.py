import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_user_request import CreateUserRequest
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
    def test_account_credit_request_valid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateUserRequest,
        credit_amount: int,
        term_months: int,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account = api_manager.user_steps.create_account(create_credit_user_request)
        id_account = response_create_account.id
        assert id_account is not None, 'Счёт не создан, id отсутствует в ответе'

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=credit_amount,
                                                      termMonths=term_months)

        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request,
                                                                       response_credit_request)

        id_credit = response_create_credit.creditId
        assert id_credit is not None, 'Кредит не создан, creditId отсутствует в ответе'
        assert response_create_credit.id == id_account, 'ID счёта в ответе не совпадает с ожидаемым'
        assert response_create_credit.amount == pytest.approx(credit_amount), \
            'Сумма кредита в ответе не совпадает с запрошенной'
        assert response_create_credit.termMonths == term_months, 'Срок кредита в ответе не совпадает с запрошенным'
        assert response_create_credit.balance == pytest.approx(credit_amount), \
            'Баланс кредита в ответе не совпадает с суммой кредита'

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

        assert response_credit_history.userId is not None, 'userId отсутствует в кредитной истории'

        credits = response_credit_history.credits
        assert len(credits) == 1, 'Количество кредитов в истории не равно 1'

        credit = credits[0]
        assert credit.creditId == id_credit, 'ID кредита в истории не совпадает с созданным'
        assert credit.accountId == id_account, 'ID счёта в истории не совпадает с ожидаемым'
        assert credit.amount == pytest.approx(credit_amount), 'Сумма кредита в истории не совпадает с ожидаемой'
        assert credit.termMonths == term_months, 'Срок кредита в истории не совпадает с ожидаемым'
        assert credit.balance == pytest.approx(-credit_amount), 'Баланс кредита в истории не совпадает с ожидаемым'
        assert credit.createdAt is not None, 'Дата создания кредита отсутствует в истории'

        response_account_transactions = api_manager.user_steps.get_transactions(create_credit_user_request, id_account)

        assert response_account_transactions.id == id_account, 'ID счёта в транзакциях не совпадает с ожидаемым'
        assert response_account_transactions.number is not None, 'Номер счёта отсутствует в ответе'
        assert response_account_transactions.balance == pytest.approx(credit_amount), \
            'Баланс счёта после выдачи кредита не совпадает с ожидаемым'

        transactions = response_account_transactions.transactions
        assert len(transactions) == 1, 'Количество транзакций после выдачи кредита не равно 1'

        transaction = transactions[0]
        assert transaction.transactionId is not None, 'ID транзакции отсутствует'
        assert transaction.type == "credit_issuance", 'Тип транзакции не соответствует выдаче кредита'
        assert transaction.amount == pytest.approx(credit_amount), 'Сумма транзакции не совпадает с суммой кредита'
        assert transaction.fromAccountId is None, 'Поле fromAccountId должно быть пустым для выдачи кредита'
        assert transaction.toAccountId == id_account, 'Счёт-получатель транзакции не совпадает с ожидаемым'
        assert transaction.createdAt is not None, 'Дата создания транзакции отсутствует'

        account_from_db = Account.get_account_by_id(db_session, id_account)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == pytest.approx(credit_amount), \
            'Баланс счёта в БД не совпадает с суммой кредита'

        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert credit_from_db is not None, 'Кредит не найден в БД'
        assert credit_from_db.account_id == id_account, 'ID счёта кредита в БД не совпадает с ожидаемым'
        assert credit_from_db.amount == pytest.approx(credit_amount), 'Сумма кредита в БД не совпадает с ожидаемой'
        assert credit_from_db.term_months == term_months, 'Срок кредита в БД не совпадает с ожидаемым'
        assert credit_from_db.balance == pytest.approx(-credit_amount), 'Баланс кредита в БД не совпадает с ожидаемым'

        transactions_from_db = Transaction.get_transactions_by_account_id(db_session, id_account)
        assert len(transactions_from_db) == 1, 'Количество транзакций в БД не равно 1'
        assert transactions_from_db[0].transaction_type == "credit_issuance", \
            'Тип транзакции в БД не соответствует выдаче кредита'

    def test_account_credit_request_invalid_second_credit_while_active(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateUserRequest,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account_first = api_manager.user_steps.create_account(create_credit_user_request)
        id_account_first = response_create_account_first.id
        assert id_account_first is not None, 'Первый счёт не создан, id отсутствует в ответе'

        response_create_account_second = api_manager.user_steps.create_account(create_credit_user_request)
        id_account_second = response_create_account_second.id
        assert id_account_second is not None, 'Второй счёт не создан, id отсутствует в ответе'

        response_credit_request_first = CreateCreditRequest(accountId=id_account_first, amount=5000,
                                                            termMonths=12)
        api_manager.user_steps.credit_request(create_credit_user_request, response_credit_request_first)

        response_credit_request_second = CreateCreditRequest(accountId=id_account_second, amount=5000,
                                                             termMonths=12)
        api_manager.user_steps.credit_request_invalid(create_credit_user_request, response_credit_request_second)

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

        assert len(response_credit_history.credits) == 1, \
            'Количество кредитов в истории не равно 1 — второй кредит не должен был создаться'
        assert response_credit_history.credits[0].accountId == id_account_first, \
            'Единственный кредит в истории должен принадлежать первому счёту'

        credits_second_account_from_db = Credit.get_credits_by_account_id(db_session, id_account_second)
        assert len(credits_second_account_from_db) == 0, \
            'В БД не должно быть кредитов для второго счёта'

    def test_account_credit_repay_valid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateUserRequest,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account = api_manager.user_steps.create_account(create_credit_user_request)
        id_account = response_create_account.id
        assert id_account is not None, 'Счёт не создан, id отсутствует в ответе'

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000,
                                                      termMonths=12)

        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request,
                                                                       response_credit_request)
        id_credit = response_create_credit.creditId
        assert id_credit is not None, 'Кредит не создан, creditId отсутствует в ответе'

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)
        api_manager.user_steps.account_deposit(create_credit_user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account, amount=9000)

        response_credit_repay = api_manager.user_steps.credit_repay(create_credit_user_request, credit_repay_request)

        assert response_credit_repay.amountDeposited == 9000, \
            'Сумма погашения в ответе не совпадает с ожидаемой'
        assert response_credit_repay.creditId == id_credit, 'ID кредита в ответе погашения не совпадает с ожидаемым'

        response_account_transactions = api_manager.user_steps.get_transactions(create_credit_user_request, id_account)

        assert response_account_transactions.balance == pytest.approx(9000), \
            'Баланс счёта после погашения не совпадает с ожидаемым'

        transactions = response_account_transactions.transactions
        assert len(transactions) == 3, 'Количество транзакций после погашения не равно 3'

        repayment_transactions = [t for t in transactions if t.type == "credit_repayment"]
        assert len(repayment_transactions) == 1, 'Количество транзакций погашения не равно 1'

        repayment = repayment_transactions[0]
        assert repayment.amount == pytest.approx(-9000), 'Сумма транзакции погашения не совпадает с ожидаемой'
        assert repayment.fromAccountId == id_account, 'Счёт-отправитель транзакции погашения не совпадает с ожидаемым'
        assert repayment.toAccountId is None, 'Поле toAccountId должно быть пустым для погашения кредита'
        assert repayment.transactionId is not None, 'ID транзакции погашения отсутствует'
        assert repayment.createdAt is not None, 'Дата создания транзакции погашения отсутствует'

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

        credits = response_credit_history.credits
        assert len(credits) == 1, 'Количество кредитов в истории не равно 1'

        credit = credits[0]
        assert credit.creditId == id_credit, 'ID кредита в истории не совпадает с ожидаемым'
        assert credit.balance == pytest.approx(0), 'Баланс кредита после полного погашения должен быть равен 0'

        account_from_db = Account.get_account_by_id(db_session, id_account)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == pytest.approx(9000), 'Баланс счёта в БД не совпадает с ожидаемым'

        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert credit_from_db is not None, 'Кредит не найден в БД'
        assert credit_from_db.balance == pytest.approx(0), 'Баланс кредита в БД после погашения должен быть равен 0'

        transactions_from_db = Transaction.get_transactions_by_account_id(db_session, id_account)
        assert len(transactions_from_db) == 3, 'Количество транзакций в БД не равно 3'

        repayment_from_db = [t for t in transactions_from_db if t.transaction_type == "credit_repayment"]
        assert len(repayment_from_db) == 1, 'Количество транзакций погашения в БД не равно 1'
        assert repayment_from_db[0].credit_id == id_credit, 'ID кредита транзакции погашения в БД не совпадает'

    def test_account_credit_repay_invalid_partial_amount(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateUserRequest,
        db_session: Session
    ):
        api_manager.admin_steps.login_user(create_credit_user_request)

        response_create_account = api_manager.user_steps.create_account(create_credit_user_request)
        id_account = response_create_account.id
        assert id_account is not None, 'Счёт не создан, id отсутствует в ответе'

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000,
                                                      termMonths=12)

        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request,
                                                                       response_credit_request)
        id_credit = response_create_credit.creditId
        assert id_credit is not None, 'Кредит не создан, creditId отсутствует в ответе'

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)

        api_manager.user_steps.account_deposit(create_credit_user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account,
                                                  amount=4000)

        api_manager.user_steps.credit_repay_invalid(create_credit_user_request, credit_repay_request)

        response_credit_history = api_manager.user_steps.credit_history(create_credit_user_request)

        credits = response_credit_history.credits
        assert len(credits) == 1, 'Количество кредитов в истории не равно 1'

        credit = credits[0]
        assert credit.creditId == id_credit, 'ID кредита в истории не совпадает с ожидаемым'
        assert credit.balance == pytest.approx(-9000), \
            'Баланс кредита не должен измениться после отклонённого частичного погашения'

        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert credit_from_db is not None, 'Кредит не найден в БД'
        assert credit_from_db.balance == pytest.approx(-9000), \
            'Баланс кредита в БД не должен измениться после отклонённого частичного погашения'