import os
from dotenv import load_dotenv
from supabase import Client
from supabase import create_client


load_dotenv()


URL: str = os.environ.get("SUPABASE_URL")
KEY: str = os.environ.get("SUPABASE_KEY")


class DB:

    supabase: Client

    def __init__(self) -> None:
        self.supabase = create_client(URL, KEY)
