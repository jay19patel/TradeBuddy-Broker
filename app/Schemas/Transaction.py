from pydantic import BaseModel

class CreateTransaction(BaseModel):
    amount: float
    note: str
    transaction_type: str
