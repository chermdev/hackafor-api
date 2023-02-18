from postgrest import APIResponse
from postgrest import SyncRequestBuilder
from postgrest import SyncSelectRequestBuilder
from database.db import DB
from database.db import Client
from schemas.schemas import Product
from schemas.schemas import Score


class Table:

    table_name: str

    def __init__(self, supabase: Client = None) -> None:
        if supabase:
            self.supabase = supabase
        else:
            self.supabase = DB().supabase

    def table(self) -> SyncRequestBuilder:
        return self.supabase.table(self.table_name)

    def select(self, columns="*") -> SyncSelectRequestBuilder:
        return self.table().select(columns)

    def insert(self) -> APIResponse:
        ...

    def update(self, id: int, data: dict) -> APIResponse:
        return self.table().update(data).eq("id", id).execute()


class Products(Table):

    table_name: str = "products"

    def insert(self, product: Product) -> APIResponse:
        return self.table().insert(product.dict()).execute()


class Ranking(Table):

    table_name: str = "ranking"

    def insert(self, score: Score) -> APIResponse:
        return self.table().insert(score.dict()).execute()
