
from fastapi import APIRouter,Depends
from uuid import uuid4
from sqlalchemy import select
# App
from app.Database.base import get_db, AsyncSession
from app.Schemas.Transaction import CreateTransaction
from app.Core.utility import get_account_from_token
from app.Models.models import Transaction

transaction_route =APIRouter()

@transaction_route.post("/create_transaction")
async def create_new_transaction(transaction_data:CreateTransaction,
                                 account:any=Depends(get_account_from_token),
                                 db:AsyncSession =Depends(get_db)):

    transaction = Transaction(
        transaction_id=str(uuid4()), 
        account_id=account.account_id,
        email_id=account.email_id,
        transaction_type=transaction_data.transaction_type,
        transaction_amount=transaction_data.amount,
        transaction_note=transaction_data.note
    )

    # Update account balance
    if transaction.transaction_type == "Deposit":
        account.account_balance += transaction.transaction_amount
    elif transaction.transaction_type == "Withdrawal":
        if account.account_balance >= transaction.transaction_amount:
            account.account_balance -= transaction.transaction_amount
        else:
            return {"status": "error", "message": "Insufficient funds"}

    # Add transaction and updated account to the database
    db.add(transaction)
    db.add(account)
    await db.commit()

    # Refresh the transaction and account instances
    await db.refresh(transaction)
    await db.refresh(account)

    return {
        "status": "success",
        "message": "Transaction successful",
        "payload": {"transaction_id": transaction.transaction_id}
    }

@transaction_route.get("/get_all_transactions")
async def get_all_transactions(account:any=Depends(get_account_from_token),
                                account: any = Depends(get_account_from_token),
                                db:AsyncSession =Depends(get_db)):
    # result = await db.execute(select(Transaction).where(Transaction.account_id==account.account_id))
    # transaction_list = result.scalars()
    # return list(transaction_list)

    transaction_list = db.query(Transaction).fillter(Transaction.account_id==account.account_id)
    return transaction_list