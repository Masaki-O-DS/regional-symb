import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import random


def show():
    st.title("📊 収支報告")
    st.write("町内会費の収支状況を確認できます。")

    # ダミーデータ生成：過去12ヶ月の月別収支
    months = (
        pd.date_range(end=date.today(), periods=12, freq="M").strftime("%Y-%m").tolist()
    )
    incomes = [random.randint(50_000, 150_000) for _ in months]  # 収入
    expenses = [random.randint(30_000, 120_000) for _ in months]  # 支出
    net = [inc - exp for inc, exp in zip(incomes, expenses)]  # 月次収支
    balance = np.cumsum(net)  # 残高推移

    df = pd.DataFrame(
        {
            "月": months,
            "収入（円）": incomes,
            "支出（円）": expenses,
            "月次収支（円）": net,
            "残高（円）": balance,
        }
    )

    # テーブル表示
    st.subheader("月別収支一覧")
    st.dataframe(df)

    # 収入・支出の推移グラフ
    st.subheader("収入・支出推移")
    st.line_chart(df.set_index("月")[["収入（円）", "支出（円）"]])

    # 残高推移グラフ
    st.subheader("残高推移")
    st.line_chart(df.set_index("月")["残高（円）"])

    # —— 支出内訳の生成 —— #
    categories = ["備品購入", "交通費", "会場費", "通信費", "その他"]
    breakdown_data = {}
    for month, exp in zip(months, expenses):
        weights = np.random.rand(len(categories))
        values = (weights / weights.sum() * exp).round().astype(int)
        breakdown_data[month] = dict(zip(categories, values))

    # ユーザーに表示する月を選択させる
    selected_month = st.selectbox("▶ 支出内訳を表示する月を選択", months)

    # 選択月の支出内訳をDataFrame化
    breakdown_df = (
        pd.DataFrame.from_dict(
            breakdown_data[selected_month], orient="index", columns=["支出（円）"]
        )
        .rename_axis("カテゴリ")
        .reset_index()
    )

    # 支出内訳表示
    st.subheader(f"{selected_month} の支出内訳")
    st.dataframe(breakdown_df)

    # 支出内訳のグラフ化
    st.bar_chart(breakdown_df.set_index("カテゴリ"))
