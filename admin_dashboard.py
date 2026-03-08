import streamlit as st
import sqlite3
import pandas as pd
import time

# --- CONFIGURATION ---
ADMIN_PASSWORD = "admin"
DB_PATH = 'leads.db'

st.set_page_config(page_title="LQ Admin Dashboard", layout="wide")


def main():
    st.title("🔐 LQ Lead Generation Admin")

    # Simple Session State for Login
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Login Screen
    if not st.session_state.authenticated:
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Password")
        return

    # --- DASHBOARD (Only visible after login) ---
    with st.sidebar:
        st.header("Controls")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # Header with Refresh Button
    col_header, col_btn = st.columns([6, 1])
    with col_header:
        st.subheader("📋 Captured Leads")
    with col_btn:
        if st.button("🔄 Refresh"):
            st.rerun()

    # 1. Load Data
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM leads ORDER BY Timestamp DESC", conn)
        conn.close()
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return

    # 2. Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", len(df))
    col2.metric("Top Course", df['Course_Name'].mode()[0] if not df.empty else "N/A")
    col3.metric("Latest Lead", df['Timestamp'].iloc[0] if not df.empty else "N/A")

    # 3. Data Table
    st.dataframe(df, use_container_width=True)

    # 4. CSV Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Leads CSV",
        data=csv,
        file_name='learnquest_leads.csv',
        mime='text/csv',
    )


if __name__ == "__main__":
    main()

