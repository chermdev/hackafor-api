from database.db import DB
from supabase import Client
from fastapi import Request
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Body
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi import HTTPException
from routes.ranking import Ranking
from gotrue.errors import AuthApiError
from postgrest.exceptions import APIError
from database.auth import jwtBearer


class SessionToken(BaseModel):
    token: str
    
class Message(BaseModel):
    msg: str


class GamePlayed(BaseModel):
    id: int | None
    created_at: str | None
    username: str | None
    score: int
    data: dict | None


user_router = APIRouter(prefix="/user")


@user_router.get("/info/")
def get_user_info(token: Client = Depends(jwtBearer())) -> dict[str, dict]:
    try:
        supabase = DB().supabase
        response = supabase.auth.get_user(token)
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
def get_user_games_played(token: Client = Depends(jwtBearer())) -> list[GamePlayed]:
    try:
        supabase = DB().supabase
        supabase.postgrest.auth(token)
        user_response = supabase.auth.get_user(token)
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


@user_router.get("/ranking/")
def get_user_ranking(token: Client = Depends(jwtBearer())) -> Ranking | Message:
    try:
        supabase = DB().supabase
        supabase.postgrest.auth(token)
        user_response = supabase.auth.get_user(token)
        ranking_list = supabase.table("ranking").select("*").order("score",
                                                                   desc=True).execute().data

        # check if user has ranking
        user_ranking_data = supabase.table("ranking") \
            .select("*") \
            .eq("username", user_response.user.id).execute().data
        if not user_ranking_data:
            return {
                "msg": "Play a game to see your ranking score here."
            }
        user_rank_data = user_ranking_data[0]
        user_rank_index = ranking_list.index(user_rank_data)
        user_rank_data["rank"] = user_rank_index+1
        return user_rank_data
    except APIError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err.message))
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@user_router.post("/game_played/")
def add_user_score(game: GamePlayed = Body(), token: Client = Depends(jwtBearer())) -> list:
    try:
        supabase = DB().supabase
        supabase.postgrest.auth(token)
        user_response = supabase.auth.get_user(token)

        # insert data
        game.username = user_response.user.id
        game.data = {"user_metadata": user_response.user.user_metadata}
        game_played = GamePlayed.parse_obj(game.dict(exclude_none=True,
                                                     exclude_unset=True))
        response = supabase.table("games").insert(
            game_played.dict(exclude_none=True)).execute()
        ranking_data = Ranking.parse_obj(game_played.dict(exclude_none=True,
                                                          exclude_unset=True))
        ranking_data.data = {"user_metadata": user_response.user.user_metadata}
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
