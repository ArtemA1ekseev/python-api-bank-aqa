from src.main.api.models.base_model import BaseModel



class CreateACcountResponce(BaseModel):
    id: int
    number: str
    balance: float