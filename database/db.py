import os
from dotenv import load_dotenv
from supabase import Client
from supabase import create_client


load_dotenv()


class DB:

    supabase: Client

    def __init__(self) -> None:
        URL: str = os.environ.get("SUPABASE_URL")
        KEY: str = os.environ.get("SUPABASE_KEY")
        self.supabase = create_client(URL, KEY)
