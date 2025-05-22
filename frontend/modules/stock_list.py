import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from .func import load_data # Assuming load_data is in func.py at the same level

# Define BASE_DIR and file_path
BASE_DIR = Path(__file__).resolve().parents[2] # Should go up two levels from modules to regional-symb
file_path = BASE_DIR / "backend/app/db/stock_data.json"

def show():
    st.title("📦 備蓄一覧")
    st.write("災害用備蓄品の在庫を確認できます。")

    raw_data = load_data(file_path)
    data_for_df = []
    today = datetime.today().date()

    if raw_data:
        for item in raw_data:
            exp_date_str = item.get("消費期限")
            if exp_date_str:
                exp_date_obj = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
                remaining_days = abs((exp_date_obj - today).days)
            else:
                # Handle cases where 消費期限 might be missing or null
                exp_date_obj = None # Or some default date, or skip the item
                remaining_days = -1 # Or some other indicator

            data_for_df.append(
                {
                    "物品名": item.get("品名"),
                    "数量": item.get("数量"),
                    "消費期限": exp_date_str,
                    "残り消費期限（日）": remaining_days,
                    "保管場所": item.get("格納場所"),
                }
            )

    df = pd.DataFrame(data_for_df)

    # 残り消費期限が30日以下の行全体を赤字にするスタイリング
    def highlight_expired(row):
        return ["color: red" if row["残り消費期限（日）"] <= 30 else "" for _ in row]

    styled = df.style.apply(highlight_expired, axis=1)

    st.dataframe(styled)
