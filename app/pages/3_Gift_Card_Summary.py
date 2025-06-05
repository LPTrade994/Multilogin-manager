import streamlit as st, pandas as pd, asyncio
from app.crud import get_giftcard_summary
from app.db import get_db_session
from app.auth_utils import get_current_user_id

async def fetch(start,end,country):
    async for ses in get_db_session():
        return await get_giftcard_summary(ses,start,end,country)

async def page():
    st.title("🎁 Gift Card Summary")
    if not get_current_user_id():
        st.warning("Login required.")
        return
    start = st.session_state.get("start_date_filter")
    end = st.session_state.get("end_date_filter")
    if not start or not end:
        st.info("Set date filter in sidebar.")
        return
    country = st.selectbox("Country", ["ALL","IT","DE","FR","ES","JP","US"])
    data = await fetch(start,end,country)
    if not data:
        st.info("No data.")
        return
    df = pd.DataFrame([d.model_dump() for d in data])
    st.bar_chart(df.set_index("country")["total_value"])
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    asyncio.run(page())
