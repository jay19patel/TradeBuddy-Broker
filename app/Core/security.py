import random
import string
from fastapi import Request,HTTPException,status
import jwt 
import bcrypt
from datetime import timedelta,datetime
from app.Core.config import setting
from app.Database.base import get_db
import uuid
from sqlalchemy import text


async def generate_unique_custom_id() -> str:
    characters = string.ascii_uppercase + string.digits
    async for db in get_db():
        while True:
            new_id = ''.join(random.choice(characters) for _ in range(5))
            query = text(f"SELECT account_id FROM accounts WHERE account_id = :new_id")
            result = await db.execute(query, {'new_id': new_id})
            existing_id = result.fetchone()

            if not existing_id:
                print("-----------------------", new_id)
                return str(new_id)
                
            
            
def generate_hash_password(password :str):
    hash_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(hash_password, salt)
    return hashed_password.decode('utf-8')

def check_hash_password(password:str,hashed_password:str):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(payload:dict,expiry:timedelta=None):
    payload = payload.copy()
    payload['exp'] = datetime.now() + expiry
    # payload['iat'] = datetime.now()
    payload['jti']=str(uuid.uuid4())
    token =jwt.encode(payload, setting.SECRET_KEY, algorithm=setting.JWT_ALGORITHM)
    return token

def decode_token(token:str):
    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=setting.JWT_ALGORITHM)
        return payload  
    except jwt.PyJWTError as e:
        print(e)
        return None


from fastapi.security.http import HTTPBearer,HTTPAuthorizationCredentials

class AccessTokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error":"This token is invalid or expired",
                    "resolution":"Please get new token"
                }
            )

        if datetime.fromtimestamp(token_data["exp"])< datetime.now():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Token expired" )
        
        return token_data

    def token_valid(self, token: str) -> bool:

        token_data = decode_token(token)

        return token_data is not None 


