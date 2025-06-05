import streamlit as st
import streamlit_authenticator as stauth
from supabase import Client as SupabaseClient
from app.db import supabase_client
import os
import logging
from httpx import HTTPStatusError
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_EMAILS = [e.strip() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()]
COOKIE_KEY = os.getenv("AUTHENTICATOR_COOKIE_KEY", "dev_key_change")

config = {
    "credentials": {"usernames": {}},
    "cookie": {"name": "amazon_multilogin_cookie", "key": COOKIE_KEY, "expiry_days": 30},
    "preauthorized": {"emails": []},
}

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

def supabase_login(email: str, password: str):
    from supabase import Client
    try:
        resp = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        if resp.user and resp.session:
            st.session_state.supabase_user = resp.user
            st.session_state.supabase_session = resp.session
            st.session_state.authentication_status = True
            st.session_state.name = resp.user.user_metadata.get("full_name", email)
            st.session_state.username = email
            return True, "Login successful"
        return False, "Invalid credentials"
    except HTTPStatusError as e:
        return False, f"Login error: {e}"

def supabase_signup(email: str, password: str):
    try:
        resp = supabase_client.auth.sign_up({"email": email, "password": password})
        if resp.user:
            return True, "Signup successful. Check your email for confirmation."
        return False, "Signup failed"
    except HTTPStatusError as e:
        return False, f"Signup error: {e}"

def supabase_logout():
    for k in ["supabase_user","supabase_session","authentication_status","name","username"]:
        st.session_state.pop(k, None)
    st.success("Logged out")
    st.rerun()

def display_login_form():
    st.title("Amazon Multilogin Manager")

    tab_login, tab_signup = st.tabs(["Login","Sign Up"])
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                ok, msg = supabase_login(email, password)
                (st.success if ok else st.error)(msg)
                if ok: st.experimental_rerun()

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="s_email")
            password = st.text_input("Password", type="password", key="s_pwd")
            if st.form_submit_button("Sign Up"):
                ok, msg = supabase_signup(email, password)
                (st.success if ok else st.error)(msg)
