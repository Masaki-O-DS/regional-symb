import streamlit as st
from pathlib import Path
from .func import load_data

# ファイルパス
BASE_DIR = Path(__file__).resolve().parents[2]  # プロジェクトのルートを指す
file_path = BASE_DIR / "backend/app/db/kairanban.json"


def show():
    st.title("タウンリンク")
    st.write("地域の情報をつなぐ、安心をつなぐ")

    st.markdown("---")

    # 緊急情報
    st.markdown("### 緊急災害情報")
    st.error("地震が発生しました。大阪市の震度は5弱です。")

    st.markdown("---")

    # 新着 回覧板情報
    st.markdown("### 🆕 回覧板")

    titles = []
    kairan_data = load_data(file_path)

    # 未閲覧のデータだけを表示させる
    for data in kairan_data:
        if data["checked"] == True:
            titles.append(data["title"])

    list_text = "\n".join([f"- {title}" for title in titles])
    st.info(list_text)

    # 回覧板の詳細ページに遷移をするためのボタン
    if st.button(
        "詳細を見る",
        on_click=lambda: st.session_state.update({"menu_selection": "📄 回覧板"}),
    ):
        # on_click で session_state を書き換えたあと自動的に再レンダリングされます
        pass

    st.markdown("---")

    # 新着イベント情報
    st.markdown("### 今後の予定")
    event_titles = ["4/20 春の清掃活動", "5/2~5/10 火災予防習慣", "5/20 春のパン祭り"]
    event_list_text = "\n".join([f"- {title}" for title in event_titles])
    st.warning(event_list_text)
    st.button("イベント詳細を見る")
