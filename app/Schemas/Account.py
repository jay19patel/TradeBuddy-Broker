from pydantic import BaseModel,EmailStr
from typing import List

class CreateAccount(BaseModel):
    email_id:str
    password:str
    max_trad_per_day:int =5
    base_stoploss:float =5.0
    base_target:float =10.0
    trailing_status:bool =True
    trailing_stoploss:float =10.0
    trailing_target:float =10.0
    payment_status:str ="Paper Trading"
    description:str

class LoginAccount(BaseModel):
    email_id:EmailStr
    password:str

