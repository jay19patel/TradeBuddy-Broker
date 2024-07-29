from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# App
from app.Models.models import Order, Position, Account,OrderStatus
from app.Database.base import get_db
from app.Core.utility import get_account_from_token
from app.Schemas.Order import CreateOrder

order_route = APIRouter()

@order_route.post("/create_order")
async def create_order(
    request: CreateOrder,
    account: any = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)
):
    position_id = f"{request.stock_symbol}-{request.isin_number}"
    result = await db.execute(select(Position).where(Position.position_id == position_id))
    position = result.scalar_one_or_none()
    
    order_margin = request.order_qty * request.current_price
    
    if request.order_side == "BUY" and order_margin > account.account_balance:
        raise HTTPException(status_code=400, detail="Insufficient balance to place the order")
    
    if request.order_side == "BUY":
        account.account_balance -= order_margin
    elif request.order_side == "SELL":
        account.account_balance += order_margin
    else:
        raise HTTPException(status_code=400, detail="Order side must be 'BUY' or 'SELL' only")
    
    db.add(account)
    
    order = Order(
        account_id=account.account_id,
        order_id=str(uuid4()),
        position_id=position_id,
        quantity=request.order_qty,
        stock_symbol=request.stock_symbol,
        order_side=request.order_side,
        order_types=request.order_types,
        current_price=request.current_price,
        stoploss_price=request.stoploss_price,
        target_price=request.target_price
    )
    if position:
        if request.order_side == "BUY":
            total_quantity = position.buy_quantity + request.order_qty
            position.buy_average = (
                (position.buy_average * position.buy_quantity + request.current_price * request.order_qty) /
                total_quantity
            )
            position.buy_quantity = total_quantity
            position.buy_margin += order_margin

        elif request.order_side == "SELL" :
            if request.order_qty > (position.buy_quantity - position.sell_quantity):
                raise HTTPException(status_code=400, detail="Sell quantity is graterthe  buy quantity")
            if position.order_status==OrderStatus.COMPLETED:
                raise HTTPException(status_code=400, detail=f"Position - {position.position_id} is closed")
            total_quantity = position.sell_quantity + request.order_qty
            position.sell_average = (
                (position.sell_average * position.sell_quantity + request.current_price * request.order_qty) /
                total_quantity
            )
            position.sell_quantity = total_quantity
            position.sell_margin += order_margin

            if position.buy_quantity == position.sell_quantity:
                pnl = (position.sell_average - position.buy_average) * position.sell_quantity
                position.pnl_total += pnl

                # Mark all orders with the same position ID as completed
                await db.execute(
                    update(Order)
                    .where(Order.position_id == position_id)
                    .values(is_completed=True)
                )
                
                # Update position status to completed
                position.order_status = "COMPLETED"
    
        db.add(position)

    else:
        if request.order_side == "BUY":
            position = Position(
                buy_average=request.current_price,
                buy_margin=order_margin,
                buy_quantity=request.order_qty,
                position_id=position_id,
                order_types=request.order_types,
                account_id=account.account_id,
                stock_symbol=request.stock_symbol,
                current_price=request.current_price,
            )
        elif request.order_side == "SELL":
            position = Position(
                sell_average=request.current_price,
                sell_margin=order_margin,
                sell_quantity=request.order_qty,
                position_id=position_id,
                order_types=request.order_types,
                account_id=account.account_id,
                stock_symbol=request.stock_symbol,
                current_price=request.current_price,
            )
        db.add(position)
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    await db.refresh(position)
    return position

@order_route.post("/update_order")
async def update_order():
    pass

@order_route.get("/get_order")
async def get_order():
    pass
