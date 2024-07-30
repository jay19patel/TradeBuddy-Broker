from pydantic import BaseModel
from typing import Optional


class CreateOrder(BaseModel):
    stock_symbol:str
    stock_isin:str
    order_side:str
    order_types:Optional[str] = None

    quantity:float
    order_price:float

    limit_price:Optional[float] = None
    trigger_price:Optional[float] = None
