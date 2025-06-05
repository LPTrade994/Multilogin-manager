import streamlit as st
from datetime import datetime, date

def global_date_filter():
    st.sidebar.header("Filters")
    now = datetime.now()
    default_start = date(now.year, 1, 1)
    default_end = date(now.year, 12, 31)

    start = st.sidebar.date_input("Start Date", default_start, key="start_date_filter")
    end = st.sidebar.date_input("End Date", default_end, key="end_date_filter")

    if start > end:
        st.sidebar.error("Start date must be before end date.")
        return None, None
    return start, end
