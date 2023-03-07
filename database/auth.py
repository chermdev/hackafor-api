import urllib.parse
from database.db import DB
from fastapi import Request
from supabase import Client
from database.db import DB
from fastapi import HTTPException
from gotrue.types import AuthResponse
from gotrue.types import OAuthResponse
from gotrue.errors import AuthApiError
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials


class jwtBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True) -> None:
        super(jwtBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            jwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid or Expired Token!")
            return self.verify_jwt(credentials.credentials)
        else:
            raise HTTPException(
                status_code=403, detail="Invalid or Expired Token!")

    def verify_jwt(self, jwt_token: str) -> Client:
        try:
            supabase = DB().supabase
            # supabase.auth.get_user(jwt_token)
            supabase.postgrest.auth(jwt_token)
            return supabase
        except AuthApiError as err:
            raise HTTPException(
                status_code=400,
                detail=str(err))


class User():

    def __init__(self) -> None:
        pass

    def register(self, username: str, email: str, password: str) -> AuthResponse:
        supabase = DB().supabase
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })
        return response

    def login(self, username: str, password: str) -> AuthResponse:
        """ returns login token """
        supabase = DB().supabase
        response = supabase.auth.sign_in_with_password(
            {"email": username, "password": password})
        # response.session.access_token
        return response
    
    def login_provider(self, provider:str, redirect_to: str | None = None) -> OAuthResponse:
        """ returns login token """
        supabase = DB().supabase
        response = supabase.auth.sign_in_with_oauth({
            "provider": provider,
            "options": {
                "redirect_to": redirect_to
            }
        })
        # temp fix to issue of url encoded twice
        # https://github.com/supabase-community/gotrue-py/issues/246
        response.url = urllib.parse.unquote(response.url)
        response.url = urllib.parse.unquote(response.url)
        return response

    def logout(self, token: str) -> None:
        supabase = DB().supabase
        supabase.postgrest.auth(token=token)
        supabase.auth.sign_out()
 