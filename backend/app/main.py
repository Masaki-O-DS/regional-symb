from fastapi import FastAPI
from app.api.endpoints import residents, meetings, stock

app = FastAPI(
    title="町内会API", description="Streamlitと連携するバックエンドAPI", version="0.1.0"
)

# APIルーター登録
# app.include_router(residents.router, prefix="/residents", tags=["Residents"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
app.include_router(stock.router, prefix="/stock", tags=["Stock"])


@app.get("/")
async def root():
    return {"message": "町内会APIへようこそ！"}
