import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="datasetapp", page_icon="💾", initial_sidebar_state="collapsed"
)

st.image("cat.gif")
st.markdown("# Dataset")
st.write(
    "This app This application lets you create datasets, update them, navigate through them and much more !"
)

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