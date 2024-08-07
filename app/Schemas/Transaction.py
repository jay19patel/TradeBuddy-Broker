from pydantic import BaseModel
from typing import Optional

class CreateTransaction(BaseModel):
    amount: float
    note: Optional[str] = None
    transaction_type: str
