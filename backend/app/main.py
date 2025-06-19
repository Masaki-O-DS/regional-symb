from fastapi import FastAPI
from app.api.endpoints import whisper

app = FastAPI(
    title="町内会API", description="Streamlitと連携するバックエンドAPI", version="0.1.0"
)

# APIルーター登録
# app.include_router(residents.router, prefix="/residents", tags=["Residents"])
#機能ごとに分けたファイルをアプリ本体に登録
app.include_router(whisper.router, prefix="/whisper", tags=["Whisper"])


#トップページにアクセスした際にメッセージを表示する。
#/messageなどルートごとに表示させることも可能
@app.get("/")
async def root():
    return {"message": "町内会APIへようこそ！"}
