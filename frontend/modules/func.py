import json
from pathlib import Path
from datetime import datetime


def load_data(file_path: Path) -> list[dict]:
    """
    JSONファイルを読み込みます。
    ファイルが存在しない/空の場合は空のリストを返します。
    event.json の {"events": [...]} 形式に対応します。
    """
    if not file_path.exists():
        return []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return []
            data = json.loads(content)

            # event.json の特殊構造に対応
            if file_path.name == "event.json" and isinstance(data, dict):
                return data.get("events", [])
            # kairanban.json, stock.json などはリストを直接返す
            elif isinstance(data, list):
                return data
            else:
                print(
                    f"Warning: Unexpected JSON structure in {file_path}. Returning empty list."
                )
                return []

    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Warning: Could not load or parse {file_path}. Returning empty list.")
        return []


def save_data(file_path: Path, data: list[dict]) -> None:
    """
    リストをJSONファイルに保存します。
    event.json の {"events": [...]} 形式に対応します。
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # event.json の特殊構造に対応
    if file_path.name == "event.json":
        save_content = {"events": data}
    else:
        save_content = data

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(save_content, f, ensure_ascii=False, indent=4)


def get_next_id(data: list[dict]) -> int:
    """
    リスト内のデータから次のユニークなIDを生成します。
    """
    if not data:
        return 1
    # "id" が数値であることを確認し、存在しない場合は 0 として扱う
    return (
        max(int(item.get("id", 0)) for item in data if str(item.get("id", 0)).isdigit())
        + 1
    )


def add_item(file_path: Path, new_item_data: dict) -> None:
    """
    新しい項目を追加し、JSONファイルに保存します。
    自動的にIDを付与します。
    """
    data = load_data(file_path)
    new_id = get_next_id(data)
    new_item_data["id"] = new_id
    data.append(new_item_data)
    save_data(file_path, data)


def update_item(file_path: Path, item_id: int, **fields) -> bool:
    """
    指定したIDの項目を更新し、JSONファイルに保存します。
    """
    data = load_data(file_path)
    updated = False
    for item in data:
        # id を比較する際は型を合わせる（JSONからは文字列でくる可能性も考慮）
        if item.get("id") == item_id:
            item.update(fields)
            updated = True
            break
    if updated:
        save_data(file_path, data)
    return updated


def delete_item(file_path: Path, item_id: int) -> bool:
    """
    指定したIDの項目を削除し、JSONファイルに保存します。
    """
    data = load_data(file_path)
    original_length = len(data)
    # id を比較する際は型を合わせる
    data = [item for item in data if item.get("id") != item_id]
    if len(data) < original_length:
        save_data(file_path, data)
        return True
    return False
