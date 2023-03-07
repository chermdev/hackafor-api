from database.db import DB
from fastapi import Request
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import HTTPException
from routes.ranking import Ranking
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
def get_user_info(request: Request) -> dict[str, dict]:
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
        keys_to_collect: tuple = (
            "id", "app_metadata", "user_metadata", "email", "phone")
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
        ranking_data = Ranking.parse_obj(game_played.dict(exclude_none=True,
                                                          exclude_unset=True))
        # check if user has ranking
        ranking_response = supabase.table("ranking") \
            .select("*") \
            .eq("username", user_response.user.id).execute()
        if ranking_response.data:
            if game_played.score > ranking_response.data[0]["score"]:
                supabase.table("ranking") \
                    .update(ranking_data.dict(exclude_none=True)) \
                        .eq("username", user_response.user.id).execute()
        else:
            supabase.table("ranking") \
                    .insert(ranking_data.dict(exclude_none=True)).execute()

        return response.data
    except APIError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err.message))
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
