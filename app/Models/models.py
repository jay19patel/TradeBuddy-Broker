

from app.Database.base import Base
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime,func,ForeignKey
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




