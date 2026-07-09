import uuid

import requests
import pytest


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
                "role": "ROLE_USER"
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

        response_deposit = requests.post(
            url='http://localhost:4111/api/account/deposit',
            json={
                "accountId": id_account,
                "amount": deposit_amount
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_deposit.status_code == 200

        response_get_transaction = requests.get(
            url=f'http://localhost:4111/api/account/transactions/{id_account}',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
            }
        )

        assert response_get_transaction.status_code == 200
        response_body = response_get_transaction.json()
        assert response_body["balance"] == deposit_amount
        transactions = response_body["transactions"]
        assert len(transactions) == 1
        transaction = transactions[0]
        assert transaction["type"] == "deposit"
        assert transaction["amount"] == deposit_amount
        assert transaction["toAccountId"] == id_account
        assert transaction["transactionId"] is not None
        assert transaction["createdAt"] is not None

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
                "role": "ROLE_USER"
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

        response_deposit = requests.post(
            url='http://localhost:4111/api/account/deposit',
            json={
                "accountId": id_account,
                "amount": invalid_amount
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_deposit.status_code == 400

        response_get_transaction = requests.get(
            url=f'http://localhost:4111/api/account/transactions/{id_account}',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}'
            }
        )

        assert response_get_transaction.status_code == 200
        response_body = response_get_transaction.json()
        assert response_body["balance"] == 0
        assert len(response_body["transactions"]) == 0

    @pytest.mark.parametrize(
        "deposit_amount, transfer_amount",
        [
            (1000, 500),
            (5000, 2000),
            (9000, 9000),
        ]
    )
    def test_bank_account_transfer_valid(self, deposit_amount, transfer_amount):
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
                "role": "ROLE_USER"
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

        response_deposit = requests.post(
            url='http://localhost:4111/api/account/deposit',
            json={
                "accountId": id_account_first,
                "amount": deposit_amount
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_deposit.status_code == 200

        response_transfer_accounts = requests.post(
            url='http://localhost:4111/api/account/transfer',
            json={
                "fromAccountId": id_account_first,
                "toAccountId": id_account_second,
                "amount": transfer_amount
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_transfer_accounts.status_code == 200

        response_get_transaction_first = requests.get(
            url=f'http://localhost:4111/api/account/transactions/{id_account_first}',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
            }
        )

        assert response_get_transaction_first.status_code == 200

        response_body = response_get_transaction_first.json()
        assert response_body["id"] == id_account_first
        assert response_body["balance"] == deposit_amount - transfer_amount
        transactions = response_body["transactions"]
        assert len(transactions) == 2
        # flaky (уточнить гарантированный порядок сортировки)
        transfer = transactions[0]
        assert transfer["type"] == "transfer_out"
        assert transfer["amount"] == -transfer_amount
        assert transfer["fromAccountId"] == id_account_first
        assert transfer["toAccountId"] == id_account_second
        assert transfer["creditId"] is None
        assert transfer["transactionId"] is not None
        assert transfer["createdAt"] is not None
        # Предыдущая операция - пополнение
        deposit = transactions[1]
        assert deposit["type"] == "deposit"
        assert deposit["amount"] == deposit_amount
        assert deposit["fromAccountId"] is None
        assert deposit["toAccountId"] == id_account_first
        assert deposit["creditId"] is None
        assert deposit["transactionId"] is not None
        assert deposit["createdAt"] is not None

        response_get_transaction_second = requests.get(
            url=f'http://localhost:4111/api/account/transactions/{id_account_second}',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
            }
        )

        assert response_get_transaction_second.status_code == 200

        response_body = response_get_transaction_second.json()
        assert response_body["id"] == id_account_second
        assert response_body["balance"] == transfer_amount
        transactions = response_body["transactions"]
        assert len(transactions) == 1
        transaction = transactions[0]
        assert transaction["type"] == "transfer_in"
        assert transaction["amount"] == transfer_amount
        assert transaction["fromAccountId"] == id_account_first
        assert transaction["toAccountId"] == id_account_second
        assert transaction["creditId"] is None
        assert transaction["transactionId"] is not None
        assert transaction["createdAt"] is not None

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
                "role": "ROLE_USER"
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

        response_transfer_accounts = requests.post(
            url='http://localhost:4111/api/account/transfer',
            json={
                "fromAccountId": id_account_first,
                "toAccountId": id_account_second,
                "amount": transfer_amount
            },
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}',
                'Content-Type': 'application/json'
            }
        )

        assert response_transfer_accounts.status_code == 422

        response_get_transaction_first = requests.get(
            url=f'http://localhost:4111/api/account/transactions/{id_account_first}',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {token_user}'
            }
        )
        assert response_get_transaction_first.status_code == 200
        response_body = response_get_transaction_first.json()
        assert response_body["balance"] == 0
        assert len(response_body["transactions"]) == 0
