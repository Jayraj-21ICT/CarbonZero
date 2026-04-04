import streamlit as st
import pandas as pd
import plotly.express as px
import utils

# Initialize state and apply CSS
utils.init_session_state()
utils.local_css()

st.markdown("<h1>Enterprise Analytics Dashboard</h1>", unsafe_allow_html=True)

if len(st.session_state.emissions_data) == 0:
    st.info("No data available. Proceed to Data Entry to initialize the database.")
    st.stop()

# Work on a copy
df = st.session_state.emissions_data.copy()
df['date'] = pd.to_datetime(df['date'])

# --- GLOBAL DATE FILTER (MAIN PAGE) ---
min_date = df['date'].min().date()
max_date = df['date'].max().date()

# Default to the last 365 days if there's enough data, otherwise show all
default_start = max_date - pd.Timedelta(days=365) if (max_date - min_date).days > 365 else min_date

st.markdown("### 📅 Temporal Filter")
filt_col1, filt_col2 = st.columns([1, 2])
with filt_col1:
    date_selection = st.date_input(
        "Select Date Range:", 
        value=(default_start, max_date),
        min_value=min_date, 
        max_value=max_date,
        help="This filters the charts below to a specific timeline."
    )
    
st.divider()

# Apply the filter logic
if len(date_selection) == 2:
    start_date, end_date = date_selection
    df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    
    if df.empty:
        st.warning("No data exists in this date range. Please expand your filter.")
        st.stop() # Halts rendering of empty charts
elif len(date_selection) == 1:
    st.info("Select the end date on the calendar to apply the filter.")
    st.stop()

# --- CORE MATH & FILTERING ---
total_impact = df['emissions_kgCO2e'].sum()

# Energy Math (using .copy() to prevent warnings)
energy_df = df[df['scope'] == 'Energy Consumption'].copy()
total_energy = energy_df['quantity'].sum()
renew_energy = energy_df[energy_df['category'] == 'Renewable (Clean)']['quantity'].sum()
renew_ratio = (renew_energy / total_energy * 100) if total_energy > 0 else 0

# Waste Math (using .copy() to prevent warnings)
waste_df = df[df['scope'] == 'Waste Management'].copy()
total_waste = waste_df['quantity'].sum()
recycled_waste = waste_df[waste_df['category'] == 'Recycled/Composted']['quantity'].sum()
recycle_ratio = (recycled_waste / total_waste * 100) if total_waste > 0 else 0

# --- HIGH-LEVEL INSIGHT ENGINE ---
st.markdown("### 🧠 Automated System Insights")
insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    # Insight 1: Predictive Run-Rate
    days_logged = (df['date'].max() - df['date'].min()).days
    if days_logged > 5: # Need a minimum baseline for projection
        daily_rate = total_impact / days_logged
        projected_annual = daily_rate * 365
        st.warning(f"**📈 Projected Annual Run-Rate:** Based on current velocity, your facility is on track to emit **{projected_annual:,.0f} kgCO2e** over 12 months.")
    else:
        st.info("**📈 Projected Annual Run-Rate:** Insufficient temporal data (need >5 days spread) to calculate yearly projection.")
        
with insight_col2:
    # Insight 2: Worst Offender Identification
    if total_impact > 0:
        worst_offender = df.groupby('activity')['emissions_kgCO2e'].sum().idxmax()
        worst_value = df.groupby('activity')['emissions_kgCO2e'].sum().max()
        st.error(f"**⚠️ Primary Carbon Bottleneck:** **{worst_offender}** is currently responsible for **{worst_value:,.0f} kgCO2e**, making it your highest priority for reduction.")

st.divider()

# --- EXPORT REPORT ---
# --- EXPORT REPORTS ---
st.markdown("### 📥 Compliance Exports")
exp_col1, exp_col2 = st.columns(2)

with exp_col1:
    # Raw Data CSV Download
    csv_export = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Download Raw Data (CSV)",
        data=csv_export,
        file_name=f"GreenOps_Data_{st.session_state.get('company_settings', {}).get('company_name', 'Enterprise')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with exp_col2:
    # Executive PDF Download
    if not df.empty:
        date_range_str = f"{df['date'].min().date()} to {df['date'].max().date()}"
        pdf_bytes = utils.generate_esg_pdf(df, st.session_state.get('company_settings', {}), date_range_str)
        st.download_button(
            label="📊 Download Executive Report (PDF)",
            data=pdf_bytes,
            file_name=f"GreenOps_Report_{st.session_state.get('company_settings', {}).get('company_name', 'Enterprise')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.button("📊 Download Executive Report (PDF)", disabled=True, use_container_width=True)

# --- THE 3-TAB ARCHITECTURE ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "⚡ Energy Deep-Dive", "🗑️ Waste & Logistics"])

# ==========================================
# TAB 1: EXECUTIVE SUMMARY
# ==========================================
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        utils.metric_card("Total Impact", f"{total_impact:,.0f}", "kgCO2e", "🌍")
    with col2:
        utils.metric_card("Renewable Ratio", f"{renew_ratio:.1f}", "% of Total Power", "🌱")
    with col3:
        utils.metric_card("Recycling Rate", f"{recycle_ratio:.1f}", "% of Total Waste", "♻️")
    with col4:
        utils.metric_card("Total Entries", str(len(df)), "Database Rows", "🗄️")
        
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Impact by Domain**")
        domain_data = df.groupby('scope')['emissions_kgCO2e'].sum().reset_index()
        if domain_data['emissions_kgCO2e'].sum() > 0:
            fig1 = px.pie(domain_data, values='emissions_kgCO2e', names='scope', hole=0.4,
                          color_discrete_sequence=['#2196F3', '#8D6E63', '#4CAF50'])
            fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Awaiting impactful data.")
            
    with col_chart2:
        st.markdown("**Temporal Trend (Month over Month)**")
        df['month'] = df['date'].dt.strftime('%Y-%m')
        trend_data = df.groupby('month')['emissions_kgCO2e'].sum().reset_index()
        if len(trend_data) > 0:
            fig2 = px.line(trend_data, x='month', y='emissions_kgCO2e', markers=True)
            fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), xaxis_title="", yaxis_title="kgCO2e")
            st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# TAB 2: ENERGY ANALYTICS
# ==========================================
with tab2:
    if energy_df.empty:
        st.info("No Energy data logged.")
    else:
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            st.markdown("**Carbon Footprint by Source (kgCO2e)**")
            e_emissions_data = energy_df.groupby('activity')['emissions_kgCO2e'].sum().reset_index()
            dirty_energy = e_emissions_data[e_emissions_data['emissions_kgCO2e'] > 0]
            
            if not dirty_energy.empty:
                fig3 = px.pie(dirty_energy, values='emissions_kgCO2e', names='activity', hole=0.4,
                              color_discrete_sequence=['#F44336', '#FF9800', '#8D6E63'])
                fig3.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.success("100% Clean Energy! No carbon footprint from power consumption.")
        with e_col2:
            st.markdown("**Energy Transition Trajectory (Ternary Plot)**")
            if 'date' in energy_df.columns and not energy_df.empty:
                t_df = energy_df.copy()
                t_df['month'] = pd.to_datetime(t_df['date']).dt.strftime('%Y-%m')
                
                def map_axis(activity):
                    if activity == 'Grid Electricity': return 'Grid (Traditional)'
                    elif activity == 'Diesel Generator': return 'Diesel (Off-Grid Fossil)'
                    else: return 'Clean (Solar/Wind)'
                    
                t_df['axis'] = t_df['activity'].apply(map_axis)
                pivot_df = t_df.groupby(['month', 'axis'])['quantity'].sum().unstack(fill_value=0).reset_index()
                
                for col in ['Grid (Traditional)', 'Diesel (Off-Grid Fossil)', 'Clean (Solar/Wind)']:
                    if col not in pivot_df.columns: pivot_df[col] = 0
                        
                pivot_df['Total'] = pivot_df['Grid (Traditional)'] + pivot_df['Diesel (Off-Grid Fossil)'] + pivot_df['Clean (Solar/Wind)']
                pivot_df = pivot_df[pivot_df['Total'] > 0] 
                
                if len(pivot_df) > 0:
                    pivot_df['Clean_%'] = (pivot_df['Clean (Solar/Wind)'] / pivot_df['Total']) * 100
                    pivot_df['Grid_%'] = (pivot_df['Grid (Traditional)'] / pivot_df['Total']) * 100
                    pivot_df['Diesel_%'] = (pivot_df['Diesel (Off-Grid Fossil)'] / pivot_df['Total']) * 100
                    pivot_df = pivot_df.sort_values('month')
                    
                    fig_ternary = px.scatter_ternary(
                        pivot_df, 
                        a="Clean_%", b="Grid_%", c="Diesel_%",
                        color="month", size="Total", hover_name="month", 
                        template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"
                    )
                    fig_ternary.update_layout(
                        margin=dict(t=30, b=30, l=10, r=10),
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig_ternary, use_container_width=True)
                else:
                    st.info("Insufficient data to plot trajectory.")
            else:
                st.info("Awaiting temporal data.")

# ==========================================
# TAB 3: WASTE & LOGISTICS
# ==========================================
with tab3:
    w_col1, w_col2 = st.columns(2)
    with w_col1:
        st.markdown("**Waste Lifecycle Analysis**")
        if not waste_df.empty:
            waste_df['material'] = waste_df['activity'].apply(lambda x: x.split(' (')[0])
            fig5 = px.bar(waste_df, x='material', y='quantity', color='category', 
                          title="Disposal Method by Material (kg)",
                          color_discrete_map={'Recycled/Composted': '#4CAF50', 'Landfill': '#8D6E63'})
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("No Waste data logged.")
            
    with w_col2:
        st.markdown("**Direct Carbon Footprint**")
        carbon_df = df[df['scope'] == 'Carbon Emissions']
        if not carbon_df.empty:
            fig6 = px.bar(carbon_df, x='activity', y='emissions_kgCO2e', color='activity')
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("No Direct Carbon data logged.")