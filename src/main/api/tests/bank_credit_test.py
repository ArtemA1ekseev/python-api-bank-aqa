import uuid

import requests
import pytest


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
        login_admin_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_admin_response.status_code == 200
        token_admin = login_admin_response.json().get('token')
        assert token_admin is not None

        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {token_admin}'
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": username,
                "password": "Pas!sw0rd",
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_user_response.status_code == 200
        token_user = login_user_response.json().get('token')
        assert token_user is not None

        response_create_account = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'accept': 'application/json',
                "Authorization": f'Bearer {token_user}'
            }
        )

        assert response_create_account.status_code == 201
        id_account = response_create_account.json().get('id')
        assert id_account is not None

        response_credit_request = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                "accountId": id_account,
                "amount": credit_amount,
                "termMonths": term_months
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_credit_request.status_code == 201
        id_credit = response_credit_request.json().get('creditId')
        assert id_credit is not None

        response_credit_history = requests.get(
            url='http://localhost:4111/api/credit/history',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
            }
        )

        assert response_credit_history.status_code == 200

        response_body = response_credit_history.json()
        assert response_body["userId"] is not None
        credits = response_body["credits"]
        assert len(credits) == 1
        credit = credits[0]
        assert credit["creditId"] == id_credit
        assert credit["accountId"] == id_account
        assert credit["amount"] == credit_amount
        assert credit["termMonths"] == term_months
        assert credit["balance"] == -credit_amount
        assert credit["createdAt"] is not None

        response_account = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{id_account}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {token_user}"
            }
        )

        assert response_account.status_code == 200

        account = response_account.json()
        assert account["id"] == id_account
        assert account["number"] is not None
        assert account["balance"] == credit_amount
        transactions = account["transactions"]
        assert len(transactions) == 1
        transaction = transactions[0]
        assert transaction["transactionId"] is not None
        assert transaction["type"] == "credit_issuance"
        assert transaction["amount"] == credit_amount
        assert transaction["fromAccountId"] is None
        assert transaction["toAccountId"] == id_account
        assert transaction["createdAt"] is not None

    def test_account_credit_request_invalid_second_credit_while_active(self):
        login_admin_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_admin_response.status_code == 200
        token_admin = login_admin_response.json().get('token')
        assert token_admin is not None

        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {token_admin}'
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_user_response.status_code == 200
        token_user = login_user_response.json().get('token')
        assert token_user is not None

        response_create_account_first = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'accept': 'application/json',
                "Authorization": f'Bearer {token_user}'
            }
        )

        assert response_create_account_first.status_code == 201
        id_account_first = response_create_account_first.json().get('id')
        assert id_account_first is not None

        response_create_account_second = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'accept': 'application/json',
                "Authorization": f'Bearer {token_user}'
            }
        )

        assert response_create_account_second.status_code == 201
        id_account_second = response_create_account_second.json().get('id')
        assert id_account_second is not None

        response_credit_request_first = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                "accountId": id_account_first,
                "amount": 5000,
                "termMonths": 12
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_credit_request_first.status_code == 201

        response_credit_request_second = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                "accountId": id_account_second,
                "amount": 5000,
                "termMonths": 12
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_credit_request_second.status_code == 404

        response_credit_history = requests.get(
            url='http://localhost:4111/api/credit/history',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}'
            }
        )

        assert response_credit_history.status_code == 200
        credits = response_credit_history.json()["credits"]
        assert len(credits) == 1
        assert credits[0]["accountId"] == id_account_first

    def test_account_credit_repay_valid(self):
        login_admin_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_admin_response.status_code == 200
        token_admin = login_admin_response.json().get('token')
        assert token_admin is not None

        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {token_admin}'
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": username,
                "password": "Pas!sw0rd",
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_user_response.status_code == 200
        token_user = login_user_response.json().get('token')
        assert token_user is not None

        response_create_account = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'accept': 'application/json',
                "Authorization": f'Bearer {token_user}'
            }
        )

        assert response_create_account.status_code == 201
        id_account = response_create_account.json().get('id')
        assert id_account is not None

        response_credit_request = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                "accountId": id_account,
                "amount": 9000,
                "termMonths": 12
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_credit_request.status_code == 201
        id_credit = response_credit_request.json().get('creditId')
        assert id_credit is not None

        response_deposit = requests.post(
            url='http://localhost:4111/api/account/deposit',
            json={
                "accountId": id_account,
                "amount": 9000.0
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_deposit.status_code == 200

        response_credit_repay = requests.post(
            url='http://localhost:4111/api/credit/repay',
            json={
                "creditId": id_credit,
                "accountId": id_account,
                "amount": 9000
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_credit_repay.status_code == 200
        assert response_credit_repay.json().get('amountDeposited') == 9000
        assert response_credit_repay.json().get('creditId') == id_credit

        response_get_transaction = requests.get(
            url=f'http://localhost:4111/api/account/transactions/{id_account}',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
            }
        )

        assert response_get_transaction.status_code == 200
        response_body = response_get_transaction.json()
        assert response_body["balance"] == 9000

        response_credit_history = requests.get(
            url='http://localhost:4111/api/credit/history',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
            }
        )

        assert response_credit_history.status_code == 200
        credits = response_credit_history.json()["credits"]
        assert len(credits) == 1
        credit = credits[0]
        assert credit["creditId"] == id_credit
        assert credit["balance"] == 0

        transactions = response_body["transactions"]
        assert len(transactions) == 3

        repayment_transactions = [t for t in transactions if t["type"] == "credit_repayment"]
        assert len(repayment_transactions) == 1
        repayment = repayment_transactions[0]
        assert repayment["amount"] == -9000
        assert repayment["fromAccountId"] == id_account
        assert repayment["toAccountId"] is None
        assert repayment["creditId"] == id_credit
        assert repayment["transactionId"] is not None
        assert repayment["createdAt"] is not None

    def test_account_credit_repay_invalid_partial_amount(self):
        login_admin_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_admin_response.status_code == 200
        token_admin = login_admin_response.json().get('token')
        assert token_admin is not None

        username = f"Max{uuid.uuid4().hex[:8]}"

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {token_admin}'
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        assert login_user_response.status_code == 200
        token_user = login_user_response.json().get('token')
        assert token_user is not None

        response_create_account = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'accept': 'application/json',
                "Authorization": f'Bearer {token_user}'
            }
        )

        assert response_create_account.status_code == 201
        id_account = response_create_account.json().get('id')
        assert id_account is not None

        response_credit_request = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                "accountId": id_account,
                "amount": 9000,
                "termMonths": 12
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_credit_request.status_code == 201
        id_credit = response_credit_request.json().get('creditId')
        assert id_credit is not None

        response_deposit = requests.post(
            url='http://localhost:4111/api/account/deposit',
            json={
                "accountId": id_account,
                "amount": 9000.0
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_deposit.status_code == 200

        response_credit_repay = requests.post(
            url='http://localhost:4111/api/credit/repay',
            json={
                "creditId": id_credit,
                "accountId": id_account,
                "amount": 4000
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_credit_repay.status_code == 422

        response_credit_history = requests.get(
            url='http://localhost:4111/api/credit/history',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}'
            }
        )

        assert response_credit_history.status_code == 200
        credit = response_credit_history.json()["credits"][0]
        assert credit["balance"] == -9000