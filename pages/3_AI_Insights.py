import streamlit as st
import pandas as pd
import os
import data_store as ds
import ui_components as ui

st.set_page_config(page_title="AI Insights - GreenOps", page_icon="🌱", layout="wide")
ds.init_session_state()
ui.load_css()

st.markdown("<h1>🤖 AI Insights & Advisory</h1>", unsafe_allow_html=True)

if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ **GROQ_API_KEY is not set.** Add it to your `.env` file and restart.")
    st.stop()

from ai_agents import GreenOpsAgents # Assumes you updated the class name as discussed

@st.cache_resource
def load_agents():
    return GreenOpsAgents()

# Instantiate it once globally
agents = load_agents()

cs = st.session_state.get("company_settings", {})
c_location = cs.get("location", "Not Specified")
c_industry = cs.get("industry", "Not Specified")
saved_markets = cs.get("export_markets", [])
c_exports = ", ".join(saved_markets) if saved_markets else "None"

# --- AI Temporal Filter ---
if len(st.session_state.emissions_data) > 0:
    df_ai = st.session_state.emissions_data.copy()
    df_ai['date'] = pd.to_datetime(df_ai['date'])
    
    st.markdown("### 📅 AI Analysis Timeframe")
    min_date = df_ai['date'].min().date()
    max_date = df_ai['date'].max().date()
    default_start = max_date - pd.Timedelta(days=365) if (max_date - min_date).days > 365 else min_date
    
    if "global_date_range" not in st.session_state:
        st.session_state.global_date_range = (default_start, max_date)
        
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        start_date = st.date_input("Start Date", value=st.session_state.global_date_range[0], min_value=min_date, max_value=max_date, key="ai_start")
    with col2:
        end_date = st.date_input("End Date", value=st.session_state.global_date_range[1], min_value=min_date, max_value=max_date, key="ai_end")
        
    if start_date > end_date:
        st.error("Invalid range: Start Date cannot be after End Date.")
        st.stop()
        
    # Synchronize state and apply filter
    st.session_state.global_date_range = (start_date, end_date)
    filtered_df = df_ai[(df_ai['date'].dt.date >= start_date) & (df_ai['date'].dt.date <= end_date)]
else:
    filtered_df = pd.DataFrame()

ai_tabs = st.tabs(["Data Assistant", "Report Summary", "Offset Advisor", "Regulation Radar", "Emission Optimizer"])

with ai_tabs[0]:
    st.markdown("### Data Entry Assistant")
    data_description = st.text_area("Describe emission activity", placeholder="E.g., We use diesel generators for backup power.")
    if st.button("Get Assistance", type="primary") and data_description:
        with st.spinner("Analysing..."):
            try:
                result = agents.run_data_entry_crew(data_description)
                with st.container(border=True):
                    st.markdown(result)
            except Exception as e: st.error(f"API Error: {e}")

with ai_tabs[1]:
    st.markdown("### Executive Report Generator")
    if filtered_df.empty: st.warning("No data in selected timeframe.")
    elif st.button("Generate Summary", type="primary"):
        with st.spinner("Generating..."):
            try:
                result = agents.run_report_summary_crew(ds.compress_data(filtered_df))
                with st.container(border=True):
                    st.markdown(result)
            except Exception as e: st.error(f"API Error: {e}")

with ai_tabs[2]:
    st.markdown("### Carbon Offset Advisor")
    if filtered_df.empty: st.warning("No data in selected timeframe.")
    else:
        total = filtered_df["emissions_kgCO2e"].sum()
        st.markdown(f"**To offset:** {total:,.2f} kgCO2e")
        if st.button("Get Recommendations", type="primary"):
            with st.spinner("Finding programs..."):
                try:
                    result = agents.run_offset_advice_crew(total, c_location, c_industry)
                    with st.container(border=True):
                        st.markdown(result)
                except Exception as e: st.error(f"API Error: {e}")

with ai_tabs[3]:
    st.markdown("### Regulation Radar")
    if st.button("Check Regulations", type="primary"):
        if c_exports != "None":
            with st.spinner("Analysing trade laws..."):
                try:
                    result = agents.run_regulation_check_crew(c_location, c_industry, c_exports)
                    with st.container(border=True):
                        st.markdown(result)
                except Exception as e: st.error(f"API Error: {e}")
        else:
            st.warning("Configure Export Markets in Settings first.")

with ai_tabs[4]:
    st.markdown("### Emission Optimizer")
    if filtered_df.empty: st.warning("No data in selected timeframe.")
    elif st.button("Generate Optimisation Strategy", type="primary"):
        with st.spinner("Analysing bottlenecks..."):
            try:
                result = agents.run_optimization_crew(ds.compress_data(filtered_df))
                with st.container(border=True):
                    st.markdown(result)
            except Exception as e: st.error(f"API Error: {e}")