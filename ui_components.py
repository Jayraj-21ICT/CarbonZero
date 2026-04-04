import streamlit as st

def load_css():
    with open("static/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True) # Safe here: reading static local file

def metric_card(title, value, description=None, icon=None, prefix="", suffix=""):
    st.markdown(f"""
    <div class="metric-card">
        {f'<div style="font-size:24px">{icon}</div>' if icon else ''}
        <div class="metric-label">{title}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {f'<div style="color:#aaa;font-size:12px">{description}</div>' if description else ''}
    </div>
    """, unsafe_allow_html=True)