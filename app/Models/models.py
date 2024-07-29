

from app.Database.base import Base
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime,func,ForeignKey
from enum import Enum
from sqlalchemy.orm import relationship


class Account(Base):
    INITIAL_BALANCE:float = 10000.00
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, unique=True,nullable=False)
    account_balance = Column(Float, default=INITIAL_BALANCE)
    email_id = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False)
    role=Column(String,default="User")
    is_activate = Column(Boolean, default=True)
    max_trad_per_day = Column(Integer, default=5)
    todays_margin = Column(Float, default=0.0)
    todays_single_trade_margin = Column(Float, default=0.0)
    base_stoploss = Column(Float, default=0.0)
    base_target = Column(Float, default=0.0)
    trailing_status = Column(Boolean, default=True)
    trailing_stoploss = Column(Float, default=0.0)
    trailing_target = Column(Float, default=0.0)
    payment_status = Column(String, default="Paper Trade")
    description = Column(String, default="")
    created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    modified_datetime = Column(DateTime(timezone=True), nullable=True, default=None, onupdate=func.now())
    
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, unique=True, nullable=False)
    account_id = Column(String,nullable=False)
    email_id = Column(String, nullable=False)
    transaction_type =Column(String,nullable=False)
    transaction_amount = Column(Float,nullable=False)
    transaction_note =Column(String)
    transaction_datetime = Column(DateTime(timezone=True), server_default=func.now())

class OrderSide(enum.Enum):
    BUY = 'buy'
    SELL = 'sell'

class OrderStatus(enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELED = 'canceled'


class OrderTypes(enum.Enum):
    LIMIT ="limit"
    MARKET  ="market"
    STOP ="stop"
    STOPLIMIT ="stoplimit"


class ProductType(enum.Enum):
    CNC  = 'cnc'
    INTRADAY = 'intraday'
    MARGIN = 'margin'


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    aaccount_id = Column(String,nullable=False)
    order_id = Column(String, unique=True, nullable=False)
    position_id = Column(String, unique=True, nullable=False)
    stock_symbol = Column(String, nullable=False)
    order_side = Column(Enum(OrderSide), nullable=False)
    product_type = Column(Enum(ProductType), nullable=False, default=ProductType.CNC)
    order_status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    order_types = Column(Enum(OrderTypes), nullable=False, default=OrderTypes.MARKET)
    is_completed = Column(Boolean, default=False)
    current_price = Column(Float, nullable=False)
    stoploss_price = Column(Float,default=0.0)
    target_price = Column(Float,default=0.0)
    is_order_modified = Column(Boolean, default=False)
    order_datetime = Column(DateTime(timezone=True), server_default=func.now())
    	
class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    account_id = Column(String,nullable=False)
    stock_symbol = Column(String, nullable=False)
    order_types = Column(Enum(OrderTypes), nullable=False, default=OrderTypes.MARKET)
    order_status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    position_id = Column(String, unique=True, nullable=False)
    current_price = Column(Float, nullable=False)
    buy_average = Column(Float, nullable=False)
    buy_margin = Column(Float, nullable=False)
    buy_quantity = Column(Integer, nullable=False, default=1)
    buy_datetime = Column(DateTime(timezone=True), server_default=func.now())
    sell_average = Column(Float, nullable=False, default=0.0)
    sell_margin = Column(Float, nullable=False, default=0.0)
    sell_quantity = Column(Integer, nullable=False, default=0)
    sell_datetime = Column(DateTime(timezone=True))
    product_type = Column(Enum(ProductType), nullable=False, default=ProductType.CNC)
    pl_realized = Column(Float, nullable=False, default=0.0)

