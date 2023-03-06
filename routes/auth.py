from fastapi import APIRouter
from pydantic import BaseModel
from database.auth import User
from fastapi import HTTPException
from gotrue.types import AuthResponse
from gotrue.errors import AuthApiError
from fastapi import Request


class Register(BaseModel):
    username: str
    email: str
    password: str


class Login(BaseModel):
    username: str
    password: str


auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register/")
def post_register(register: Register) -> AuthResponse:
    try:
        response = User().register(register.username,
                                   register.email,
                                   register.password)
        # return response
        if response.user.identities:
            # user created, requires email confirmation or resend verification email
            return response
        else:
            # user already created
            raise HTTPException(
                status_code=401,
                detail="User already exists, try to sign up")
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@auth_router.post("/login/")
def login(login: Login) -> AuthResponse:
    try:
        response = User().login(login.username,
                                login.password)
        return response
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@auth_router.post("/logout/")
def logout(request: Request) -> None:
    try:
        # get auth
        header_auth = request.headers.get('authorization')
        if not header_auth:
            raise HTTPException(
                status_code=401, detail="Authorization token not found")
        token_type, access_token = header_auth.split(" ")
        response = User().logout(access_token)
        return response
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
