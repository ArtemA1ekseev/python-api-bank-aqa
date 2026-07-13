from datetime import datetime
from typing import List

from src.main.api.models.base_model import BaseModel


class Credit(BaseModel):
    creditId: int
    accountId: int
    amount: float
    termMonths: int
    balance: float
    createdAt: datetime


class CreditHistoryResponse(BaseModel):
    userId: int
    credits: List[Credit]
