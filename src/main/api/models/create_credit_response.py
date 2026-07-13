from src.main.api.models.base_model import BaseModel


class CreateCreditResponse(BaseModel):
    id: int
    amount: float
    termMonths: int
    balance: float
    creditId: int
