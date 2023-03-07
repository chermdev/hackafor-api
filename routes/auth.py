import requests
from typing import Literal
from fastapi import Request
from fastapi import APIRouter
from pydantic import BaseModel
from database.auth import User
from fastapi import HTTPException
from gotrue.errors import AuthApiError
from starlette.responses import RedirectResponse
from typing import Any


class Register(BaseModel):
    username: str
    email: str
    password: str


class Login(BaseModel):
    username: str
    password: str


class LoginDataUserSchema(BaseModel):
    id: Any
    email: Any
    app_metadata: Any
    user_metadata: Any


class LoginDataSessionSchema(BaseModel):
    provider_token: Any
    provider_refresh_token: Any
    access_token: Any
    refresh_token: Any
    expires_in: Any
    expires_at: Any
    token_type: Any
    user: LoginDataUserSchema


class LoginDataSchema(BaseModel):
    session: LoginDataSessionSchema


class RegisterDataSchema(BaseModel):
    user: LoginDataUserSchema


class SessionToken(BaseModel):
    provider_token: str | None
    provider_refresh_token: str | None
    access_token: str
    refresh_token: str
    expires_in: int
    expires_at: int | None
    token_type: str


auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register/")
def register_new_user(register: Register) -> dict[str, str]:
    try:
        response = User().register(register.username,
                                   register.email,
                                   register.password)
        # return response
        if not response.user.identities:
            # user already created
            raise HTTPException(
                status_code=401,
                detail="User already exists, try to sign up")
        # user created, requires email confirmation or resend verification email
        # data = RegisterDataSchema.parse_obj(
        #     response.dict(exclude_none=True,
        #                   exclude_unset=True))
        return {"message": "Email confirmation sent, please check your inbox!"}
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@auth_router.get("/authorize/")
def authorize_provider(provider: Literal['google', 'github'],
                       redirect_to: str | None = None) -> RedirectResponse:
    try:
        provider_response = User().login_provider(provider=provider,
                                                  redirect_to=redirect_to)
        response = RedirectResponse(provider_response.url, status_code=302)
        return response
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@auth_router.post("/login/")
def login(login: Login) -> LoginDataSchema:
    try:
        login_response = User().login(login.username,
                                      login.password)

        data = LoginDataSchema.parse_obj(
            login_response.dict(exclude_none=True,
                                exclude_unset=True))
        return data
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
