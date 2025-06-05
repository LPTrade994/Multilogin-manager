import streamlit as st
import asyncio
from app.auth_utils import display_login_form, supabase_logout, is_admin
from app.ui_components import global_date_filter

st.set_page_config(page_title="Amazon Multilogin Manager", layout="wide")

async def main():
    if not st.session_state.get("authentication_status"):
        display_login_form()
        return

    st.sidebar.title(f"Welcome, {st.session_state.get('name','User')}")

    if st.sidebar.button("Logout"):
        supabase_logout()

    start, end = global_date_filter()
    if start is None:
        return
    st.session_state.start_date_filter = start
    st.session_state.end_date_filter = end

    st.sidebar.info(f"Admin: {'Yes' if is_admin() else 'No'}")

    st.subheader("Benvenuto!")
    st.write("Usa il menu di sinistra per navigare tra le pagine dell'app.")

if __name__ == "__main__":
    asyncio.run(main())
