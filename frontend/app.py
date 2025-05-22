import streamlit as st

# 各ページをインポート
import modules.dashboard as dashboard
import modules.event_calendar as event_calendar
import modules.kairanban as kairanban
import modules.stock_list as stock_list
import modules.chat as chat
import modules.financial_report as financial_report
import modules.meeting as meeting
import modules.admin as admin

# メニュー（表示名 -> ページ識別子）
menu = {
    "🏠 ダッシュボード": "dashboard",
    "📅 イベントカレンダー": "event_calendar",
    "📄 回覧板": "kairanban",
    "📦 備蓄一覧": "stock_list",
    "💬 チャット": "chat",
    "📊 収支報告": "financial_report",
    "📝 議事録": "meeting",
    "🔧 管理者ページ": "admin",
}


# サイドバーにメニューを表示
st.sidebar.title("メニュー")
selection = st.sidebar.selectbox(
    "ページを選択してください",
    list(menu.keys()),
    key="menu_selection",  # ← セッションステートに保存させる
)


# 選択されたページを表示
page = menu[st.session_state.menu_selection]

if page == "dashboard":
    dashboard.show()
elif page == "event_calendar":
    event_calendar.show()
elif page == "kairanban":
    kairanban.show()
elif page == "stock_list":
    stock_list.show()
elif page == "chat":
    chat.show()
elif page == "financial_report":
    financial_report.show()
elif page == "meeting":
    meeting.show()
elif page == "admin":
    admin.show()
