from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.Models.models import Order, Position, Account, PositionStatus,OrderTypes
from app.Database.base import get_db
from app.Core.utility import get_account_from_token, generate_unique_id
from app.Schemas.Order import CreateOrder, UpdateStopMarketOrder

order_route = APIRouter()

@order_route.post("/create_order")
async def create_order(
    request: CreateOrder,
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)
):
        created_symbol = f"{request.stock_symbol}-{request.stock_isin}"
        if request.order_types =="MARKET" :
            order_margin = request.quantity * request.order_price

        result = await db.execute(
                select(Position).where(
                    Position.stock_symbol == created_symbol,
                    Position.order_status == PositionStatus.PENDING
                )
            )
        position = result.scalar_one_or_none()
        if not position:
            created_trade_id = generate_unique_id("TRD")
        else:
            created_trade_id = position.trade_id

        # Check account balance
        if request.order_types =="MARKET":
            if request.order_side == "BUY" and order_margin > account.balance:
                raise HTTPException(status_code=400, detail="Insufficient balance to place the order")
            if request.order_side == "BUY":
                account.balance -= order_margin
            elif request.order_side == "SELL":
                account.balance += order_margin
            else:
                raise HTTPException(status_code=400, detail="Order side must be 'BUY' or 'SELL' only")
        


        # Create the order
        

        order = Order(
            account_id=account.account_id,
            order_id=generate_unique_id("ORD"),
            quantity=request.quantity,
            trade_id = created_trade_id,
            order_symbol=created_symbol,
            stock_isin=request.stock_isin,   
            order_side=request.order_side,
            order_price=request.order_price,
            stoploss_price=request.stoploss_price,
            target_price=request.target_price,
            order_types = request.order_types
        )
        print("Order created")

        if position and request.order_types =="MARKET" :
            # Update existing position
            if request.order_side == "BUY":
                position.buy_quantity += request.quantity
                position.buy_margin += order_margin
                position.buy_average = ((position.buy_average * (position.buy_quantity - request.quantity) + request.order_price * request.quantity) / position.buy_quantity)
            elif request.order_side == "SELL":
                position.sell_quantity += request.quantity
                position.sell_margin += order_margin
                position.sell_average = ((position.sell_average * (position.sell_quantity - request.quantity) + request.order_price * request.quantity) / position.sell_quantity)

            if position.buy_quantity == position.sell_quantity and position.order_status == PositionStatus.PENDING:
                pnl = (position.sell_average - position.buy_average) * position.sell_quantity
                position.pnl_total += pnl
                position.order_status = PositionStatus.COMPLETED

            if order.order_types == OrderTypes.STOPMARKET:
                position.target = request.order_price + (account.base_target * request.order_price) / 100
                position.stoploss = request.order_price - (account.base_stoploss * request.order_price) / 100
        else:
            # Create new position
            if request.order_side == "BUY" and request.order_types =="MARKET" :
                position = Position(
                    trade_id= created_trade_id,
                    account_id=account.account_id,
                    stock_symbol=created_symbol,
                    order_types=request.order_types,
                    current_price=request.order_price,
                    buy_average=request.order_price,
                    buy_quantity=request.quantity,
                    buy_margin=order_margin
                )
            if request.order_side == "SELL" and request.order_types =="MARKET" :
                position = Position(
                    trade_id=generate_unique_id("TRD"),
                    account_id=account.account_id,
                    stock_symbol=created_symbol,
                    order_types=request.order_types,
                    current_price=request.order_price,
                    sell_average=request.order_price,
                    sell_quantity=request.quantity,
                    sell_margin=order_margin
                )

        # Add records to the database
        db.add(account)
        db.add(position)
        db.add(order)
        await db.commit()
        await db.refresh(order)
        await db.refresh(position)
        await db.refresh(account)

        return {
            "status": "success",
            "message": "Order created successfully",
            "payload": {
                "account": account.account_id,
                "order": order.order_id,
                "position": position.trade_id if position else None
            }
        }


@order_route.get("/get_position")
async def get_position(account: Account = Depends(get_account_from_token),
                    db: AsyncSession = Depends(get_db)):
    data = await db.execute(select(Position).where(Position.account_id==account.account_id))
    return data.scalars().all()



    
    
@order_route.get("/get_trade_info")
async def get_trade_info(account: Account = Depends(get_account_from_token),
                    db: AsyncSession = Depends(get_db)):
    result = await db.execute(
            select(Position).options(selectinload(Position.orders)).where(Position.account_id == account.account_id)
        )
    data = result.scalars().all()
    overview = {
        "total_positions":len(data),
        "open_positions":sum(1 for p in list(data) if p.order_status=="pending"),
        "closed_positions":sum(1 for p in list(data) if p.order_status=="completed"),
        "pnl_realized":sum(p.pnl_total for p in list(data) if p.order_status=="completed"),
        "pnl_unrealized":sum(p.pnl_total for p in list(data) if p.order_status!="completed"),
        "pnl_total":  sum([p.pnl_total for p in list(data)])

    }

    return {"data":data,
            "overview":overview}
