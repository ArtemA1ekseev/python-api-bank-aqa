from src.main.api.models.base_model import BaseModel


class AccountDepositResponse(BaseModel):
    id: int
    balance: float
