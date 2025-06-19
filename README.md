# region-project

Describe your project here.

## サーバー起動

rye run uvicorn app.main:app --reload --port 8000 --app-dir backend

## フロントエンド起動
rye run streamlit run frontend/app.py