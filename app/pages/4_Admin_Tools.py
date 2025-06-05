import streamlit as st, pandas as pd, asyncio
from io import BytesIO
from app.crud import regenerate_materialized_view, get_all_transactions, get_amazon_accounts, create_amazon_account
from app.schemas import AmazonAccountCreate
from app.db import get_db_session
from app.auth_utils import is_admin, get_current_user_id

async def page():
    st.title("🛠️ Admin Tools")
    if not get_current_user_id() or not is_admin():
        st.error("Admin only.")
        return

    async for ses in get_db_session():
        accs = await get_amazon_accounts(ses)
    st.subheader("Accounts")
    if accs:
        st.dataframe(pd.DataFrame([a.model_dump() for a in accs]), use_container_width=True)
    with st.expander("Add Account"):
        with st.form("new_acc"):
            name = st.text_input("Name")
            notes = st.text_area("Notes")
            if st.form_submit_button("Create"):
                async for ses in get_db_session():
                    await create_amazon_account(ses, AmazonAccountCreate(display_name=name, notes=notes))
                st.success("Account created")
                st.experimental_rerun()

    st.subheader("DB Operations")
    if st.button("Refresh Materialized View"):
        async for ses in get_db_session():
            await regenerate_materialized_view(ses)
        st.success("Refreshed!")

if __name__ == "__main__":
    asyncio.run(page())
