from fastapi import Depends
from database.db import DB
from supabase import Client
from fastapi import APIRouter
from fastapi import HTTPException
from schemas.schemas import Product
from database.tables import Products
from database.auth import jwtBearer

products_router = APIRouter(prefix="/products")


# FastAPI handles JSON serialization and deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Item].
@products_router.get("/")
def get_all_products() -> list[Product]:
    return Products().select().execute().data


@products_router.get("/amazon/")
def scrap_amazon_product_from_url(url: str,
                                  lang: str = "en-US",
                                  method: str = "playwright") -> dict[str, dict[str, dict]]:
    from hackafor_crawler_amz import crawler
    import asyncio
    data = asyncio.run(crawler.scrap_urls(url,
                                          locales=lang,
                                          method=method))
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
def query_product_by_url(url: str | None = None) -> Product:
    response = Products().select().eq("url", url).execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {url=} does not exist.")
    return response.data[0]


@products_router.put("/amazon/")
def scrap_and_add_product_from_url(url: str,
                                   lang: str = "en-US",
                                   method: str = "playwright",
                                   token: Client = Depends(jwtBearer())) -> dict[str, dict | list]:
    urls_filtered: list[str | dict] = []
    lang = lang.split(",")[0]
    for url_ in url.split(","):
        if not Products().select("url, lang").eq("url", url_).eq("lang", lang).execute().data:
            urls_filtered.append(url_)

    from hackafor_crawler_amz import crawler
    import asyncio
    data_modified = []
    urls_data = asyncio.run(crawler.scrap_urls(urls_filtered,
                                               locales=lang,
                                               method=method))
    for url_ in url.split(","):
        if url_ not in urls_filtered:
            data_modified.append({
                "error": "Product already added, use PATCH method instead.",
                "url": url,
                "lang": lang
            })
            continue
        lang_data = urls_data[url_]
        for lang, product_data in lang_data.items():
            if "error" in product_data:
                product_data["error"] = str(product_data["error"])
                data_modified.append(product_data)
                continue
            product_data["store"] = "amazon"
            img_link_split: list = product_data.get("image").split(".")
            img_link_split.pop(-2)
            img_size_updated = ".".join(img_link_split)
            product_data["image"] = img_size_updated
            data_modified.append(product_data)
            updated_data = Product.parse_obj(product_data)
            supabase = DB().supabase
            supabase.postgrest.auth(token)
            response = supabase.table("products") \
                .insert(updated_data.dict(exclude_none=True)) \
                .execute()
            data_modified.append(response.data)
    return {
        "query": {"url": url, "lang": lang, "method": method},
        "result": data_modified
    }


@products_router.patch("/amazon/{product_id}")
def scrap_and_update_product_by_id(product_id: int,
                                   url: str = None,
                                   lang: str = "en-US",
                                   method: str = "playwright",
                                   token: Client = Depends(jwtBearer())) -> dict[str, dict]:
    lang = lang.split(",")[0]
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
    import asyncio

    urls_data = asyncio.run(crawler.scrap_urls(url,
                                               locales=lang,
                                               method=method))
    lang_data = urls_data[url]
    product_data = lang_data[lang]

    if "error" in product_data:
        updated_data = product_data
        updated_data["error"] = str(updated_data["error"])
        return {
            "query": {"id": product_id,
                      "url": url},
            "response": {
                "original": original_data,
                "error": updated_data
            }
        }
    else:
        updated_data = Product.parse_obj({
            "name": original_data["name"],
            "full_name": product_data["full_name"],
            "price": product_data["price"],
            "image": product_data["image"],
            "url": url,
            "store": "amazon",
            "categories": product_data["categories"],
            "lang": lang
        })
        supabase = DB().supabase
        supabase.postgrest.auth(token)
        response = supabase.table("products") \
            .update(updated_data.dict(exclude_none=True)) \
            .eq("id", product_id).execute()
        return {
            "query": {"id": product_id,
                      "url": url},
            "response": {
                "original": original_data,
                "updated": response.data[0]
            }
        }


# @products_router.patch("/amazon/")
# def scrap_and_update_product_by_url(url: str,
#                                     lang: str = "en-US",
#                                     method: str = "playwright") -> dict[str, dict]:
#     lang = lang.split(",")[0]

#     urls_filtered: list[str | dict] = []
#     lang = lang.split(",")[0]
#     for url_ in url.split(","):
#         if Products().select("url, lang").eq("url", url_).eq("lang", lang).execute().data:
#             urls_filtered.append(url_)
#     if not urls_filtered:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Product with {url=} does not exist.")

#     for url_ in urls_filtered:
#         original_data = response.data[0]
#         original_store = original_data.get("store")
#         original_url = original_data.get("url")
#         if original_store != "amazon":
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"This request only works with 'amazon' products, not '{original_store}'."
#             )
#         if not original_url and not url:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"URL value required on either database or parameters."
#             )
#         url = url if url else original_url
#         if "," in url:
#             url = url.split(",")[0]

#         if not url.startswith("https://a.co"):
#             raise HTTPException(
#                 status_code=400,
#                 detail="This request only works for amazon urls that contains 'https://a.co'."
#             )

#     from hackafor_crawler_amz import crawler
#     import asyncio

#     urls_data = asyncio.run(crawler.scrap_urls(url,
#                                                locales=lang,
#                                                method=method))
#     lang_data = urls_data[url]
#     product_data = lang_data[lang]

#     if "error" in product_data:
#         updated_data = product_data
#         updated_data["error"] = str(updated_data["error"])
#         return {
#             "query": {"id": original_data["id"],
#                       "url": url},
#             "response": {
#                 "original": original_data,
#                 "error": updated_data
#             }
#         }
#     else:
#         updated_data = Product.parse_obj({
#             "name": original_data["name"],
#             "full_name": product_data["full_name"],
#             "price": product_data["price"],
#             "image": product_data["image"],
#             "url": url,
#             "store": "amazon",
#             "categories": product_data["categories"],
#             "lang": lang
#         })
#         response = Products().update(original_data["id"], updated_data)
#         return {
#             "query": {"id": original_data["id"],
#                       "url": url},
#             "response": {
#                 "original": original_data,
#                 "updated": response.data[0]
#             }
#         }


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
