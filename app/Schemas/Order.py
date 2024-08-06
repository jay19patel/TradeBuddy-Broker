from pydantic import BaseModel
from typing import Optional


class CreateOrder(BaseModel):
    stock_symbol:str
    stock_isin:str

    order_side:str
    order_types:str
    product_type:Optional[str] = None

    stop_order_hit:Optional[bool] = None
    quantity:Optional[int] = None
    order_price:Optional[float] = None

    stoploss_limit_price = Optional[float] = None
    stoploss_trigger_price =Optional[float] = None

    target_limit_price = Optional[float] = None
    target_trigger_price = Optional[float] = None
    order_note = Optional[str] = None
    cratedby:Optional[float] = None


class UpdateStopMarketOrder(BaseModel):  
    order_id:float
    stoploss:float
    target:float