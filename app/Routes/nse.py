
from fastapi import APIRouter,Depends
from uuid import uuid4
from sqlalchemy import select
# App
from app.Database.base import get_db, AsyncSession


nse_route =APIRouter()


@nse_route.get("/get_option_oi")
async def create_order():
    pass