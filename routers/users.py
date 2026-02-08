from fastapi import APIRouter, Request, Body, status, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from  authentication import AuthHandler
from models import UserModel, CurrentUserModel, LoginModel


router = APIRouter()
auth_handler = AuthHandler()

@router.post('/register', response_description='Register User')
async def register(request: Request, newUser: LoginModel = Body(...)) -> UserModel:

    users = request.app.db['users']

    # hash the password  before inserting into MongoDB

    newUser.password = auth_handler.get_password_hash(newUser.password)

    newUser = newUser.model_dump()
    # Check existing user 

    if (existing_user := await users.find_one({'username': newUser['username']})) is not None:

        raise HTTPException(status_code=409, detail=f'User with username {newUser['username']} already existing')
    
    new_user = await users.insert_one(newUser)
    created_user = await users.find_one({'_id': new_user.inserted_id})
    return created_user


@router.post('/login', response_description='Login User')
async def login(request: Request, loginUser: LoginModel = Body(...)) -> str:
    users = request.app.db['users']
    user = await users.find_one({'username': loginUser.username})
    if (user is None) or not auth_handler.verify_password(loginUser.password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(str(user['_id']), user['username'])

    respose = JSONResponse(
        content={
            'token': token,
            'username': user['username']
        }
    )

    return respose

# @router.get('/me', response_description='Logged in user data', response_model=CurrentUserModel)
# async def me(
#     request: Request,
#     response: Response,
#     user_data=Depends(auth_handler.auth_wrapper)
# ):
    
#     users = request.app.db['users']
#     currentuser = await users.find_one(
#         {'_id': ObjectId(user_data['user_id'])}
#     )

#     return currentuser

@router.get('/me', response_model=CurrentUserModel)
async def me(
    request: Request,
    user_data=Depends(auth_handler.auth_wrapper)
):
    users = request.app.db['users']

    currentuser = await users.find_one({
        '_id': ObjectId(user_data['user_id'])
    })

    if not currentuser:
        raise HTTPException(status_code=404, detail='User not found')

    return currentuser



