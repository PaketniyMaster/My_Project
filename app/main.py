from fastapi import FastAPI
#from app.routes import game, review

app = FastAPI(title="Game Recommender API")

# Подключаем роуты
#app.include_router(game.router, prefix="/games", tags=["games"])
#app.include_router(review.router, prefix="/reviews", tags=["reviews"])

@app.get("/")
async def root():
    return {"message": "API is running!"}
