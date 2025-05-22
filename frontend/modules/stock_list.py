import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random


def show():
    st.title("📦 備蓄一覧")
    st.write("災害用備蓄品の在庫を確認できます。")

    # ダミーデータ生成
    names = [
        "水",
        "缶詰",
        "カップ麺",
        "乾パン",
        "パン",
        "バッテリー",
        "ライト",
        "救急セット",
        "毛布",
        "携帯トイレ",
        "ラジオ",
        "マスク",
        "常備薬",
        "消毒液",
        "軍手",
        "包帯",
        "乾燥果物",
        "ビスケット",
        "ミルク",
        "ガスボンベ",
    ]
    locations = ["倉庫A", "倉庫B", "屋内", "屋外", "地下室"]
    today = datetime.today().date()

    data = []
    for i in range(20):
        name = names[i % len(names)]
        quantity = random.randint(1, 50)
        # -30日から+365日の間で期限を設定
        exp_date = today + timedelta(days=random.randint(-30, 365))
        # 残日数を絶対値に（マイナスをプラス化）
        remaining = abs((exp_date - today).days)
        data.append(
            {
                "物品名": name,
                "数量": quantity,
                "消費期限": exp_date.strftime("%Y-%m-%d"),
                "残り消費期限（日）": remaining,
                "保管場所": random.choice(locations),
            }
        )

    df = pd.DataFrame(data)

    # 残り消費期限が30日以下の行全体を赤字にするスタイリング
    def highlight_expired(row):
        return ["color: red" if row["残り消費期限（日）"] <= 30 else "" for _ in row]

    styled = df.style.apply(highlight_expired, axis=1)

    st.dataframe(styled)
