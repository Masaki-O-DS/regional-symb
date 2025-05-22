import streamlit as st
import random


def show():
    st.title("💬 AIチャット (ダミー)")
    st.write(
        "APIを使わずに、あたかもAIと会話しているかのように動作するデモチャットです。"
    )

    # セッションステートにチャット履歴を保持
    if "history" not in st.session_state:
        st.session_state.history = []

    # 履歴を表示
    for msg in st.session_state.history:
        st.chat_message(msg["role"]).write(msg["content"])

    # ユーザー入力受付
    user_input = st.chat_input("メッセージを入力してください…")
    if user_input:
        # ユーザーメッセージを履歴に追加・表示
        st.session_state.history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # ダミーAI応答をランダム選択
        dummy_responses = [
            "それは興味深いですね。",
            "詳しく教えてもらえますか？",
            "なるほど、続けてください。",
            "はい、承知しました。",
            "お手伝いできることは他にありますか？",
        ]
        ai_reply = random.choice(dummy_responses)

        # AIメッセージを履歴に追加・表示
        st.session_state.history.append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)
