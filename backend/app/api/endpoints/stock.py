from fastapi import APIRouter

router = APIRouter()

# 仮の備蓄品データ
mock_stock_list = [
    {"item_id": 1, "item_name": "水", "quantity": 100},
    {"item_id": 2, "item_name": "非常食", "quantity": 50},
    {"item_id": 3, "item_name": "懐中電灯", "quantity": 30},
]


@router.get("/")
async def get_stocks():
    """
    備蓄品一覧を取得する
    """
    return mock_stock_list


@router.post("/")
async def add_stock(item_name: str, quantity: int):
    """
    新しい備蓄品を追加する
    """
    new_id = len(mock_stock_list) + 1
    new_item = {"item_id": new_id, "item_name": item_name, "quantity": quantity}
    mock_stock_list.append(new_item)
    return {"message": "備蓄品を追加しました", "item": new_item}
