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
    category: Category
