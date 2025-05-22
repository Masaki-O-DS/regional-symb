import json
from pathlib import Path
from datetime import datetime # This import is not used by the functions below, consider removing if not needed elsewhere


def load_json_data(file_path) -> list[dict]:
    """
    Loads JSON data from a file.
    Handles FileNotFoundError and JSONDecodeError.
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from file: {file_path}")
        return []


def save_json_data(file_path, data: list[dict]) -> None:
    """
    Saves data to a JSON file.
    Uses indent=4 and ensure_ascii=False.
    Handles IOError during writing.
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    try:
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError:
        print(f"Error: Could not write JSON to file: {file_path}")


def update_item(file_path, item_id: int, **fields) -> bool:
    """
    指定した item_id のレコードだけを更新し、保存する。
    fields は更新したいキー=値 を任意に指定。
    例: update_item(3, checked=True, editor="山田")
    戻り値: 更新対象が見つかれば True、なければ False
    """
    data = load_json_data(file_path) # Use new function name
    for item in data:
        if item.get("id") == item_id:
            # 更新フィールドを反映
            for k, v in fields.items():
                item[k] = v
            save_json_data(file_path, data) # Use new function name
            return True
    return False
