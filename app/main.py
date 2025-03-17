from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routers import auth
from app.routers import search

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Game Recommender API",
        version="1.0.0",
        description="API for game recommendations",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
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
    ],
    dependencies=[Depends(oauth2_scheme)]
)

app.openapi = lambda: custom_openapi(app)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(search.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is running!"}
