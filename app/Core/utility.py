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
    
import hashlib
import time

def generate_unique_id(input_string: str) -> int:
    timestamp = time.time()
    unique_string = f"TB-{timestamp}-{input_string.capitalize()}"
    return unique_string

