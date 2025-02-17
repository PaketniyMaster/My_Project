from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from app.routes import auth
from app.swagger_config import custom_openapi
from fastapi.middleware.cors import CORSMiddleware


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать конкретные источники, например: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т. д.)
    allow_headers=["*"],  # Разрешить все заголовки
)


@app.get("/")
async def root():
    return {"message": "API is running!"}
