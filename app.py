import streamlit as st
import pandas as pd
import numpy as np

st.markdown(
    """
    <style>
    body {
        background-image: url("https://www.numerama.com/wp-content/uploads/2016/09/grumpycat.jpg");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(
    page_title="datasetapp", page_icon="💾", initial_sidebar_state="collapsed"
)
st.markdown("# Dataset")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/create.py", label="CREATE", icon="1️⃣")

with col2:
    st.page_link("pages/update.py", label="UPDATE", icon="2️⃣")

with col3:
    st.page_link("pages/view.py", label="VIEW", icon="3️⃣")
    
st.markdown("---")
st.markdown(
    "More infos at [github.com/Unicron03/datasetApp](https://github.com/Unicron03/datasetApp)"
)