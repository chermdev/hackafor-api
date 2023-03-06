from database.db import DB
from supabase import Client
from gotrue.errors import AuthApiError
from gotrue.types import AuthResponse
from gotrue.types import OAuthResponse
from postgrest import SyncPostgrestClient


# TODO: not complete, initial commit.
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
    
    
    def login_github(self) -> OAuthResponse:
        """ returns login token """
        provider = 'github'
        supabase = DB().supabase
        response = supabase.auth.sign_in_with_oauth({'provider': provider})
        # response.session.access_token
        return response
    
    def login_google(self) -> OAuthResponse:
        """ returns login token """
        provider = 'google'
        supabase = DB().supabase
        response = supabase.auth.sign_in_with_oauth({'provider': provider})
        # response.session.access_token
        return response

    def logout(self, token: str) -> None:
        supabase = DB().supabase
        supabase.postgrest.auth(token=token)
        supabase.auth.sign_out()
 