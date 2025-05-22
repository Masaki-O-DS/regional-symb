import streamlit as st
import requests


def show(id):
    st.title("回覧板の詳細")

    if not id:
        st.error("IDが指定されていません")
        return

    try:
        res = requests.get(f"http://localhost:8000/kairanban/{id}")
        res.raise_for_status()
        data = res.json()
        st.markdown(f"### タイトル: {data['title']}")
        st.write(f"内容: {data['body']}")
    except Exception as e:
        st.error(f"データ取得に失敗しました: {e}")
