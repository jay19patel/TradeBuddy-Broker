

from fastapi import APIRouter,Depends
from app.Core.utility import get_account_from_token
from app.Database.base import get_db, AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import selectinload
from app.Models.models import Position
from datetime import datetime,date
import pandas as pd


analytics_route =APIRouter()

@analytics_route.get("/performance_report")
async def performance_report(account:any=Depends(get_account_from_token),
                            db:AsyncSession =Depends(get_db)):
    
    result = await db.execute(
            select(Position).options(selectinload(Position.orders)).
            where(Position.account_id == account.account_id)
    ) 
    positions = result.scalars().fetchmany()
    if not positions:
        return {"message": "No positions found for the account."}
    
    return positions


@analytics_route.get("/performance_counts")
async def performance_counts(account:any=Depends(get_account_from_token),
                            db:AsyncSession =Depends(get_db)):
    pass