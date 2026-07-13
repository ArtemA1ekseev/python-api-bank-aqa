from datetime import datetime
from typing import List, Optional

from src.main.api.models.base_model import BaseModel


class Transaction(BaseModel):
    transactionId: int
    type: str
    amount: float
    fromAccountId: Optional[int] = None
    toAccountId: Optional[int] = None
    createdAt: datetime


class AccountTransactionsResponse(BaseModel):
    id: int
    number: str
    balance: float
    transactions: List[Transaction]