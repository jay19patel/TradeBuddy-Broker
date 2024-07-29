

from fastapi import APIRouter

order_route =APIRouter()


@order_route.post("/buy_order")
async def buy_order():
    pass

@order_route.post("/sell_order")
async def sell_order():
    pass

@order_route.post("/update_order")
async def update_order():
    pass

@order_route.get("/get_order")
async def get_order():
    pass