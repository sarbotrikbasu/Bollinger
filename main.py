import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# CONFIG
# ==========================================================

API_URL = "http://45.61.60.110:8002/bollinger"  # change if VPS
USERNAME = "OrivisAlpha"
PASSWORD = "Orivis"
REFRESH_INTERVAL_MS = 180000  # 3 minutes in milliseconds

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Orivis Alpha – Live Signals",
    layout="wide"
)

# ==========================================================
# LOGIN SYSTEM
# ==========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Orivis Alpha Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ==========================================================
# AUTO REFRESH (NON-BLOCKING)
# ==========================================================

st_autorefresh(interval=REFRESH_INTERVAL_MS, key="datarefresh")

# ==========================================================
# MAIN DASHBOARD
# ==========================================================

st.title("📊 Orivis Alpha – Live Bollinger Volatility")

# ==========================================================
# FETCH DATA
# ==========================================================

def fetch_data():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

data = fetch_data()

if data is None or "data" not in data:
    st.error("Failed to fetch data from API")
    st.stop()

# ==========================================================
# DISPLAY TIMESTAMPS
# ==========================================================

frontend_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
api_timestamp = data.get("timestamp", "N/A")

col1, col2 = st.columns(2)
col1.markdown(f"**API Last Updated:** {api_timestamp}")
col2.markdown(f"**Frontend Refreshed At:** {frontend_timestamp}")

st.markdown("---")

# ==========================================================
# PROCESS TABLE DATA
# ==========================================================

rows = []

for symbol, timeframes in data["data"].items():
    for tf, values in timeframes.items():
        rows.append({
            "Symbol": symbol.replace("m", ""),
            "Timeframe": tf,
            "Timestamp": values["LastClosedTime"],
            "Current Range": values["CurrentRange"],
            "Max Range": values["MaxRange"],
            "Min Range": values["MinRange"]
        })

df = pd.DataFrame(rows)

df = df.sort_values(by=["Symbol", "Timeframe"])

# ==========================================================
# DISPLAY TABLE
# ==========================================================

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
