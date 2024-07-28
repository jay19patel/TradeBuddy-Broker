from fastapi import APIRouter, Depends, HTTPException, status
import logging
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import os
# App
from app.Database.base import get_db, AsyncSession
from app.Models.models import Account
from app.Schemas.Account import CreateAccount, LoginAccount
from app.Core.security import generate_hash_password, check_hash_password, create_access_token,generate_unique_custom_id
from app.Core.config import setting
from app.Services.email import email_send_access_token
from app.Core.utility import get_account_from_token

# Logging
# logging.basicConfig(filename=f"{os.getcwd()}/Records/StrategyManager.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

auth_rout = APIRouter()

@auth_rout.post("/create_account")
async def create_account(request: CreateAccount, db: AsyncSession = Depends(get_db)):
    try:
        account = Account(
        email_id=request.email_id,
        account_id=await generate_unique_custom_id(),
        password=generate_hash_password(password=request.password),
        max_trad_per_day=request.max_trad_per_day,
        base_stoploss=request.base_stoploss,
        base_target=request.base_target,
        trailing_status=request.trailing_status,
        trailing_stoploss=request.trailing_stoploss,
        trailing_target=request.trailing_target,
        payment_status=request.payment_status,
        description=request.description
        )
        
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return {
            "status": "success",
            "message": "Registration successful",
            "payload": {"account": account.account_id},
        }
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(detail=f"Email already exists", status_code=status.HTTP_400_BAD_REQUEST)

@auth_rout.post("/login_account")  
async def login_account(request: LoginAccount, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Account).where(Account.email_id == request.email_id))
        account = result.scalars().first()
        if not account:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)
        
        if not check_hash_password(password=request.password, hashed_password=account.password):
            raise HTTPException(detail="Invalid password", status_code=status.HTTP_400_BAD_REQUEST)
        
        if not account.email_verified:
            raise HTTPException(detail="Email not verified. Check your email.", status_code=status.HTTP_400_BAD_REQUEST)
        
        access_token = create_access_token(payload={
            "AccountId": account.account_id,
            "AccountEmail": account.email_id,
            "AccountRole": account.role
        }, expiry=timedelta(hours=setting.ACCESS_TOKEN_EXPIRY))

        return {
            "message": "Login successful",
            "payload": {
                "account": account.account_id,
                "role": account.role,
                "access_token": access_token,
            }
        }
    except Exception as e:
        raise HTTPException(detail=f"{e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@auth_rout.get("/account", status_code=status.HTTP_201_CREATED)
async def private_page(account:Account = Depends(get_account_from_token), db: AsyncSession = Depends(get_db)):
    return {
        "msg": "Welcome Account User",
        "account": account
    }

from app.Core.security import decode_token
@auth_rout.get("/verify_email/verification/{AccessToken}", status_code=status.HTTP_200_OK)
async def verify_email_verification(AccessToken,db: AsyncSession = Depends(get_db)):
    token_data = decode_token(AccessToken)
    result = await db.execute(select(Account).where(Account.email_id == token_data["AccountEmail"]))
    account = result.scalars().first()
    if not account.email_verified:
        account.email_verified = True
        await db.commit()
        return {"msg": "Email verified"}
    return {"msg":"Alredy Verified this email"}

@auth_rout.get("/verify_email/send_token/{email}", status_code=status.HTTP_200_OK)
async def verify_email_send_token(email,db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Account).where(Account.email_id == email))
        account = result.scalars().first()
        if not account.email_verified:
            access_token = create_access_token(payload={
                                                        "AccountId": account.account_id,
                                                        "AccountEmail": account.email_id,
                                                        "AccountRole": account.role
                                                        }, expiry=timedelta(hours=setting.ACCESS_TOKEN_EXPIRY))
                                                    
            # await email_send_access_token([email.email],access_token)
            return {"message": "Email sent successfully", "payload": {"access_token": access_token}}
        return {"message": "Email Alredy Verified"}
    except Exception as e:
        return e

