import streamlit as st
from streamlit_calendar import calendar
from .func import load_data
from pathlib import Path
from datetime import datetime

# ファイルパス
BASE_DIR = Path(__file__).resolve().parents[2]  # プロジェクトのルートを指す
file_path = BASE_DIR / "backend/app/db/event.json"


def show():
    st.title("📅 カレンダー")
    st.write("今後の町内イベントを確認できます。")

    st.markdown("---")

    # JSONからイベント情報を読み込む
    data = load_data(file_path)
    events = data.get("events", [])

    # カレンダー表示設定
    calendar_options = {
        "initialView": "timeGridWeek",
        "slotMinTime": "07:00:00",  # 朝7時から表示
        "slotMaxTime": "19:00:00",  # 夜7時まで表示
        "allDaySlot": False,  # all-dayスロットを表示しない
        "editable": False,
        "headerToolbar": {"left": "prev", "center": "today", "right": "next"},
        "locale": "en",
        "height": 600,
    }

    # カレンダーを描画
    calendar(events=events, options=calendar_options)

    st.markdown("---")

    # 日付選択UI
    selected_date = st.date_input("確認したいイベントの日付を選んでください")

    # 該当日付のイベントを抽出
    matched = []
    for ev in events:
        start_dt = datetime.fromisoformat(ev["start"])
        end_dt = datetime.fromisoformat(ev["end"])
        if start_dt.date() <= selected_date <= end_dt.date():
            matched.append((ev, start_dt, end_dt))

    st.subheader(f"{selected_date} のイベント")

    if not matched:
        st.info("指定した日にはイベントがありません。")
        return

    # マッチしたイベントをリスト表示 + 申込フォーム
    for ev, start_dt, end_dt in matched:
        st.markdown(f"### {ev['title']}")
        st.markdown(
            f"- 🕒 時間：{start_dt.strftime('%H:%M')} ～ {end_dt.strftime('%H:%M')}"
        )
        st.markdown(f"- 📄 詳細：{ev['details']}")

        # 参加申込ポップオーバー
        def registration_form():
            with st.form(key=f"form_{ev.get('id')}"):
                name = st.text_input("氏名")
                num = st.number_input("人数", min_value=1, step=1)
                remarks = st.text_area("備考欄 (任意)")
                submitted = st.form_submit_button("送信")
                if submitted:
                    st.success(
                        f"{name} さん、{ev['title']}へのお申し込みありがとうございます！\n"
                        f"人数: {num}名, 備考: {remarks or 'なし'}"
                    )

                # 参加申込ポップオーバーをコンテキストマネージャで表示

        with st.popover("参加申込"):
            with st.form(key=f"form_{ev['id']}"):
                name = st.text_input("氏名")
                num = st.number_input("人数", min_value=1, step=1)
                remarks = st.text_area("備考欄 (任意)")
                if st.form_submit_button("送信"):
                    st.success(
                        f"{name} さん、{ev['title']}への申し込みを受け付けました！\n"
                        f"人数: {num}名, 備考: {remarks or 'なし'}"
                    )

        st.markdown("---")
