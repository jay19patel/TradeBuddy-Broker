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
    
import random
import time
import time

def generate_unique_id(input_string: str) -> str:
    timestamp = time.time() + 19
    timestamp_str = str(timestamp).replace('.', '')  # Remove the dot from the timestamp string
    unique_string = f"TB-{timestamp_str}-{input_string.upper()}"
    return unique_string


