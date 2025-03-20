from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routers import auth, search
from app.routers.game_detail import router as game_router

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Game Recommender API",
        version="1.0.0",
        description="API for game recommendations",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Game Recommender API",
    docs_url="/docs",
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Operations with authentication",
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
        # "http://localhost",
        # "http://localhost:5173",
        # "http://127.0.0.1:8000",
        # "https://myproject-production-5993.up.railway.app",
        # "https://web.telegram.org",
        # "https://web.telegram.org/k/",
        # "https://t.me/GamesRec_bot/gamefinder",
        # "https://t.me/GamesRec_bot",
        # "https://myproject-production-5993.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.openapi = lambda: custom_openapi(app)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(search.router)
app.include_router(game_router)

@app.get("/")
async def root():
    return {"message": "API is running!"}

# Обработка preflight-запросов (OPTIONS)
@app.options("/{full_path:path}")
async def preflight_handler():
    return {}
