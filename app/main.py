

from fastapi import FastAPI 
from app.Database.base import init_db
from contextlib import asynccontextmanager
from app.Routes.auth import auth_rout
from app.Routes.transaction import transaction_route

# Harek Load par aa function execute thase(like.restart par)
@asynccontextmanager
async def connectingTodb(app: FastAPI):
    await init_db()
    print("Connection Done ....")
    yield


app = FastAPI(title="Leaning Api building",lifespan=connectingTodb)


app.include_router(auth_rout,prefix="/auth",tags=["Authetication"])
app.include_router(transaction_route,prefix="/transaction",tags=["Transaction"])