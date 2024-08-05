from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.Models.models import Order, Position, Account, PositionStatus,OrderTypes
from app.Database.base import get_db
from app.Core.utility import get_account_from_token, generate_unique_id
from app.Schemas.Order import CreateOrder, UpdateStopMarketOrder

order_route = APIRouter()

async def create_order(
    request: CreateOrder,
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)
):
    # created_symbol = f"{request.stock_symbol}-{request.stock_isin}"
    order_margin = request.quantity * request.order_price if request.order_types == "MARKET" else 0

    # Check account balance for market orders
    if request.order_types == "MARKET" and request.order_side == "BUY" and order_margin > account.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance to place the order")

    # Retrieve existing position
    position = await db.scalar(select(Position).where(
        Position.stock_symbol == request.stock_symbol,
        Position.order_status == PositionStatus.PENDING
    ))

    # Determine trade ID
    created_trade_id = position.trade_id if position else generate_unique_id("TRD")

    # Adjust account balance for market orders
    if request.order_types == "MARKET":
        account.balance += order_margin if request.order_side == "SELL" else -order_margin

    # Create the order
    order = Order(
        account_id=account.account_id,
        order_id=generate_unique_id("ORD"),
        quantity=request.quantity,
        trade_id=created_trade_id,
        order_symbol=request.stock_symbol,
        stock_isin=request.stock_isin,
        order_side=request.order_side,
        order_price=request.order_price,
        stoploss_price=request.stoploss_price,
        target_price=request.target_price,
        order_types=request.order_types
    )

    if position and request.order_types == "MARKET":
        # Update existing position
        if request.order_side == "BUY":
            position.buy_quantity += request.quantity
            position.buy_margin += order_margin
            position.buy_average = ((position.buy_average * (position.buy_quantity - request.quantity)
                                     + request.order_price * request.quantity) / position.buy_quantity)
        elif request.order_side == "SELL":
            position.sell_quantity += request.quantity
            position.sell_margin += order_margin
            position.sell_average = ((position.sell_average * (position.sell_quantity - request.quantity)
                                      + request.order_price * request.quantity) / position.sell_quantity)

        # Complete position if quantities match
        if position.buy_quantity == position.sell_quantity:
            pnl = (position.sell_average - position.buy_average) * position.sell_quantity
            position.pnl_total += pnl
            position.order_status = PositionStatus.COMPLETED

        # Update position for STOPMARKET orders
        if order.order_types == OrderTypes.STOPMARKET:
            position.target = request.order_price + (account.base_target * request.order_price) / 100
            position.stoploss = request.order_price - (account.base_stoploss * request.order_price) / 100

    else:
        # Create new position
        position_data = {
            "trade_id": created_trade_id,
            "account_id": account.account_id,
            "stock_symbol": request.stock_symbol,
            "order_types": request.order_types,
            "current_price": request.order_price,
        }
        if request.order_side == "BUY" and request.order_types == "MARKET":
            position_data.update({
                "buy_average": request.order_price,
                "buy_quantity": request.quantity,
                "buy_margin": order_margin
            })
        elif request.order_side == "SELL" and request.order_types == "MARKET":
            position_data.update({
                "sell_average": request.order_price,
                "sell_quantity": request.quantity,
                "sell_margin": order_margin
            })
        position = Position(**position_data)

    # Add records to the database
    db.add_all([account, position, order])
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
            "position": position.trade_id
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
