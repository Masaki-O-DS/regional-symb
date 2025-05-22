import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import uuid # For generating unique IDs
from .func import load_json_data, save_json_data

# Define BASE_DIR and file_paths
BASE_DIR = Path(__file__).resolve().parents[2]
kairanban_file_path = BASE_DIR / "backend/app/db/kairanban.json"
event_file_path = BASE_DIR / "backend/app/db/event.json"
stock_file_path = BASE_DIR / "backend/app/db/stock_data.json"

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
    # if "boards" not in st.session_state:  # Removed for kairanban.json
    #     st.session_state.boards = []
    # if "events" not in st.session_state: # Removed for event.json
    #     st.session_state.events = []
    # if "stocks" not in st.session_state: # Removed for stock_data.json
    #     st.session_state.stocks = []
    if "minutes" not in st.session_state:
        st.session_state.minutes = []
    if "finances" not in st.session_state:
        st.session_state.finances = []

    # --- 回覧板管理 ---
    with st.expander("📋 回覧板管理"):
        st.subheader("回覧板一覧")
        boards_data = load_json_data(kairanban_file_path)

        if boards_data:
            # Ensure 'id' is present, if not, it might need assignment here for older data.
            # For now, assuming kairanban.json items always have 'id'.
            # Display specific columns, map to Japanese names if needed or adjust kairanban.py expectations.
            # For this task, showing 'id', 'title', 'date', 'detail'.
            display_df_boards = pd.DataFrame(boards_data)[['id', 'title', 'date', 'detail']]
            st.table(display_df_boards)
        else:
            st.info("回覧板データがありません。")

        with st.form("create_board"):
            b_title = st.text_input("タイトル")
            b_content = st.text_area("内容")
            if st.form_submit_button("作成"):
                new_id = uuid.uuid4().hex
                new_board = {
                    "id": new_id,
                    "title": b_title,
                    "detail": b_content,
                    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), # ISO format
                    "checked": False # Default for new items
                }
                boards_data.append(new_board)
                save_json_data(kairanban_file_path, boards_data)
                st.success("回覧板を作成しました。")
                st.rerun()

        if boards_data:
            # Use 'title' for display, ensure .get for safety if title might be missing
            board_options = {board.get("id"): board.get("title", "無題") for board in boards_data}
            selected_board_id_to_edit = st.selectbox(
                "編集する回覧板を選択",
                options=list(board_options.keys()),
                format_func=lambda board_id: board_options[board_id],
                key="select_board_edit" # Unique key for selectbox
            )
            
            # Find the full board data for the selected ID
            selected_board_for_editing = next((b for b in boards_data if b["id"] == selected_board_id_to_edit), None)

            if selected_board_for_editing:
                with st.form("edit_board"):
                    current_title = selected_board_for_editing.get("title", "")
                    current_detail = selected_board_for_editing.get("detail", "")
                    
                    t2 = st.text_input("タイトル", value=current_title)
                    c2 = st.text_area("内容", value=current_detail)
                    col1, col2 = st.columns(2)

                    if col1.form_submit_button("更新"):
                        for board_item in boards_data:
                            if board_item["id"] == selected_board_id_to_edit:
                                board_item["title"] = t2
                                board_item["detail"] = c2
                                board_item["date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") # Update date
                                break
                        save_json_data(kairanban_file_path, boards_data)
                        st.success("回覧板を更新しました。")
                        st.rerun()

                    if col2.form_submit_button("削除"):
                        boards_data = [b for b in boards_data if b["id"] != selected_board_id_to_edit]
                        save_json_data(kairanban_file_path, boards_data)
                        st.success("回覧板を削除しました。")
                        st.rerun()
            else:
                st.warning("選択された回覧板が見つかりません。") # Should not happen if selectbox is populated correctly

    # --- イベントカレンダー管理 ---
    with st.expander("🗓️ イベントカレンダー管理"):
        st.subheader("イベント一覧")
        events_data = load_json_data(event_file_path)

        if events_data:
            for event_item in events_data:
                if 'start' in event_item and 'T' in event_item['start']:
                    event_item['display_date'] = event_item['start'].split('T')[0]
                elif 'start' in event_item: # if it's just YYYY-MM-DD
                     event_item['display_date'] = event_item['start']
                else: # backward compatibility or if 'start' is missing
                    event_item['display_date'] = event_item.get('日付', 'N/A') # Fallback to '日付' if 'start' is missing

            # Ensure 'id' is present for display, use .get('id', uuid.uuid4().hex) if some items might lack it
            # For now, assuming items processed will have an id or it's not critical for display if missing
            # However, for edit/delete, ID is critical.
            display_df_events = pd.DataFrame(events_data)[['id', 'title', 'display_date', 'description']]
            display_df_events.columns = ['ID', 'タイトル', '開始日', '説明'] # Rename columns for display
            st.table(display_df_events)
        else:
            st.info("イベントデータがありません。")

        with st.form("create_event"):
            e_date = st.date_input("日付", value=date.today())
            e_title = st.text_input("タイトル")
            e_desc = st.text_area("説明")
            if st.form_submit_button("追加"):
                new_event_id = uuid.uuid4().hex
                event_date_str = e_date.strftime("%Y-%m-%d")
                new_event = {
                    "id": new_event_id,
                    "title": e_title,
                    "description": e_desc,
                    "start": event_date_str,
                    "end": event_date_str,
                }
                events_data.append(new_event)
                save_json_data(event_file_path, events_data)
                st.success("イベントを追加しました。")
                st.rerun()

        if events_data:
            # Ensure all items have an 'id' before creating selectbox options
            # This is critical if old data without 'id' might exist
            valid_events_for_selection = [ev for ev in events_data if "id" in ev]
            if not valid_events_for_selection:
                st.warning("編集可能なイベントがありません（IDが見つからないイベントがあります）。")
            else:
                event_options = {
                    event.get("id"): f"{event.get('start', '').split('T')[0]} {event.get('title', '無題')}"
                    for event in valid_events_for_selection
                }
                selected_event_id_to_edit = st.selectbox(
                    "編集するイベントを選択",
                    options=list(event_options.keys()),
                    format_func=lambda event_id: event_options[event_id],
                    key="select_event_edit"
                )

                selected_event_for_editing = next((ev for ev in valid_events_for_selection if ev["id"] == selected_event_id_to_edit), None)

                if selected_event_for_editing:
                    with st.form("edit_event"):
                        default_date_str = selected_event_for_editing.get('start', str(date.today()))
                        try:
                            current_date_val = datetime.strptime(default_date_str, "%Y-%m-%d").date()
                        except ValueError: # Handle cases where date might be in a different format or invalid
                            current_date_val = date.today()
                        
                        d2 = st.date_input("日付", value=current_date_val)
                        t2 = st.text_input("タイトル", value=selected_event_for_editing.get("title", ""))
                        c2 = st.text_area("説明", value=selected_event_for_editing.get("description", ""))
                        col1, col2 = st.columns(2)

                        if col1.form_submit_button("更新"):
                            updated_event_date_str = d2.strftime("%Y-%m-%d")
                            for event_item in events_data: # Iterate through original events_data to update
                                if event_item.get("id") == selected_event_id_to_edit:
                                    event_item["title"] = t2
                                    event_item["description"] = c2
                                    event_item["start"] = updated_event_date_str
                                    event_item["end"] = updated_event_date_str
                                    break
                            save_json_data(event_file_path, events_data)
                            st.success("イベントを更新しました。")
                            st.rerun()

                        if col2.form_submit_button("削除"):
                            events_data = [ev for ev in events_data if ev.get("id") != selected_event_id_to_edit]
                            save_json_data(event_file_path, events_data)
                            st.success("イベントを削除しました。")
                            st.rerun()
                else:
                    st.warning("選択されたイベントが見つかりません。")


    # --- 備蓄在庫管理 ---
    with st.expander("📦 備蓄在庫管理"):
        st.subheader("在庫一覧")
        stocks_data = load_json_data(stock_file_path)
        
        # Ensure each stock item has a unique 'id'.
        # This loop is primarily for display and ensuring items can be keyed.
        # Actual ID assignment for persistence happens on creation or explicit update if needed.
        for item in stocks_data:
            if 'id' not in item:
                item['id'] = uuid.uuid4().hex 
        
        if stocks_data:
            processed_stocks_for_df = []
            for item in stocks_data:
                processed_item = {
                    'id': item.get('id'), # ID should be present due to the loop above for new data
                    '品名': item.get('品名', 'N/A'),
                    '数量': item.get('数量', 0),
                    '単位': item.get('単位', 'N/A'), # Will be editable in Step 6
                    '消費期限': item.get('消費期限', 'N/A'),
                    '保管日': item.get('保管日', 'N/A'),   # Will be editable in Step 6
                    '格納場所': item.get('格納場所', 'N/A')
                }
                processed_stocks_for_df.append(processed_item)

            display_df_stocks = pd.DataFrame(processed_stocks_for_df)[['id', '品名', '数量', '単位', '消費期限', '保管日', '格納場所']]
            st.table(display_df_stocks)
        else:
            st.info("備蓄在庫データがありません。")

        with st.form("create_stock"):
            s_name = st.text_input("品名")
            s_qty = st.number_input("数量", min_value=0)
            s_exp = st.date_input("消費期限") # This is datetime.date object
            s_loc = st.text_input("保管場所")
            # Final fields for "単位" and "保管日"
            s_unit = st.text_input("単位")
            s_storage_date = st.date_input("保管日", value=date.today())

            if st.form_submit_button("登録"):
                new_stock_id = uuid.uuid4().hex
                new_stock_item = {
                    "id": new_stock_id,
                    "品名": s_name,
                    "数量": int(s_qty),
                    "消費期限": s_exp.strftime("%Y-%m-%d"),
                    "格納場所": s_loc,
                    "単位": s_unit,
                    "保管日": s_storage_date.strftime("%Y-%m-%d")
                }
                stocks_data.append(new_stock_item)
                save_json_data(stock_file_path, stocks_data)
                st.success("備蓄品を登録しました。")
                st.rerun()

        if stocks_data:
            valid_stocks_for_selection = [s for s in stocks_data if "id" in s]
            if not valid_stocks_for_selection:
                st.warning("編集/削除可能な在庫データがありません (IDを持つデータのみ)。")
            else:
                # Using title (品名) for display in selectbox
                stock_options = {stock.get("id"): stock.get("品名", "無名在庫") for stock in valid_stocks_for_selection}
                selected_stock_id_to_edit = st.selectbox(
                    "編集する在庫を選択",
                    options=list(stock_options.keys()),
                    format_func=lambda stock_id: stock_options[stock_id],
                    key="select_stock_edit"
                )
                
                current_stock_item = next((s for s in valid_stocks_for_selection if s["id"] == selected_stock_id_to_edit), None)

                if current_stock_item:
                    with st.form("edit_stock"):
                        n2 = st.text_input("品名", value=current_stock_item.get("品名",""))
                        q2 = st.number_input("数量", value=current_stock_item.get("数量",0), min_value=0)
                        
                        current_exp_date_val = date.today()
                        if current_stock_item.get("消費期限"):
                            try:
                                current_exp_date_val = datetime.strptime(current_stock_item.get("消費期限"), "%Y-%m-%d").date()
                            except ValueError:
                                pass # Keep today's date if parsing fails
                        e2 = st.date_input("消費期限", value=current_exp_date_val)
                        
                        l2 = st.text_input("格納場所", value=current_stock_item.get("格納場所",""))
                        
                        # Final fields for "単位" and "保管日"
                        un2 = st.text_input("単位", value=current_stock_item.get("単位",""))
                        
                        current_storage_date_val = date.today()
                        if current_stock_item.get("保管日"):
                            try:
                                current_storage_date_val = datetime.strptime(current_stock_item.get("保管日"), "%Y-%m-%d").date()
                            except ValueError:
                                pass # Keep today's date
                        sd2 = st.date_input("保管日", value=current_storage_date_val)

                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("更新"):
                            for item in stocks_data:
                                if item.get("id") == selected_stock_id_to_edit:
                                    item["品名"] = n2
                                    item["数量"] = int(q2)
                                    item["消費期限"] = e2.strftime("%Y-%m-%d")
                                    item["格納場所"] = l2
                                    item["単位"] = un2
                                    item["保管日"] = sd2.strftime("%Y-%m-%d")
                                    break
                            save_json_data(stock_file_path, stocks_data)
                            st.success("在庫を更新しました。")
                            st.rerun()

                        if col2.form_submit_button("削除"):
                            stocks_data = [s for s in stocks_data if s.get("id") != selected_stock_id_to_edit]
                            save_json_data(stock_file_path, stocks_data)
                            st.success("在庫を削除しました。")
                            st.rerun()
                else:
                    st.warning("選択された在庫アイテムが見つかりませんでした。")

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
