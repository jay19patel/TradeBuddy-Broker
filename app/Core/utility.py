from fastapi import Depends
from app.Database.base import get_db, AsyncSession
from app.Models.models import Account
from sqlalchemy import select
from app.Core.security import AccessTokenBearer

async def get_account_from_token(request: dict = Depends(AccessTokenBearer()),db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Account).where(Account.account_id == request["AccountId"]))
        account = result.scalars().first()
        return account
    except:
        return None