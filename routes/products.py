from fastapi import APIRouter
from fastapi import HTTPException
from schemas.schemas import Product
# from schemas.schemas import Category
from database.tables import Products
from postgrest import APIResponse


products_router = APIRouter(prefix="/products")


# FastAPI handles JSON serialization and deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Item].
@products_router.get("/")
def get_all_products() -> list[Product]:
    return Products().select().execute().data


@products_router.get("/amazon/")
def scrap_amazon_product_from_url(url: str) -> list[dict]:
    from hackafor_crawler_amz import crawler
    data = crawler.scrap_urls(url)
    return data


@products_router.get("/{product_id}/")
def query_product_by_id(product_id: int) -> Product:
    response = Products().select().eq("id", product_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {product_id=} does not exist.")
    return response.data[0]


@products_router.get("/")
def query_product_by_url(url: str) -> Product:
    response = Products().select().eq("url", url).execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {url=} does not exist.")
    return response.data[0]


@products_router.put("/amazon/")
def scrap_and_add_product_from_url(url: str) -> dict[str, str | dict]:
    if Products().select("url").eq("url", url).execute().data:
        raise HTTPException(
            status_code=400,
            detail="Product already added, use PATCH method instead."
        )
    if "," in url:
        url = url.split(",")[0]
    from hackafor_crawler_amz import crawler
    product_data = crawler.scrap_urls(url)[0]
    updated_data = Product(
        full_name=product_data["full_name"],
        price=product_data["price"],
        image=product_data["image"],
        url=url,
        store="amazon",
        categories=product_data["categories"]
    )
    response = Products().insert(updated_data)
    return {
        "query": {"url": url},
        "msg": "Product added successfully!",
        "response": {
            "added": response.data
        }
    }


@products_router.patch("/amazon/{product_id}")
def scrap_and_update_product_by_id(product_id: int, url: str = None) -> dict[str, dict]:
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
    response = Products().update(product_id, updated_data)
    return {
        "query": {"id": product_id,
                  "url": url},
        "msg": "Product updated successfully!",
        "response": {
            "original": original_data,
            "updated": response.data[0]
        }
    }


@products_router.patch("/amazon/")
def scrap_and_update_product_by_url(url: str) -> dict[str, dict]:
    response = Products().select().eq("url", url).execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {url=} does not exist.")
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
    response = Products().update(original_data["id"], updated_data)
    return {
        "query": {"id": original_data["id"],
                  "url": url},
        "msg": "Product updated successfully!",
        "response": {
            "original": original_data,
            "updated": response.data[0]
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
