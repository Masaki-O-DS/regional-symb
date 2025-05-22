import streamlit as st
import pandas as pd
from datetime import datetime, date

# 管理者ページ用 show() 関数


def show():
    st.title("🔧 管理者ページ")
    st.write("管理者専用の操作画面です。")

    # --- 認証ステートの初期化 ---
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # --- ログインフォーム ---
    if not st.session_state.authenticated:
        pw = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if pw == st.secrets.get("ADMIN_PASSWORD", ""):
                st.session_state.authenticated = True
                st.success("ログイン成功！管理機能を表示します。")
            else:
                st.error("パスワードが違います。")
        # 認証まだの場合は戻る（ログイン後の同一セッションでは次行をスキップ）
        if not st.session_state.authenticated:
            return

    # --- ログアウトボタン ---
    if st.button("ログアウト"):
        st.session_state.authenticated = False
        st.success("ログアウトしました。再度ログインしてください。")
        return

    # --- 初期データストア ---
    if "boards" not in st.session_state:
        st.session_state.boards = []
    if "events" not in st.session_state:
        st.session_state.events = []
    if "stocks" not in st.session_state:
        st.session_state.stocks = []
    if "minutes" not in st.session_state:
        st.session_state.minutes = []
    if "finances" not in st.session_state:
        st.session_state.finances = []

    # --- 回覧板管理 ---
    with st.expander("📋 回覧板管理"):
        st.subheader("回覧板一覧")
        st.table(pd.DataFrame(st.session_state.boards))
        with st.form("create_board"):
            b_title = st.text_input("タイトル")
            b_content = st.text_area("内容")
            if st.form_submit_button("作成"):
                st.session_state.boards.append(
                    {
                        "タイトル": b_title,
                        "内容": b_content,
                        "作成日": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
                st.success("回覧板を作成しました。")
        if st.session_state.boards:
            idx = st.selectbox(
                "編集する回覧板を選択",
                range(len(st.session_state.boards)),
                format_func=lambda i: st.session_state.boards[i]["タイトル"],
            )
            board = st.session_state.boards[idx]
            with st.form("edit_board"):
                t2 = st.text_input("タイトル", value=board["タイトル"])
                c2 = st.text_area("内容", value=board["内容"])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("更新"):
                    board.update({"タイトル": t2, "内容": c2})
                    st.success("回覧板を更新しました。")
                if col2.form_submit_button("削除"):
                    st.session_state.boards.pop(idx)
                    st.success("回覧板を削除しました。")

    # --- イベントカレンダー管理 ---
    with st.expander("🗓️ イベントカレンダー管理"):
        st.subheader("イベント一覧")
        st.table(pd.DataFrame(st.session_state.events))
        with st.form("create_event"):
            e_date = st.date_input("日付", value=date.today())
            e_title = st.text_input("タイトル")
            e_desc = st.text_area("説明")
            if st.form_submit_button("追加"):
                st.session_state.events.append(
                    {
                        "日付": e_date.strftime("%Y-%m-%d"),
                        "タイトル": e_title,
                        "説明": e_desc,
                    }
                )
                st.success("イベントを追加しました。")
        if st.session_state.events:
            idx = st.selectbox(
                "編集するイベントを選択",
                range(len(st.session_state.events)),
                format_func=lambda i: f"{st.session_state.events[i]['日付']} {st.session_state.events[i]['タイトル']}",
            )
            ev = st.session_state.events[idx]
            with st.form("edit_event"):
                d2 = st.date_input(
                    "日付", value=datetime.fromisoformat(ev["日付"]).date()
                )
                t2 = st.text_input("タイトル", value=ev["タイトル"])
                c2 = st.text_area("説明", value=ev["説明"])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("更新"):
                    ev.update(
                        {"日付": d2.strftime("%Y-%m-%d"), "タイトル": t2, "説明": c2}
                    )
                    st.success("イベントを更新しました。")
                if col2.form_submit_button("削除"):
                    st.session_state.events.pop(idx)
                    st.success("イベントを削除しました。")

    # --- 備蓄在庫管理 ---
    with st.expander("📦 備蓄在庫管理"):
        st.subheader("在庫一覧")
        df = pd.DataFrame(st.session_state.stocks)
        st.table(df)
        with st.form("create_stock"):
            s_name = st.text_input("品名")
            s_qty = st.number_input("数量", min_value=0)
            s_exp = st.date_input("消費期限")
            s_loc = st.text_input("保管場所")
            if st.form_submit_button("登録"):
                st.session_state.stocks.append(
                    {
                        "品名": s_name,
                        "数量": int(s_qty),
                        "消費期限": s_exp.strftime("%Y-%m-%d"),
                        "保管場所": s_loc,
                    }
                )
                st.success("備蓄品を登録しました。")
        if st.session_state.stocks:
            idx = st.selectbox(
                "編集する在庫を選択",
                range(len(st.session_state.stocks)),
                format_func=lambda i: st.session_state.stocks[i]["品名"],
            )
            stck = st.session_state.stocks[idx]
            with st.form("edit_stock"):
                n2 = st.text_input("品名", value=stck["品名"])
                q2 = st.number_input("数量", value=stck["数量"], min_value=0)
                e2 = st.date_input(
                    "消費期限", value=datetime.fromisoformat(stck["消費期限"]).date()
                )
                l2 = st.text_input("保管場所", value=stck["保管場所"])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("更新"):
                    st.session_state.stocks[idx].update(
                        {
                            "品名": n2,
                            "数量": int(q2),
                            "消費期限": e2.strftime("%Y-%m-%d"),
                            "保管場所": l2,
                        }
                    )
                    st.success("在庫を更新しました。")
                if col2.form_submit_button("削除"):
                    st.session_state.stocks.pop(idx)
                    st.success("在庫を削除しました。")

    # --- 議事録管理 ---
    with st.expander("📝 議事録管理"):
        st.subheader("議事録一覧")
        st.table(pd.DataFrame(st.session_state.minutes))
        with st.form("create_minutes"):
            m_t = st.text_input("タイトル")
            m_c = st.text_area("内容")
            if st.form_submit_button("作成"):
                st.session_state.minutes.append(
                    {
                        "タイトル": m_t,
                        "内容": m_c,
                        "作成日": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
                st.success("議事録を作成しました。")
        if st.session_state.minutes:
            idx = st.selectbox(
                "編集する議事録を選択",
                range(len(st.session_state.minutes)),
                format_func=lambda i: st.session_state.minutes[i]["タイトル"],
            )
            mn = st.session_state.minutes[idx]
            with st.form("edit_minutes"):
                t2 = st.text_input("タイトル", value=mn["タイトル"])
                c2 = st.text_area("内容", value=mn["内容"])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("更新"):
                    mn.update({"タイトル": t2, "内容": c2})
                    st.success("議事録を更新しました。")
                if col2.form_submit_button("削除"):
                    st.session_state.minutes.pop(idx)
                    st.success("議事録を削除しました。")

    # --- 会計情報管理 ---
    with st.expander("💰 会計情報管理"):
        st.subheader("会計情報一覧")
        st.table(pd.DataFrame(st.session_state.finances))
        with st.form("create_finance"):
            f_date = st.date_input("日付", value=date.today())
            f_type = st.selectbox("種別", ["収入", "支出"])
            f_amount = st.number_input("金額", min_value=0, step=100)
            f_desc = st.text_area("説明")
            if st.form_submit_button("登録"):
                st.session_state.finances.append(
                    {
                        "日付": f_date.strftime("%Y-%m-%d"),
                        "種別": f_type,
                        "金額": int(f_amount),
                        "説明": f_desc,
                    }
                )
                st.success("会計情報を登録しました。")
        if st.session_state.finances:
            idx = st.selectbox(
                "編集する会計情報を選択",
                range(len(st.session_state.finances)),
                format_func=lambda i: (
                    f"{st.session_state.finances[i]['日付']} "
                    f"{st.session_state.finances[i]['種別']} "
                    f"{st.session_state.finances[i]['金額']}円"
                ),
            )
            fn = st.session_state.finances[idx]
            with st.form("edit_finance"):
                f_date2 = st.date_input(
                    "日付", value=datetime.fromisoformat(fn["日付"]).date()
                )
                f_type2 = st.selectbox(
                    "種別", ["収入", "支出"], index=0 if fn["種別"] == "収入" else 1
                )
                f_amount2 = st.number_input(
                    "金額", value=fn["金額"], min_value=0, step=100
                )
                f_desc2 = st.text_area("説明", value=fn["説明"])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("更新"):
                    st.session_state.finances[idx].update(
                        {
                            "日付": f_date2.strftime("%Y-%m-%d"),
                            "種別": f_type2,
                            "金額": int(f_amount2),
                            "説明": f_desc2,
                        }
                    )
                    st.success("会計情報を更新しました。")
                if col2.form_submit_button("削除"):
                    st.session_state.finances.pop(idx)
                    st.success("会計情報を削除しました。")
