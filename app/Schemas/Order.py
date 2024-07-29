from pydantic import BaseModel,Op
from typing import Optional


class CreateOrder(BaseModel):
    stock_symbol:str
    order_side:str
    order_types:str
    current_price:float
    stoploss_price:Optional[float] = None
    target_price:Optional[float] = None
