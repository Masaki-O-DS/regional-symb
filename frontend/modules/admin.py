import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from pathlib import Path
from . import func

# --- ファイルパス定義 ---
Path(__file__).resolve().parent.parent  # admin_page.pyがpages/にある場合など
BASE_DIR = Path(__file__).resolve().parents[2]  # プロジェクトのルートを指す
KAIRANBAN_FILE = BASE_DIR / "backend/app/db/kairanban.json"
EVENT_FILE = BASE_DIR / "backend/app/db/event.json"
STOCK_FILE = BASE_DIR / "backend/app/db/stock_data.json"
MINUTES_FILE = BASE_DIR / "backend/app/db/minutes.json"  # 議事録
FINANCES_FILE = BASE_DIR / "backend/app/db/finances.json"


# --- 共通ヘルパー関数 ---
def display_table(data):
    """データがない場合はメッセージを表示し、ある場合はテーブルを表示"""
    if not data:
        st.info("データがありません。")
    else:
        # ID を含めて表示（編集/削除時に参照しやすくするため）
        df = pd.DataFrame(data)
        st.dataframe(df)  # st.table より st.dataframe の方が見やすい場合がある


def get_item_by_id(data, item_id):
    """IDでアイテムを検索 (IDは整数として比較)"""
    try:
        target_id = int(item_id)
        for item in data:
            if item.get("id") == target_id:
                return item
    except (ValueError, TypeError):
        pass  # IDが不正な場合は None を返す
    return None


def parse_datetime_safe(dt_str):
    """ISO形式の日時文字列をdatetimeに変換。失敗したらNoneを返す。"""
    if not dt_str:
        return None
    try:
        # 'T' があればそのまま、なければ日付としてパース
        if "T" in dt_str:
            return datetime.fromisoformat(dt_str)
        else:
            return datetime.combine(date.fromisoformat(dt_str), time.min)
    except ValueError:
        return datetime.now()  # パース失敗時は現在時刻（またはNone）


# --- 管理者ページ用 show() 関数 ---
def show():
    st.title("🔧 管理者ページ")
    st.write("管理者専用の操作画面です。")

    # --- 認証 ---
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        pw = st.text_input(
            "パスワードを入力してください", type="password", key="admin_pw"
        )
        if st.button("ログイン"):
            if pw == st.secrets.get("ADMIN_PASSWORD", "your_default_password"):
                st.session_state.authenticated = True
                st.success("ログイン成功！")
                st.rerun()
            else:
                st.error("パスワードが違います。")
        return
    if st.button("ログアウト"):
        st.session_state.authenticated = False
        st.success("ログアウトしました。")
        st.rerun()

    # --- 回覧板管理 (kairanban.json) ---
    with st.expander("📋 回覧板管理", expanded=False):
        boards_data = func.load_data(KAIRANBAN_FILE)
        st.subheader("回覧板一覧")
        display_table(boards_data)

        st.subheader("新規作成")
        with st.form("create_board", clear_on_submit=True):
            b_title = st.text_input("タイトル", key="b_title_new")
            b_detail = st.text_area("内容", key="b_detail_new")
            b_editor = st.text_input(
                "編集者", value="管理者", key="b_editor_new"
            )  # 固定 or 入力
            if st.form_submit_button("作成"):
                if b_title and b_detail:
                    func.add_item(
                        KAIRANBAN_FILE,
                        {
                            "title": b_title,
                            "date": datetime.now().isoformat(),  # ISO形式で保存
                            "detail": b_detail,
                            "editor": b_editor,
                            "checked": False,  # 新規作成時は未確認
                        },
                    )
                    st.success("回覧板を作成しました。")
                    st.rerun()
                else:
                    st.warning("タイトルと内容を入力してください。")

        st.subheader("編集・削除")
        if boards_data:
            board_options = {
                f"{item['title']} (ID: {item['id']})": item["id"]
                for item in boards_data
            }
            selected_str = st.selectbox(
                "編集する回覧板を選択", options=board_options.keys(), key="select_board"
            )
            selected_id = board_options.get(selected_str)

            if selected_id:
                board = get_item_by_id(boards_data, selected_id)
                with st.form("edit_board"):
                    t2 = st.text_input(
                        "タイトル", value=board["title"], key="b_title_edit"
                    )
                    d2 = st.text_area(
                        "内容", value=board["detail"], key="b_detail_edit"
                    )
                    e2 = st.text_input(
                        "編集者",
                        value=board.get("editor", "管理者"),
                        key="b_editor_edit",
                    )
                    c2 = st.checkbox(
                        "確認済み",
                        value=board.get("checked", False),
                        key="b_checked_edit",
                    )
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("更新"):
                        func.update_item(
                            KAIRANBAN_FILE,
                            selected_id,
                            title=t2,
                            detail=d2,
                            editor=e2,
                            checked=c2,
                        )
                        st.success("回覧板を更新しました。")
                        st.rerun()
                    if col2.form_submit_button("削除", type="primary"):
                        func.delete_item(KAIRANBAN_FILE, selected_id)
                        st.success("回覧板を削除しました。")
                        st.rerun()

    # --- イベントカレンダー管理 (event.json) ---
    with st.expander("🗓️ イベントカレンダー管理", expanded=False):
        events_data = func.load_data(EVENT_FILE)
        st.subheader("イベント一覧")
        display_table(events_data)

        st.subheader("新規追加")
        with st.form("create_event", clear_on_submit=True):
            e_title = st.text_input("タイトル", key="e_title_new")
            e_start_date = st.date_input(
                "開始日", value=date.today(), key="e_start_date_new"
            )
            e_start_time = st.time_input("開始時刻", key="e_start_time_new")
            e_end_date = st.date_input("終了日", value=date.today(), key="e_end_date_new")
            e_end_time = st.time_input("終了時刻", key="e_end_time_new")
            e_details = st.text_area("詳細", key="e_details_new")
            if st.form_submit_button("追加"):
                if e_title:
                    func.add_item(
                        EVENT_FILE,
                        {
                            "title": e_title,
                            "start": datetime.combine(e_start_date, e_start_time).isoformat(),
                            "end": datetime.combine(e_end_date, e_end_time).isoformat(),
                            "details": e_details,
                            "added": date.today().isoformat(),
                        },
                    )
                    st.success("イベントを追加しました。")
                    st.rerun()
                else:
                    st.warning("タイトルを入力してください。")

        st.subheader("編集・削除")
        if events_data:
            event_options = {
                f"{item['title']} (ID: {item['id']})": item["id"]
                for item in events_data
            }
            selected_str = st.selectbox(
                "編集するイベントを選択",
                options=event_options.keys(),
                key="select_event",
            )
            selected_id = event_options.get(selected_str)

            if selected_id:
                ev = get_item_by_id(events_data, selected_id)
                with st.form("edit_event"):
                    t2 = st.text_input(
                        "タイトル", value=ev["title"], key="e_title_edit"
                    )
                    start_dt = parse_datetime_safe(ev["start"]) or datetime.now()
                    end_dt = parse_datetime_safe(ev["end"]) or datetime.now()
                    s2_date = st.date_input(
                        "開始日",
                        value=start_dt.date(),
                        key="e_start_date_edit",
                    )
                    s2_time = st.time_input(
                        "開始時刻",
                        value=start_dt.time(),
                        key="e_start_time_edit",
                    )
                    e2_date = st.date_input(
                        "終了日",
                        value=end_dt.date(),
                        key="e_end_date_edit",
                    )
                    e2_time = st.time_input(
                        "終了時刻",
                        value=end_dt.time(),
                        key="e_end_time_edit",
                    )
                    d2 = st.text_area("詳細", value=ev["details"], key="e_details_edit")
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("更新"):
                        func.update_item(
                            EVENT_FILE,
                            selected_id,
                            title=t2,
                            start=datetime.combine(s2_date, s2_time).isoformat(),
                            end=datetime.combine(e2_date, e2_time).isoformat(),
                            details=d2,
                        )
                        st.success("イベントを更新しました。")
                        st.rerun()
                    if col2.form_submit_button("削除", type="primary"):
                        func.delete_item(EVENT_FILE, selected_id)
                        st.success("イベントを削除しました。")
                        st.rerun()

    # --- 備蓄在庫管理 (stock.json) ---
    with st.expander("📦 備蓄在庫管理", expanded=False):
        stocks_data = func.load_data(STOCK_FILE)
        st.subheader("在庫一覧")
        display_table(stocks_data)

        st.subheader("新規登録")
        with st.form("create_stock", clear_on_submit=True):
            s_name = st.text_input("品名", key="s_name_new")
            s_loc = st.text_input("格納場所", key="s_loc_new")
            s_qty = st.number_input("数量", min_value=0, step=1, key="s_qty_new")
            s_unit = st.text_input("単位", key="s_unit_new")
            s_store_date = st.date_input(
                "保管日", value=date.today(), key="s_store_date_new"
            )
            s_exp_date = st.date_input(
                "消費期限", value=date.today(), key="s_exp_date_new"
            )
            if st.form_submit_button("登録"):
                if s_name:
                    func.add_item(
                        STOCK_FILE,
                        {
                            "品名": s_name,
                            "格納場所": s_loc,
                            "数量": int(s_qty),
                            "単位": s_unit,
                            "保管日": s_store_date.isoformat(),
                            "消費期限": s_exp_date.isoformat(),
                        },
                    )
                    st.success("備蓄品を登録しました。")
                    st.rerun()
                else:
                    st.warning("品名を入力してください。")

        st.subheader("編集・削除")
        if stocks_data:
            # ID があることを前提とする。なければ品名で代用（重複リスクあり）
            stock_options = {
                f"{item['品名']} (ID: {item.get('id', 'N/A')})": item.get("id")
                for item in stocks_data
            }
            selected_str = st.selectbox(
                "編集する在庫を選択", options=stock_options.keys(), key="select_stock"
            )
            selected_id = stock_options.get(selected_str)

            if selected_id:
                stck = get_item_by_id(stocks_data, selected_id)
                with st.form("edit_stock"):
                    n2 = st.text_input("品名", value=stck["品名"], key="s_name_edit")
                    l2 = st.text_input(
                        "格納場所", value=stck["格納場所"], key="s_loc_edit"
                    )
                    q2 = st.number_input(
                        "数量",
                        value=stck["数量"],
                        min_value=0,
                        step=1,
                        key="s_qty_edit",
                    )
                    u2 = st.text_input("単位", value=stck["単位"], key="s_unit_edit")
                    sd2 = st.date_input(
                        "保管日",
                        value=parse_datetime_safe(stck["保管日"]).date(),
                        key="s_store_date_edit",
                    )
                    se2 = st.date_input(
                        "消費期限",
                        value=parse_datetime_safe(stck["消費期限"]).date(),
                        key="s_exp_date_edit",
                    )
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("更新"):
                        func.update_item(
                            STOCK_FILE,
                            selected_id,
                            品名=n2,
                            格納場所=l2,
                            数量=int(q2),
                            単位=u2,
                            保管日=sd2.isoformat(),
                            消費期限=se2.isoformat(),
                        )
                        st.success("在庫を更新しました。")
                        st.rerun()
                    if col2.form_submit_button("削除", type="primary"):
                        func.delete_item(STOCK_FILE, selected_id)
                        st.success("在庫を削除しました。")
                        st.rerun()
            elif not any(item.get("id") for item in stocks_data):
                st.warning(
                    "在庫データに 'id' がありません。編集・削除機能を利用するには、stock.json にユニークな 'id' を追加してください。"
                )

    # --- 議事録管理 (変更なし) ---
    with st.expander("📝 議事録管理", expanded=False):
        minutes_data = func.load_data(MINUTES_FILE)
        st.subheader("議事録一覧")
        display_table(minutes_data)

        st.subheader("新規作成")
        with st.form("create_minutes", clear_on_submit=True):
            m_t = st.text_input("タイトル", key="m_title_new_m")
            m_c = st.text_area("内容", key="m_content_new_m")
            if st.form_submit_button("作成"):
                if m_t:
                    func.add_item(
                        MINUTES_FILE,
                        {
                            "タイトル": m_t,
                            "内容": m_c,
                            "作成日": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        },
                    )
                    st.success("議事録を作成しました。")
                    st.rerun()
                else:
                    st.warning("タイトルを入力してください。")

        st.subheader("編集・削除")
        if minutes_data:
            minute_options = {
                f"{item['タイトル']} (ID: {item.get('id', 'N/A')})": item.get("id")
                for item in minutes_data
            }
            selected_str = st.selectbox(
                "編集する議事録を選択",
                options=minute_options.keys(),
                key="select_minute_m",
            )
            selected_id = minute_options.get(selected_str)

            if selected_id:
                mn = get_item_by_id(minutes_data, selected_id)
                with st.form("edit_minutes"):
                    t2 = st.text_input(
                        "タイトル", value=mn["タイトル"], key="m_title_edit_m"
                    )
                    c2 = st.text_area("内容", value=mn["内容"], key="m_content_edit_m")
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("更新"):
                        func.update_item(
                            MINUTES_FILE, selected_id, タイトル=t2, 内容=c2
                        )
                        st.success("議事録を更新しました。")
                        st.rerun()
                    if col2.form_submit_button("削除", type="primary"):
                        func.delete_item(MINUTES_FILE, selected_id)
                        st.success("議事録を削除しました。")
                        st.rerun()

    # --- 会計情報管理 (変更なし) ---
    with st.expander("💰 会計情報管理", expanded=False):
        finances_data = func.load_data(FINANCES_FILE)
        st.subheader("会計情報一覧")
        display_table(finances_data)

        st.subheader("新規登録")
        with st.form("create_finance", clear_on_submit=True):
            f_date = st.date_input("日付", value=date.today(), key="f_date_new_f")
            f_type = st.selectbox("種別", ["収入", "支出"], key="f_type_new_f")
            f_amount = st.number_input(
                "金額", min_value=0, step=100, key="f_amount_new_f"
            )
            f_desc = st.text_area("説明", key="f_desc_new_f")
            if st.form_submit_button("登録"):
                func.add_item(
                    FINANCES_FILE,
                    {
                        "日付": f_date.strftime("%Y-%m-%d"),
                        "種別": f_type,
                        "金額": int(f_amount),
                        "説明": f_desc,
                    },
                )
                st.success("会計情報を登録しました。")
                st.rerun()

        st.subheader("編集・削除")
        if finances_data:
            finance_options = {
                f"{item['日付']} {item['種別']} {item['金額']}円 (ID: {item.get('id', 'N/A')})": item.get(
                    "id"
                )
                for item in finances_data
            }
            selected_str = st.selectbox(
                "編集する会計情報を選択",
                options=finance_options.keys(),
                key="select_finance_f",
            )
            selected_id = finance_options.get(selected_str)

            if selected_id:
                fn = get_item_by_id(finances_data, selected_id)
                with st.form("edit_finance"):
                    f_date2 = st.date_input(
                        "日付",
                        value=parse_datetime_safe(fn["日付"]).date(),
                        key="f_date_edit_f",
                    )
                    f_type2 = st.selectbox(
                        "種別",
                        ["収入", "支出"],
                        index=0 if fn["種別"] == "収入" else 1,
                        key="f_type_edit_f",
                    )
                    f_amount2 = st.number_input(
                        "金額",
                        value=fn["金額"],
                        min_value=0,
                        step=100,
                        key="f_amount_edit_f",
                    )
                    f_desc2 = st.text_area(
                        "説明", value=fn["説明"], key="f_desc_edit_f"
                    )
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("更新"):
                        func.update_item(
                            FINANCES_FILE,
                            selected_id,
                            日付=f_date2.strftime("%Y-%m-%d"),
                            種別=f_type2,
                            金額=int(f_amount2),
                            説明=f_desc2,
                        )
                        st.success("会計情報を更新しました。")
                        st.rerun()
                    if col2.form_submit_button("削除", type="primary"):
                        func.delete_item(FINANCES_FILE, selected_id)
                        st.success("会計情報を削除しました。")
                        st.rerun()


# --- アプリ実行 ---
# show()
