from database.db import DB
from fastapi import Request
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import HTTPException
from gotrue.errors import AuthApiError
from postgrest.exceptions import APIError


class SessionToken(BaseModel):
    token: str


class GamePlayed(BaseModel):
    id: int | None
    created_at: str | None
    username: str | None
    score: int
    data: dict | None


user_router = APIRouter(prefix="/user")


@user_router.get("/info")
def get_user_info(request: Request) -> dict:
    try:
        # get auth
        header_auth = request.headers.get('authorization')
        if not header_auth:
            raise HTTPException(
                status_code=401, detail="Authorization token not found")
        token_type, access_token = header_auth.split(" ")

        # get session
        supabase = DB().supabase
        response = supabase.auth.get_user(access_token)

        # filter response keys
        keys_to_collect: tuple = ("email", "phone", "user_metadata")
        user_data = {user_key: {key: val
                                for key, val
                                in user_data.items()
                                if key in keys_to_collect}
                     for user_key, user_data
                     in response.dict().items()}
        return user_data
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@user_router.get("/games/")
def get_user_games_played(request: Request) -> list[GamePlayed]:
    try:
        # get auth
        header_auth = request.headers.get('authorization')
        if not header_auth:
            raise HTTPException(
                status_code=401, detail="Authorization token not found")
        token_type, access_token = header_auth.split(" ")

        # get session
        supabase = DB().supabase
        user_response = supabase.auth.get_user(access_token)
        supabase.postgrest.auth(access_token)
        # select data
        response = supabase.table("games").select(
            "*").eq("username", user_response.user.id).execute()
        return response.data
    except APIError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err.message))
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@user_router.post("/game_played/")
def add_user_score(game: GamePlayed, request: Request) -> list:
    try:
        # get auth
        header_auth = request.headers.get('authorization')
        if not header_auth:
            raise HTTPException(
                status_code=401, detail="Authorization token not found")
        token_type, access_token = header_auth.split(" ")

        # get session
        supabase = DB().supabase
        user_response = supabase.auth.get_user(access_token)
        supabase.postgrest.auth(access_token)
        # insert data
        game.username = user_response.user.id
        game_played = GamePlayed.parse_obj(game.dict(exclude_none=True,
                                                     exclude_unset=True))
        response = supabase.table("games").insert(
            game_played.dict(exclude_none=True)).execute()
        return response.data
    except APIError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err.message))
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
