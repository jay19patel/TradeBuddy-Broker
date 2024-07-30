

from fastapi import APIRouter,Depends
from app.Core.utility import get_account_from_token
from app.Database.base import get_db, AsyncSession

analytics_route =APIRouter()

@analytics_route.get("/performance_report")
async def performance_report(account:any=Depends(get_account_from_token),
                                 db:AsyncSession =Depends(get_db)):
    pass

@analytics_route.get("/performance_counts")
async def performance_counts(account:any=Depends(get_account_from_token),
                                 db:AsyncSession =Depends(get_db)):
    pass