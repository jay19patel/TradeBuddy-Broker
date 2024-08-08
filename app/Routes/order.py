from fastapi import APIRouter,Path, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.Models.models import Order, Position, Account,PositionStatus,OrderSide,OrderTypes,CreateBy
from app.Database.base import get_db
from app.Core.utility import get_account_from_token, generate_unique_id
from app.Schemas.Order import CreateOrder
from datetime import date
order_route = APIRouter()


@order_route.post("/create_order")
async def create_order(
    request: CreateOrder,
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)
):
    

    position = await db.scalar(select(Position).where(Position.stock_symbol == request.stock_symbol,
                                                      Position.position_status == PositionStatus.PENDING
                                                    ))
    position_id = position.position_id if position else generate_unique_id("TRD")
    
    order_margin = request.quantity * request.limit_price if request.order_types  == "LIMIT" else 0

    if not position:
        print("---------------------------------- New Postion Create ----------------------------------")
        position_data = {
            "position_id": position_id,
            "account_id": account.account_id,
            "stock_symbol": request.stock_symbol,
            "stock_isin": request.stock_isin,
            "current_price": request.trigger_price,
            "created_by": request.created_by,
            "note" : request.note
        }
        if request.order_side == "BUY" and request.order_types == "LIMIT":
            position_data.update({
                "buy_average": request.limit_price,
                "buy_quantity": request.quantity,
                "buy_margin": order_margin
            })
        elif request.order_side == "SELL" and request.order_types == "LIMIT":
            position_data.update({
                "sell_average": request.limit_price,
                "sell_quantity": request.quantity,
                "sell_margin": order_margin
            })
        
        position = Position(**position_data)

    create_order = {
        "order_id" :generate_unique_id("ORD"),
        "account_id":account.account_id,
        "position_id":position_id,
        "stock_isin":request.stock_isin,
        "stock_symbol":request.stock_symbol,
        "order_types":request.order_types,
        "product_type":request.product_type,
        "stop_order_hit" : None
    }   

    stop_order = None 
    if request.order_types == "LIMIT":
        if request.order_types == "LIMIT" and request.order_side == "Buy" and order_margin > account.balance:
            raise HTTPException(status_code=400, detail="Insufficient balance to place the order")
        
        if request.order_side == "BUY":
            position.buy_quantity += request.quantity
            position.buy_margin += order_margin
            position.buy_average = (
                (position.buy_average * (position.buy_quantity - request.quantity) + request.limit_price * request.quantity) /
                position.buy_quantity
            )
        elif request.order_side == "SELL":
            position.sell_quantity += request.quantity
            position.sell_margin += order_margin
            position.sell_average = (
                (position.sell_average * (position.sell_quantity - request.quantity) + request.limit_price * request.quantity) /
                position.sell_quantity
            )
        else:
            raise HTTPException(status_code=400,detail="order side is not valied formate")
        

        if position.buy_quantity == position.sell_quantity and position.position_status == PositionStatus.PENDING:
            pnl = (position.sell_average - position.buy_average) * position.sell_quantity
            position.pnl_total += pnl
            position.position_status = PositionStatus.COMPLETED


        create_order.update({
            "order_side":request.order_side,
            "trigger_price":request.trigger_price,
            "limit_price":request.limit_price,
            "quantity":request.quantity
        })

    elif request.order_types == "STOPLIMIT":
        stop_order = await db.scalar(select(Order).where(Order.position_id == position.position_id,
                                                        Order.order_types == OrderTypes.STOPLIMIT,
                                                        Order.stop_order_hit == False
                                                        ))
        
        if stop_order:
            stop_order.stoploss_limit_price = request.stoploss_limit_price
            stop_order.stoploss_trigger_price = request.stoploss_trigger_price
            stop_order.target_limit_price = request.target_limit_price
            stop_order.target_trigger_price = request.target_trigger_price

        else:
            create_order.update({
                # "order_side":"OTHER",
                "stoploss_limit_price":request.stoploss_limit_price,
                "stoploss_trigger_price":request.stoploss_trigger_price,
                "target_limit_price":request.target_limit_price,
                "target_trigger_price":request.target_trigger_price
            })

    else:
        raise HTTPException(status_code=400,detail="Order type is not correct formate")
    
    if stop_order:
        print("STOP ORDER --------------------",stop_order)
        order = stop_order
        msg = "Order Modified successfully"
    else:
        print("NEW ORDER --------------------",create_order)
        order = Order(**create_order)
        msg = "Order Created successfully"
       
    db.add_all([account, position, order])
    await db.commit()
    await db.refresh(order)
    await db.refresh(position)
    await db.refresh(account)
    return {
        "status": "success",
        "message": msg,
        "payload": {
            "account": account.account_id,
            "order": order.order_id,
            "position": position.position_id
        }
    }

@order_route.get("/orders")
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

@order_route.get("/open_orders")
async def get_open_order(
            account: Account = Depends(get_account_from_token),
            db: AsyncSession = Depends(get_db)):
    
    query = select(Order).where(Order.account_id == account.account_id
                                ,Order.order_types == OrderTypes.STOPLIMIT
                                ,Order.stop_order_hit == False
                                )
    data = await db.execute(query)
    return data.scalars().all()


@order_route.get("/position/{position_id}/")
async def get_single_position(
    position_id: str = None,
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)):

    query = select(Position).where(Position.account_id == account.account_id,
                                   Position.position_id == position_id)
    if position_id:
        query = query.where(
            Order.account_id == account.account_id,
            Order.position_id == position_id)
    data = await db.execute(query)
    return data.scalars().all()

from sqlalchemy import func
from datetime import date

@order_route.get("/positions")
async def get_positions(trade_today: bool = False,
                        account: Account = Depends(get_account_from_token),
                        db: AsyncSession = Depends(get_db)):
    try:
        query = select(Position).where(Position.account_id == account.account_id)
        if trade_today:
            current_date = date.today()
            query = query.where(
                func.date(Position.created_date) == current_date,
                Position.position_status == PositionStatus.PENDING
            )
        print(query)
        result = await db.execute(query)
        data = result.scalars().all()

        overview = {
            "total_positions": len(data),
            "open_positions": sum(1 for p in data if p.position_status ==PositionStatus.PENDING),
            "closed_positions": sum(1 for p in data if p.position_status == PositionStatus.COMPLETED),
            "pnl_realized": sum(p.pnl_total for p in data if p.position_status == PositionStatus.COMPLETED),
            "pnl_unrealized": sum(p.pnl_total for p in data if p.position_status != PositionStatus.COMPLETED),
            "pnl_total": sum(p.pnl_total for p in data)
        }
        
        return {"data": data, "overview": overview}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Failed to retrieve data"}
