from pydantic import BaseModel
from typing import Optional


class CreateOrder(BaseModel):
    stock_symbol:str
    isin_number:str
    order_side:str
    order_qty:int
    order_types:Optional[str] = None
    current_price:float
    stoploss_price:Optional[float] = None
    target_price:Optional[float] = None
