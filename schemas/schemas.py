from enum import Enum
from pydantic import BaseModel


class Category(str, Enum):
    LAPTOP = "laptop"
    ELECTRONICOS = "electronicos"
    OFICINA = "oficina"


class Product(BaseModel):
    id: int
    name: str
    full_name: str
    price: float
    image: str
    category: str


class Score(BaseModel):
    id: int
    created_at: str
    updated_at: str
    username: str
    score: dict
    name: str = None
    avatar: str = None
