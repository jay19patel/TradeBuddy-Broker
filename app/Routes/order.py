

from fastapi import APIRouter
from uuid import uuid4

# App
from app.Models.models import Order
from app.Database.base import get_db, AsyncSession
from app.Core.utility import get_account_from_token
from app.Schemas.Order import CreateOrder
order_route =APIRouter()


@order_route.post("/buy_order")
async def buy_order(request:CreateOrder,
                    account:any=Depends(get_account_from_token),
                    db:AsyncSession =Depends(get_db)):


    order_data = Order( )

@order_route.post("/sell_order")
async def sell_order():
    pass

@order_route.post("/update_order")
async def update_order():
    pass

@order_route.get("/get_order")
async def get_order():
    pass