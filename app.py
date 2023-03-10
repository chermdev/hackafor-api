from fastapi import FastAPI
from routes.auth import auth_router
from routes.user import user_router
from routes.ranking import ranking_router
from routes.products import products_router
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(ranking_router)
app.include_router(products_router)


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/docs")
