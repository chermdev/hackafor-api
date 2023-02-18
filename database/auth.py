from db import DB
from db import Client
from gotrue.errors import AuthApiError


# TODO: not complete, initial commit.
class User():

    def __init__(self) -> None:
        pass

    def register(self, email: str, password: str) -> DB:
        db = DB()
        db.supabase.auth.sign_up({"email": email, "password": password})
        return db

    def login(self, email: str, password: str) -> DB:
        """ returns login token """
        try:
            session = DB().supabase.auth.sign_in_with_password(
                {"email": email, "password": password})
        # TODO: Improve auth error
        except AuthApiError as err:
            # temporal print
            print(err)
        else:
            db = DB()
            db.supabase.postgrest.auth(session.session.access_token)
            return db

    def logout(self, supabase: Client) -> DB:
        supabase.auth.sign_out()
