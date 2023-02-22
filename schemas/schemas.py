from enum import Enum
from pydantic import BaseModel


class Category(str, Enum):
    LAPTOP = "laptop"
    ELECTRONICOS = "electronicos"
    OFICINA = "oficina"


class Product(BaseModel):
    id: int | None
    name: str | None
    full_name: str
    price: float
    image: str
    url: str
    store: str
    categories: list


class Score(BaseModel):
    id: int
    created_at: str
    updated_at: str
    username: str
    score: dict
    name: str = None
    avatar: str = None
