from database.db import DB
from fastapi import Request
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import HTTPException
from gotrue.errors import AuthApiError
from postgrest.exceptions import APIError


class UserMetadata(BaseModel):
    user_name: str
    avatar_url: str


class RankingData(BaseModel):
    user_metadata: UserMetadata


class Ranking(BaseModel):
    id: int | None
    rank: str | None
    created_at: str | None
    username: str | None
    score: int
    data: RankingData | None


ranking_router = APIRouter(prefix="/ranking")


@ranking_router.get("/")
def get_ranking_list(max_results: int = 10) -> list[Ranking]:
    try:
        supabase = DB().supabase
        response = supabase.table("ranking").select("*").order("score",
                                                               desc=True).execute()
        for n, data in enumerate(response.data, start=1):
            data["rank"] = n
        return response.data[:max_results]
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
