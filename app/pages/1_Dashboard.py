import streamlit as st, pandas as pd, asyncio
from app.crud import get_account_summary_data_from_mv
from app.db import get_db_session
from decimal import Decimal

def highlight(val):
    if isinstance(val, (int,float,Decimal)):
        if val < 0:
            return "background-color:#FFB3B3"
        if val < 50:
            return "background-color:#FFFFCC"
    return ""

async def load_data(start, end):
    async for ses in get_db_session():
        return await get_account_summary_data_from_mv(ses, start, end)

async def page():
    st.title("📊 Dashboard")
    start = st.session_state.get("start_date_filter")
    end = st.session_state.get("end_date_filter")
    if not start or not end:
        st.info("Set date filter in sidebar.")
        return
    rows = await load_data(start,end)
    if not rows:
        st.info("No data.")
        return
    df = pd.DataFrame([r.model_dump() for r in rows])
    countries = ["IT","DE","FR","ES","JP","US"]
    st.dataframe(
        df.style.applymap(highlight, subset=countries+["total_balance_all_countries"]),
        use_container_width=True,
    )

if __name__ == "__main__":
    asyncio.run(page())
