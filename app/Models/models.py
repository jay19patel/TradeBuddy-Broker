from app.Database.base import Base
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, func, ForeignKey, Enum as sqlEnum
from enum import Enum
from sqlalchemy.orm import relationship

class Account(Base):
    """Account model."""
    INITIAL_BALANCE: float = 10000.00
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, unique=True, nullable=False)
    balance = Column(Float, default=INITIAL_BALANCE)
    email_id = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False)
    role = Column(String, default="User")
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

    transactions = relationship('Transaction', back_populates='account')
    positions = relationship('Position', back_populates='account')
    orders = relationship('Order', back_populates='account')


class Transaction(Base):
    """Transaction model."""
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, unique=True, nullable=False)
    account_id = Column(String, ForeignKey('accounts.account_id'), nullable=False)
    email_id = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    transaction_amount = Column(Float, nullable=False)
    transaction_note = Column(String)
    transaction_datetime = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship('Account', back_populates='transactions')


class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class PositionStatus(Enum):
    PENDING = 'Pending'
    COMPLETED = 'Completed'


class OrderTypes(Enum):
    # MARKET = "Market"
    LIMIT = "Limit"
    # STOPMARKET = "StopMarket"
    STOPLIMIT = "StopLimit"

class CreateBy(Enum):
    MENUAL = "Menual"
    ALGO = "Algo"

class ProductType(Enum):
    CNC = 'CNC'
    INTRADAY = 'Intraday'
    MARGIN = 'Margin'

class Position(Base):
    """Position model."""
    __tablename__ = 'positions'

    position_id = Column(String, primary_key=True, nullable=False)
    account_id = Column(String, ForeignKey('accounts.account_id'), nullable=False)
    stock_symbol = Column(String, nullable=False)
    stock_isin = Column(String, nullable=False) 

    position_status = Column(sqlEnum(PositionStatus), nullable=False, default=PositionStatus.PENDING)
    product_type = Column(sqlEnum(ProductType), nullable=False, default=ProductType.CNC)

    trailing_activated = Column(Boolean, default=True)
    trailing_count = Column(Integer, default=0)
    current_price = Column(Float, nullable=False, default=0)
    buy_average = Column(Float, nullable=False, default=0)
    buy_margin = Column(Float, nullable=False, default=0)
    buy_quantity = Column(Integer, nullable=False, default=0)
    sell_average = Column(Float, nullable=False, default=0)
    sell_margin = Column(Float, nullable=False, default=0.0)
    sell_quantity = Column(Integer, nullable=False, default=0)
    pnl_total = Column(Float, nullable=False, default=0)
    created_date = Column(DateTime, server_default=func.now())
    created_by = Column(sqlEnum(CreateBy), nullable=False, default=CreateBy.MENUAL)
    note = Column(String,default="-")

    account = relationship('Account', back_populates='positions')
    orders = relationship('Order', back_populates='position')

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(String, primary_key=True, nullable=False)
    account_id = Column(String, ForeignKey('accounts.account_id'), nullable=False)
    position_id = Column(String, ForeignKey('positions.position_id'), nullable=False)
    stock_isin = Column(String, nullable=False)
    stock_symbol = Column(String, nullable=False)

    order_side = Column(sqlEnum(OrderSide), nullable=False, default=OrderSide.BUY)
    order_types = Column(sqlEnum(OrderTypes), nullable=False, default=OrderTypes.LIMIT)
    product_type = Column(sqlEnum(ProductType), nullable=False, default=ProductType.CNC)

    trigger_price = Column(Float)
    limit_price =Column(Float)
    quantity = Column(Integer)

    stop_order_hit = Column(Boolean, default=False)


    stoploss_limit_price = Column(Float)
    stoploss_trigger_price = Column(Float)

    target_limit_price = Column(Float)
    target_trigger_price = Column(Float)

    order_datetime = Column(DateTime(timezone=True), server_default=func.now())  

    # Relationships
    account = relationship('Account', back_populates='orders')
    position = relationship('Position', back_populates='orders')