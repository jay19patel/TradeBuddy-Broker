from pydantic import BaseModel
from typing import Optional


class CreateOrder(BaseModel):
    stock_symbol:str
    stock_isin:str
    order_side:str
    order_types:Optional[str] = None

    quantity:Optional[float] = None
    order_price:Optional[float] = None

    stoploss_price:Optional[float] = None
    target_price:Optional[float] = None


class UpdateStopMarketOrder(BaseModel):  
    order_id:float
    stoploss:float
    target:float