

from fastapi import FastAPI 
from app.Database.base import init_db
from contextlib import asynccontextmanager
from app.Routes.auth import auth_rout
from app.Routes.transaction import transaction_route
from app.Routes.order import order_route
from app.Routes.analytic import analytics_route
from fastapi.middleware.cors import CORSMiddleware
# Harek Load par aa function execute thase(like.restart par)
@asynccontextmanager
async def connectingTodb(app: FastAPI):
    await init_db()
    print("Connection Done ....")
    yield


app = FastAPI(title="Leaning Api building",lifespan=connectingTodb)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_rout,prefix="/auth",tags=["Authetication"])
app.include_router(transaction_route,prefix="/transaction",tags=["Transaction"])
app.include_router(order_route,prefix="/order",tags=["Orders"])
app.include_router(analytics_route,prefix="/analytic",tags=["Analytics"])