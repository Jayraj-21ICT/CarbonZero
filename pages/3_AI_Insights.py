import streamlit as st
import pandas as pd
import os
import utils

utils.init_session_state()
utils.local_css()

st.markdown("<h1>🤖 AI Insights & Advisory</h1>", unsafe_allow_html=True)

if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ **GROQ_API_KEY is not set.** Add it to your `.env` file and restart.")
    st.stop()

from ai_agents import GreenOpsAgents # Assumes you updated the class name as discussed

if "ai_agents" not in st.session_state:
    st.session_state.ai_agents = GreenOpsAgents()

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
    min_date, max_date = df_ai['date'].min().date(), df_ai['date'].max().date()
    default_start = max_date - pd.Timedelta(days=365) if (max_date - min_date).days > 365 else min_date
    
    col1, _ = st.columns([1, 2])
    with col1:
        date_selection = st.date_input("Date Range for AI:", value=(default_start, max_date), min_value=min_date, max_value=max_date)
        
    if len(date_selection) == 2:
        filtered_df = df_ai[(df_ai['date'].dt.date >= date_selection[0]) & (df_ai['date'].dt.date <= date_selection[1])]
    else:
        filtered_df = pd.DataFrame()
else:
    filtered_df = pd.DataFrame()

ai_tabs = st.tabs(["Data Assistant", "Report Summary", "Offset Advisor", "Regulation Radar", "Emission Optimizer"])

with ai_tabs[0]:
    st.markdown("### Data Entry Assistant")
    data_description = st.text_area("Describe emission activity", placeholder="E.g., We use diesel generators for backup power.")
    if st.button("Get Assistance", type="primary") and data_description:
        with st.spinner("Analysing..."):
            try:
                result = st.session_state.ai_agents.run_data_entry_crew(data_description)
                st.markdown(f"<div class='stCard'>{result}</div>", unsafe_allow_html=True)
            except Exception as e: st.error(f"API Error: {e}")

with ai_tabs[1]:
    st.markdown("### Executive Report Generator")
    if filtered_df.empty: st.warning("No data in selected timeframe.")
    elif st.button("Generate Summary", type="primary"):
        with st.spinner("Generating..."):
            try:
                result = st.session_state.ai_agents.run_report_summary_crew(utils.compress_data(filtered_df))
                st.markdown(f"<div class='stCard'>{result}</div>", unsafe_allow_html=True)
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
                    result = st.session_state.ai_agents.run_offset_advice_crew(total, c_location, c_industry)
                    st.markdown(f"<div class='stCard'>{result}</div>", unsafe_allow_html=True)
                except Exception as e: st.error(f"API Error: {e}")

with ai_tabs[3]:
    st.markdown("### Regulation Radar")
    if st.button("Check Regulations", type="primary"):
        if c_exports != "None":
            with st.spinner("Analysing trade laws..."):
                try:
                    result = st.session_state.ai_agents.run_regulation_check_crew(c_location, c_industry, c_exports)
                    st.markdown(f"<div class='stCard'>{result}</div>", unsafe_allow_html=True)
                except Exception as e: st.error(f"API Error: {e}")
        else:
            st.warning("Configure Export Markets in Settings first.")

with ai_tabs[4]:
    st.markdown("### Emission Optimizer")
    if filtered_df.empty: st.warning("No data in selected timeframe.")
    elif st.button("Generate Optimisation Strategy", type="primary"):
        with st.spinner("Analysing bottlenecks..."):
            try:
                result = st.session_state.ai_agents.run_optimization_crew(utils.compress_data(filtered_df))
                st.markdown(f"<div class='stCard'>{result}</div>", unsafe_allow_html=True)
            except Exception as e: st.error(f"API Error: {e}")