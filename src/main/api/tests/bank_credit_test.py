import pytest
from sqlalchemy.orm import Session

from src.main.api.configs.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.fixture_data import UserWithAccount, UserWithTwoAccounts
from src.main.api.utils.credit_utils import find_credit_by_id
from src.main.api.utils.transaction_utils import find_transaction_by_type


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
            logged_credit_user_with_account: UserWithAccount,
            credit_amount: int,
            term_months: int,
            db_session: Session
    ) -> None:
        response_credit_request = CreateCreditRequest(accountId=logged_credit_user_with_account.account.id,
                                                      amount=credit_amount,
                                                      termMonths=term_months)
        response_create_credit = api_manager.user_steps.credit_request(logged_credit_user_with_account.user_request,
                                                                       response_credit_request)
        id_credit = response_create_credit.creditId

        assert response_create_credit.amount == pytest.approx(credit_amount), \
            'Сумма кредита в ответе не совпадает с запрошенной'

        credit_history = api_manager.user_steps.credit_history(logged_credit_user_with_account.user_request)
        credit = find_credit_by_id(credit_history.credits, id_credit)
        assert credit is not None, 'Созданный кредит не найден в истории'
        assert credit.balance == pytest.approx(-credit_amount), 'Баланс кредита в истории не совпадает с ожидаемым'

        account_transactions = api_manager.user_steps.get_transactions(logged_credit_user_with_account.user_request,
                                                                       logged_credit_user_with_account.account.id)
        issuance = find_transaction_by_type(account_transactions.transactions, "credit_issuance")
        assert issuance is not None, 'Транзакция выдачи кредита не найдена'
        assert issuance.amount == pytest.approx(credit_amount), 'Сумма зачисления кредита не совпадает с ожидаемой'

        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert credit_from_db.balance == pytest.approx(-credit_amount), 'Баланс кредита в БД не совпадает с ожидаемым'

    def test_account_credit_request_invalid_second_credit_while_active(
            self,
            api_manager: ApiManager,
            logged_credit_user_with_two_accounts: UserWithTwoAccounts,
            db_session: Session
    ) -> None:
        response_credit_request_first = CreateCreditRequest(
            accountId=logged_credit_user_with_two_accounts.first_account.id, amount=5000, termMonths=12)
        api_manager.user_steps.credit_request(logged_credit_user_with_two_accounts.user_request,
                                              response_credit_request_first)

        response_credit_request_second = CreateCreditRequest(
            accountId=logged_credit_user_with_two_accounts.second_account.id, amount=5000, termMonths=12)
        api_manager.user_steps.credit_request_invalid(logged_credit_user_with_two_accounts.user_request,
                                                      response_credit_request_second)

        credits_second_account_from_db = Credit.get_credits_by_account_id(db_session,
                                                                          logged_credit_user_with_two_accounts.second_account.id)
        assert len(credits_second_account_from_db) == 0, \
            'В БД не должно быть кредитов для второго счёта — повторный кредит не должен был оформиться'

    def test_account_credit_repay_valid(
            self,
            api_manager: ApiManager,
            logged_credit_user_with_account: UserWithAccount,
            db_session: Session
    ) -> None:
        response_credit_request = CreateCreditRequest(accountId=logged_credit_user_with_account.account.id, amount=9000,
                                                      termMonths=12)
        response_create_credit = api_manager.user_steps.credit_request(logged_credit_user_with_account.user_request,
                                                                       response_credit_request)
        id_credit = response_create_credit.creditId

        account_deposit_request = AccountDepositRequest(accountId=logged_credit_user_with_account.account.id,
                                                        amount=9000.0)
        api_manager.user_steps.account_deposit(logged_credit_user_with_account.user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit,
                                                  accountId=logged_credit_user_with_account.account.id, amount=9000)
        response_credit_repay = api_manager.user_steps.credit_repay(logged_credit_user_with_account.user_request,
                                                                    credit_repay_request)

        assert response_credit_repay.amountDeposited == 9000, 'Сумма погашения в ответе не совпадает с ожидаемой'

        account_transactions = api_manager.user_steps.get_transactions(logged_credit_user_with_account.user_request,
                                                                       logged_credit_user_with_account.account.id)
        repayment = find_transaction_by_type(account_transactions.transactions, "credit_repayment")
        assert repayment is not None, 'Транзакция погашения не найдена'
        assert repayment.amount == pytest.approx(-9000), 'Сумма транзакции погашения не совпадает с ожидаемой'

        credit_history = api_manager.user_steps.credit_history(logged_credit_user_with_account.user_request)
        credit = find_credit_by_id(credit_history.credits, id_credit)
        assert credit is not None, 'Кредит не найден в истории после погашения'
        assert credit.balance == pytest.approx(0), 'Баланс кредита после полного погашения должен быть равен 0'

        account_from_db = Account.get_account_by_id(db_session, logged_credit_user_with_account.account.id)
        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert account_from_db.balance == pytest.approx(9000), 'Баланс счёта в БД не совпадает с ожидаемым'
        assert credit_from_db.balance == pytest.approx(0), 'Баланс кредита в БД после погашения должен быть равен 0'

    def test_account_credit_repay_invalid_partial_amount(
            self,
            api_manager: ApiManager,
            logged_credit_user_with_account: UserWithAccount,
            db_session: Session
    ) -> None:
        response_credit_request = CreateCreditRequest(accountId=logged_credit_user_with_account.account.id, amount=9000,
                                                      termMonths=12)
        response_create_credit = api_manager.user_steps.credit_request(logged_credit_user_with_account.user_request,
                                                                       response_credit_request)
        id_credit = response_create_credit.creditId

        account_deposit_request = AccountDepositRequest(accountId=logged_credit_user_with_account.account.id,
                                                        amount=9000.0)
        api_manager.user_steps.account_deposit(logged_credit_user_with_account.user_request, account_deposit_request)

        credit_repay_request = CreditRepayRequest(creditId=id_credit,
                                                  accountId=logged_credit_user_with_account.account.id, amount=4000)
        api_manager.user_steps.credit_repay_invalid(logged_credit_user_with_account.user_request, credit_repay_request)

        credit_from_db = Credit.get_credit_by_id(db_session, id_credit)
        assert credit_from_db.balance == pytest.approx(-9000), \
            'Баланс кредита не должен измениться после отклонённого частичного погашения'
