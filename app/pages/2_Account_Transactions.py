import streamlit as st, pandas as pd, asyncio
from app import crud, schemas, models
from app.db import get_db_session
from app.auth_utils import get_current_user_id
from datetime import date
async def load_accounts():
    async for ses in get_db_session():
        return await crud.get_amazon_accounts(ses)

async def load_transactions(acc_id,start,end,skip,limit):
    async for ses in get_db_session():
        return await crud.get_transactions_for_account(ses,acc_id,start,end,skip,limit)

async def page():
    st.title("💼 Account Transactions")
    uid = get_current_user_id()
    if not uid:
        st.warning("Login required.")
        return
    accounts = await load_accounts()
    if not accounts:
        st.info("No accounts found.")
        return
    acc_map = {a.id:a.display_name for a in accounts}
    acc_id = st.selectbox("Account", acc_map.keys(), format_func=lambda x: acc_map[x])
    st.markdown("---")
    with st.form("add_tx"):
        country = st.selectbox("Country", ["IT","DE","FR","ES","JP","US"])
        ttype = st.radio("Type", [t.value for t in models.TransactionType])
        value = st.number_input("Value €", min_value=0.0, step=0.01)
        tdate = st.date_input("Date", value=date.today())
        code = st.text_input("Code/Ref")
        if st.form_submit_button("Add"):
            tx = schemas.TransactionCreate(
                account_id=acc_id,
                user_id=uid,
                trans_date=tdate,
                trans_type=models.TransactionType(ttype),
                code=code,
                country=country,
                value=value,
            )
            async for ses in get_db_session():
                await crud.add_transaction(ses, tx)
            st.success("Transaction added")
            st.experimental_rerun()
    st.markdown("---")
    start = st.session_state.get("start_date_filter")
    end = st.session_state.get("end_date_filter")
    txs = await load_transactions(acc_id,start,end,0,100)
    if txs:
        df = pd.DataFrame([t.model_dump(exclude={'account'}) for t in txs])
        st.dataframe(df,use_container_width=True)
    else:
        st.info("No transactions.")

if __name__ == "__main__":
    asyncio.run(page())
