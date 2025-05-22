import json
from pathlib import Path
from datetime import datetime


def load_data(file_path) -> list[dict]:
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_data(file_path, data: list[dict]) -> None:
    # 上書きモードで開いてダンプ
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_item(file_path, item_id: int, **fields) -> bool:
    """
    指定した item_id のレコードだけを更新し、保存する。
    fields は更新したいキー=値 を任意に指定。
    例: update_item(3, checked=True, editor="山田")
    戻り値: 更新対象が見つかれば True、なければ False
    """
    data = load_data(file_path)
    for item in data:
        if item.get("id") == item_id:
            # 更新フィールドを反映
            for k, v in fields.items():
                item[k] = v
            save_data(file_path, data)
            return True
    return False
