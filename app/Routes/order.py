from fastapi import APIRouter,Path, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.Models.models import Order, Position, Account, PositionStatus,OrderTypes
from app.Database.base import get_db
from app.Core.utility import get_account_from_token, generate_unique_id
from app.Schemas.Order import CreateOrder, UpdateStopMarketOrder
from datetime import date
order_route = APIRouter()


@order_route.post("/create_order")
async def create_order(
    request: CreateOrder,
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)
):

    # created_symbol = f"{request.stock_symbol}-{request.stock_isin}"
    order_margin = request.quantity * request.order_price if request.order_types in [OrderTypes.LIMIT,OrderTypes.MARKET] else 0

    # Check account balance for market orders
    if request.order_types in [OrderTypes.LIMIT,OrderTypes.MARKET] and request.order_side == "BUY" and order_margin > account.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance to place the order")

    # Retrieve existing position
    position = await db.scalar(select(Position).where(
        Position.stock_symbol == request.stock_symbol,
        Position.order_status == PositionStatus.PENDING
    ))

    # Determine trade ID
    created_position_id = position.position_id if position else generate_unique_id("TRD")

    # Adjust account balance for market orders
    if request.order_types in [OrderTypes.LIMIT,OrderTypes.MARKET]:
        account.balance += order_margin if request.order_side == "SELL" else -order_margin

    StopOrder = None
    if position and  request.order_types in [OrderTypes.STOPLIMIT,OrderTypes.STOPMARKET]:
        StopOrder = await db.scalar(select(Order).where(
            Order.position_id==position.position_id,
            Order.order_types.in_([OrderTypes.STOPLIMIT,OrderTypes.STOPMARKET]),
            Order.stop_order_hit == False
        ))
        if StopOrder:
            StopOrder.stoploss_limit_price = request.stoploss_limit_price
            StopOrder.stoploss_trigger_price = request.stoploss_trigger_price
            StopOrder.target_limit_price = request.target_limit_price
            StopOrder.target_trigger_price = request.target_trigger_price
            
     
    # Create the order
    if not StopOrder:
        order = Order(
        account_id=account.account_id,
        order_id=generate_unique_id("ORD"),
        position_id = created_position_id,
        stock_symbol =request.stock_symbol,
        stock_isin = request.stock_isin,
        order_side = request.order_side,
        order_types = request.order_types,
        product_type = request.product_type,
        stop_order_hit = request.stop_order_hit,
        quantity = request.quantity,
        order_price = request.order_price,
        limit_price = request.order_price,
        stoploss_limit_price = request.stoploss_limit_price,
        stoploss_trigger_price = request.stoploss_trigger_price,
        target_limit_price = request.target_limit_price,
        target_trigger_price = request.target_limit_price,
        order_note = request.order_note
    )

    if position and request.order_types in [OrderTypes.LIMIT,OrderTypes.MARKET]:
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

    if not position :
        position_data = {
            "position_id": created_position_id,
            "account_id": account.account_id,
            "stock_symbol": request.stock_symbol,
            "current_price": request.order_price,
            "created_by": request.created_by
        }
        if request.order_side == "BUY" and request.order_types == OrderTypes.MARKET:
            position_data.update({
                "buy_average": request.order_price,
                "buy_quantity": request.quantity,
                "buy_margin": order_margin
            })
        elif request.order_side == "SELL" and request.order_types ==  OrderTypes.MARKET:
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
            "position": position.position_id
        }
    }


@order_route.get("/orders/")
@order_route.get("/orders/{position_id}/")
async def get_orders(
    position_id: str = None,
    account: Account = Depends(get_account_from_token),
                    db: AsyncSession = Depends(get_db)):
    query = select(Order).where(Order.account_id == account.account_id)
    if position_id:
        query = query.where(
            Order.account_id == account.account_id,
            Order.position_id == position_id)
    data = await db.execute(query)
    return data.scalars().all()


@order_route.get("/position/{position_id}/")
async def get_single_position(
    position_id: str = None,
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)):

    query = select(Position).where(Position.account_id == account.account_id,Position.position_id = position_id)
    if position_id:
        query = query.where(
            Order.account_id == account.account_id,
            Order.position_id == position_id)
    data = await db.execute(query)
    return data.scalars().all()



@order_route.get("/positions")
async def get_positions(trade_today:bool = True,
                    account: Account = Depends(get_account_from_token),
                    db: AsyncSession = Depends(get_db)):
    query = select(Position).where(Position.account_id==account.account_id)
    if trade_today:
        current_date = date.today()
        query = select(Position).where(
            Position.account_id == account.account_id,
            Position.created_date >= current_date,
            Position.order_status == PositionStatus.PENDING
        )
    result = await db.execute(query)
    data = result.scalars().all()
    overview = {
        "total_positions":len(data),
        "open_positions":sum(1 for p in list(data) if p.order_status==PositionStatus.PENDING),
        "closed_positions":sum(1 for p in list(data) if p.order_status==PositionStatus.COMPLETED),
        "pnl_realized":sum(p.pnl_total for p in list(data) if p.order_status==PositionStatus.COMPLETED),
        "pnl_unrealized":sum(p.pnl_total for p in list(data) if p.order_status!=PositionStatus.COMPLETED),
        "pnl_total":  sum([p.pnl_total for p in list(data)])
    }

    return {"data":data,
            "overview":overview}
