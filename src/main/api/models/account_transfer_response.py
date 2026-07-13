from src.main.api.models.base_model import BaseModel



class AccountTransferResponse(BaseModel):
    fromAccountId: int
    toAccountId: int
    fromAccountIdBalance: float