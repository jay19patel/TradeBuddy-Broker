from pydantic import BaseModel
from typing import Optional


class CreateOrder(BaseModel):
    stock_symbol: str
    stock_isin: str

    order_side: Optional[str] = None
    order_types: Optional[str] = None
    product_type: Optional[str] = None

    quantity: Optional[int] = None
    trigger_price: Optional[float] = None
    limit_price: Optional[float] = None

    stop_order_hit: Optional[bool] = None

    stoploss_limit_price: Optional[float] = None
    stoploss_trigger_price: Optional[float] = None

    target_limit_price: Optional[float] = None
    target_trigger_price: Optional[float] = None

    note: Optional[str] = None
    created_by: Optional[str] = None 

