from typing import List, Optional

from src.main.api.models.account_transactions_response import Transaction


def find_transaction_by_type(transactions: List[Transaction], transaction_type: str) -> Optional[Transaction]:
    return next((t for t in transactions if t.type == transaction_type), None)