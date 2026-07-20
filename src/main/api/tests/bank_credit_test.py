import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
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
            logged_credit_user_with_account, # добавить
            credit_amount: int,
            term_months: int,
            db_session: Session
    ) -> None:
        create_credit_user_request, account = logged_credit_user_with_account
        id_account = account.id

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=credit_amount, termMonths=term_months)
        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request, response_credit_request)
        id_credit = response_create_credit.creditId

        assert response_create_credit.amount == pytest.approx(credit_amount), \
            'Сумма кредита в ответе не совпадает с запрошенной'

        credit_history = api_manager.user_steps.credit_history(create_credit_user_request)
        credit = next((c for c in credit_history.credits if c.creditId == id_credit), None)
        assert credit is not None, 'Созданный кредит не найден в истории'
        assert credit.balance == pytest.approx(-credit_amount), 'Баланс кредита в истории не совпадает с ожидаемым'

        account_transactions = api_manager.user_steps.get_transactions(create_credit_user_request, id_account)
        issuance = next((t for t in account_transactions.transactions if t.type == "credit_issuance"), None)
        assert issuance is not None, 'Транзакция выдачи кредита не найдена'
        assert issuance.amount == pytest.approx(credit_amount), 'Сумма зачисления кредита не совпадает с ожидаемой'

        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert credit_from_db.balance == pytest.approx(-credit_amount), 'Баланс кредита в БД не совпадает с ожидаемым'

    def test_account_credit_request_invalid_second_credit_while_active(
        self,
        api_manager: ApiManager,
        logged_credit_user_with_two_accounts, # добавить
        create_credit_user_request: CreateUserRequest,
        db_session: Session
    ) -> None:
        create_credit_user_request, first_account, second_account = logged_credit_user_with_two_accounts
        id_account_first = first_account.id
        id_account_second = second_account.id

        response_credit_request_first = CreateCreditRequest(accountId=id_account_first, amount=5000, termMonths=12)
        api_manager.user_steps.credit_request(create_credit_user_request, response_credit_request_first)

        response_credit_request_second = CreateCreditRequest(accountId=id_account_second, amount=5000, termMonths=12)
        api_manager.user_steps.credit_request_invalid(create_credit_user_request, response_credit_request_second)

        credits_second_account_from_db = Credit.get_credits_by_account_id(db_session, id_account_second)
        assert len(credits_second_account_from_db) == 0, \
            'В БД не должно быть кредитов для второго счёта — повторный кредит не должен был оформиться'

    def test_account_credit_repay_valid(
        self,
        api_manager: ApiManager,
        logged_credit_user_with_account, # добавить
        create_credit_user_request: CreateUserRequest,
        db_session: Session
    ) -> None:
        create_credit_user_request, account = logged_credit_user_with_account
        id_account = account.id

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000, termMonths=12)
        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request, response_credit_request)
        id_credit = response_create_credit.creditId

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)
        api_manager.user_steps.account_deposit(create_credit_user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account, amount=9000)
        response_credit_repay = api_manager.user_steps.credit_repay(create_credit_user_request, credit_repay_request)

        assert response_credit_repay.amountDeposited == 9000, 'Сумма погашения в ответе не совпадает с ожидаемой'

        account_transactions = api_manager.user_steps.get_transactions(create_credit_user_request, id_account)
        repayment = next((t for t in account_transactions.transactions if t.type == "credit_repayment"), None)
        assert repayment is not None, 'Транзакция погашения не найдена'
        assert repayment.amount == pytest.approx(-9000), 'Сумма транзакции погашения не совпадает с ожидаемой'

        credit_history = api_manager.user_steps.credit_history(create_credit_user_request)
        credit = next((c for c in credit_history.credits if c.creditId == id_credit), None)
        assert credit is not None, 'Кредит не найден в истории после погашения'
        assert credit.balance == pytest.approx(0), 'Баланс кредита после полного погашения должен быть равен 0'

        account_from_db = Account.get_account_by_id(db_session, id_account)
        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert account_from_db.balance == pytest.approx(9000), 'Баланс счёта в БД не совпадает с ожидаемым'
        assert credit_from_db.balance == pytest.approx(0), 'Баланс кредита в БД после погашения должен быть равен 0'

    def test_account_credit_repay_invalid_partial_amount(
        self,
        api_manager: ApiManager,
        logged_credit_user_with_account, # добавить
        create_credit_user_request: CreateUserRequest,
        db_session: Session
    ) -> None:
        create_credit_user_request, account = logged_credit_user_with_account
        id_account = account.id

        response_credit_request = CreateCreditRequest(accountId=id_account, amount=9000, termMonths=12)
        response_create_credit = api_manager.user_steps.credit_request(create_credit_user_request, response_credit_request)
        id_credit = response_create_credit.creditId

        account_deposit_request = AccountDepositRequest(accountId=id_account, amount=9000.0)
        api_manager.user_steps.account_deposit(create_credit_user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit, accountId=id_account, amount=4000)
        api_manager.user_steps.credit_repay_invalid(create_credit_user_request, credit_repay_request)

        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert credit_from_db.balance == pytest.approx(-9000), \
            'Баланс кредита не должен измениться после отклонённого частичного погашения'