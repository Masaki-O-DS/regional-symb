from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_meetings():
    return [
        {"meeting_id": 1, "title": "防災会議"},
        {"meeting_id": 2, "title": "町内祭り準備会"},
    ]
