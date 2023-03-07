from database.db import DB
from fastapi import Request
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import HTTPException
from gotrue.errors import AuthApiError
from postgrest.exceptions import APIError


class Ranking(BaseModel):
    id: int | None
    created_at: str | None
    username: str | None
    score: int
    data: dict | None


ranking_router = APIRouter(prefix="/ranking")


@ranking_router.get("/")
def get_ranking_list(max_results: str = 10) -> list[dict]:
    try:
        supabase = DB().supabase
        response = supabase.table("ranking").select("*").order("score",
                                                               desc=True).execute()
        return response.data[:max_results]
    except AuthApiError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
