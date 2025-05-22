import streamlit as st
from pathlib import Path
from .func import load_data, update_item

# ファイルパス
BASE_DIR = Path(__file__).resolve().parents[2]  # プロジェクトのルートを指す
file_path = BASE_DIR / "backend/app/db/kairanban.json"


def show():
    kairanban_data = load_data(file_path)
    st.title("📄 回覧板")

    for item in kairanban_data:
        if item["checked"] == True:
            continue
        st.markdown("---")

        # 表示コンテナ（HTML風にスタイル適用）
        with st.container():
            st.markdown(
                f"""
                <div >
                    <h3 style="margin-bottom: 0;">{item['title']}</h3>
                    <p style="color: gray; margin-top: 2px;">{item['date'].split('T')[0]}</p>
                    <p>{item['detail']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # チェックボックス状態を取得（状態管理のため key をユニークに）
        checked = st.checkbox(
            f"{item['title']} を確認しました",
            value=item.get("checked", False),
            key=f"check_{item['id']}",
        )

        if checked:
            update_item(file_path, item["id"], checked=True)
            st.rerun()
