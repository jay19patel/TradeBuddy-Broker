from fastapi import APIRouter, Depends, HTTPException
# from uuid import uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# App
from app.Models.models import Order, Position, Account,OrderStatus,OrderStatus
from app.Database.base import get_db
from app.Core.utility import get_account_from_token,generate_unique_id
from app.Schemas.Order import CreateOrder

order_route = APIRouter()

@order_route.post("/create_order")
async def create_order(
    request: CreateOrder,
    account: any = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)
    ):

    try:
        created_symbol = f"{request.stock_symbol}-{request.isin_number}"
        position = await db.execute(select(Position).where(Position.order_symbol == created_symbol and Position.order_status==OrderStatus.PENDING)).scalar_one_or_none()
        order_margin = request.quantity * request.current_price  
    
        # Account balance Status Chnage 
        if request.order_side == "BUY" and order_margin > account.balance:
            raise HTTPException(status_code=400, detail="Insufficient balance to place the order")
        
        if request.order_side == "BUY":
            account.balance -= order_margin
        elif request.order_side == "SELL":
            account.balance += order_margin
        else:
            raise HTTPException(status_code=400, detail="Order side must be 'BUY' or 'SELL' only")
    

        # order created
        order = Order(
            account_id=account.account_id,
            order_id=generate_unique_id("ORD"),
            position_id=position_id,
            quantity=request.quantity,
            stock_symbol=request.stock_symbol,
            stock_isin=request.stock_isin,   
            order_side=request.order_side,
            order_types=request.order_types,
            current_price=request.current_price,
            limit_price=request.limit_price,
            trigger_price=request.trigger_price
        )

        # If Position Alredy Existed then Update Position 
        if not position :
            total_buying_quantity = position.buy_quantity + request.quantity
            total_selling_quantity = position.sell_quantity + request.quantity
            
            position.buy_average = ((position.buy_average * position.buy_quantity + request.current_price * request.quantity) / total_buying_quantity )
            position.sell_average = ((position.sell_average * position.sell_quantity + request.current_price * request.quantity) / total_selling_quantity )

            position.buy_margin += order_margin
            position.buy_quantity = total_buying_quantity
            
            position.sell_margin += order_margin
            position.sell_quantity = total_selling_quantity

            if position.buy_quantity == position.sell_quantity and Position.order_status==OrderStatus.PENDING:
                pnl = (position.sell_average - position.buy_average) * position.sell_quantity
                position.pnl_total += pnl
                position.order_status = OrderStatus.COMPLETED
    
        else:
            # Create New Position in Position not exist
            pass
    
    except Exception as e
        print(e)
    else:
        db.add(account)
        db.add(position)
        db.add(order)
        await db.commit()
        await db.refresh(order)
        await db.refresh(position)
        await db.refresh(account)

        return {
            "status": "success",
            "message": "order create successful",
            "payload": {
                "account": account.account_id,
                "order":order.order_id,
                "position":position.position_id
            }
        }

@order_route.post("/update_order")
async def update_order():
    pass

@order_route.get("/get_order")
async def get_order():
    pass
