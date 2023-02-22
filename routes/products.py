from fastapi import APIRouter
from fastapi import HTTPException
from schemas.schemas import Product
# from schemas.schemas import Category
from database.tables import Products

products_router = APIRouter(prefix="/products")


# FastAPI handles JSON serialization and deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Item].
@products_router.get("/")
def index() -> list[Product]:
    return Products().select().execute().data


@products_router.get("/{product_id}")
def query_item_by_id(product_id: int) -> Product:
    response = Products().select().eq("id", product_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {product_id=} does not exist.")
    return response.data[0]


@products_router.get("/amazon/")
def srap_amazon_product_data(
    url: str
) -> list[Product]:
    from hackafor_crawler_amz import crawler
    data = crawler.scrap_urls(url)
    return data


@products_router.patch("/amazon/{product_id}")
def query_item_by_id(product_id: int, url: str = None) -> dict[str, dict]:
    response = Products().select().eq("id", product_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {product_id=} does not exist.")
    original_data = response.data[0]
    original_store = original_data.get("store")
    original_url = original_data.get("url")
    if original_store != "amazon":
        raise HTTPException(
            status_code=400,
            detail=f"This request only works with 'amazon' products, not '{original_store}'."
        )
    if not original_url and not url:
        raise HTTPException(
            status_code=400,
            detail=f"URL value required on either database or parameters."
        )
    url = url if url else original_url
    if "," in url:
        url = url.split(",")[0]

    if not url.startswith("https://a.co"):
        raise HTTPException(
            status_code=400,
            detail="This request only works for amazon urls that contains 'https://a.co'."
        )

    from hackafor_crawler_amz import crawler
    data_scrap = crawler.scrap_urls(url)[0]
    updated_data = {
        "name": original_data["name"],
        "full_name": data_scrap["full_name"],
        "price": data_scrap["price"],
        "image": data_scrap["image"],
        "url": url,
        "store": "amazon",
        "categories": data_scrap["categories"]
    }
    Products().update(product_id, updated_data)
    return {
        "query": {"id": product_id,
                  "url": url},
        "response": {
            "original": original_data,
            "updated": updated_data
        }
    }


# # Selection = dict[str, str | int | float | Category | None]
# Selection = dict[str, str | int | float | None]

# TODO: WIP
# @products_router.get("/products/")
# def query_item_by_parameters(
#     name: str | None = None,
#     min_price: float | None = None,
#     max_price: float | None = None,
#     category: str | None = None
# ) -> dict[str, Selection | list[Product]]:
#     def check_item(item: Product) -> bool:
#         """  """
#         return all(
#             (
#                 name is None or name.lower() in item.name.lower(),
#                 min_price is None or item.price > min_price,
#                 max_price is None or item.price < max_price,
#                 category is None or item.category is category,
#             )
#         )

#     selection = [product for product in products_db if check_item(product)]
#     return {
#         "query": {"name": name,
#                   "min_price": min_price,
#                   "max_price": max_price,
#                   "category": category},
#         "products": selection
#     }
