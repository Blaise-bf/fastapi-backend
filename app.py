from contextlib import asynccontextmanager
from motor import motor_asyncio
from fastapi import FastAPI
from config import BaseConfig
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from routers.cars import router as car_router
from routers.users import router as user_router

settings = BaseConfig()

# @asynccontextmanager
async def lifespan(app: FastAPI):

    app.client = motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
    app.db = app.client[settings.DB_NAME]

    try:
        app.client.admin.command('ping')
        print(f'Pinged your deployment. You have sucessfully connected to MongoDB!')
        print(f'Mongo address: {settings.DB_URL}')
    except Exception as e:
        print(e)
    # print('Starting up')
    yield
    app.client.close()
    print('Shutting down')

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(car_router, prefix='/cars', tags=['cars'])
app.include_router(user_router, prefix='/users', tags=['users'])

@app.get('/')
def get_root():
    return {'Message': 'Root working'}