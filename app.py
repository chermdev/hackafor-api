from fastapi import FastAPI
from routes.products import products_router
from starlette.responses import RedirectResponse


app = FastAPI()

app.include_router(products_router)


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/docs")
