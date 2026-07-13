from src.main.api.models.base_model import BaseModel


class CreateCreditRequest(BaseModel):
    accountId: int
    amount: float
    termMonths: int