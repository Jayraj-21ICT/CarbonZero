import streamlit as st
import pandas as pd
import utils
import emission_factors as ef  

utils.init_session_state()
utils.local_css()

st.markdown("<h1>Add New Sustainability Entry</h1>", unsafe_allow_html=True)

# Inherit context from Settings; no more local region overrides
cs = st.session_state.get("company_settings", {})
defaults = {
    "business_unit": cs.get("company_name", "Main Office"),
    "country": cs.get("location", "Not Specified"),
    "facility": cs.get("location", "HQ"),
    "responsible_person": cs.get("contact_person", "Admin"),
}

if defaults["country"] == "Not Specified":
    st.warning("⚠️ Warning: Your operating region is not set. Go to **Settings** to configure your enterprise profile so emission factors are regionally accurate.")

tabs = st.tabs(["⚡ Energy", "🗑️ Waste", "💨 Direct Carbon / Travel", "📂 CSV Upload"])

# Helper to fetch activities from the physics engine dynamically
def get_activities(category):
    return list(ef.EMISSION_FACTORS.get(category, {}).keys())

# ── Tab: Energy ──
with tabs[0]:
    st.markdown("### Log Energy Consumption")
    e_date = st.date_input("Date", key="e_date")
    
    e_type = st.radio("Energy Type", ["Purchased Electricity (Scope 2)", "Stationary Combustion / Generators (Scope 1)"])
    e_cat = "Electricity" if "Electricity" in e_type else "Stationary Combustion"
    
    if e_cat == "Electricity":
        # Pull grid from settings
        saved_grid = cs.get("grid_selection", "India Grid")
        
        # User still needs to select if they used Grid, Solar, or Wind today
        power_source = st.selectbox("Power Source", ["Grid Electricity", "Solar Power", "Wind Power"])
        
        if power_source == "Grid Electricity":
            if saved_grid == "Custom / Manual Entry":
                e_activity = cs.get("custom_grid_name", "Custom Grid")
                e_unit = "kWh"
                e_factor = cs.get("custom_grid_factor", 0.0)
            else:
                e_activity = saved_grid
                e_data = ef.get_emission_factor(e_cat, e_activity)
                e_unit = e_data["unit"] if e_data else "kWh"
                e_factor = e_data["factor"] if e_data else 0.0
        else:
            # Solar or Wind
            e_activity = power_source
            e_data = ef.get_emission_factor(e_cat, e_activity)
            e_unit = e_data["unit"] if e_data else "kWh"
            e_factor = e_data["factor"] if e_data else 0.0
            
    else:
        # Stationary Combustion (Diesel, Gas, etc.)
        e_activity = st.selectbox("Fuel Source", get_activities(e_cat))
        e_data = ef.get_emission_factor(e_cat, e_activity)
        e_unit = e_data["unit"] if e_data else "unit"
        e_factor = e_data["factor"] if e_data else 0.0

    e_qty = st.number_input(f"Quantity ({e_unit})", min_value=0.0, format="%.2f", key="e_qty")
    
    if e_cat == "Electricity" and power_source == "Grid Electricity" and saved_grid == "Custom / Manual Entry":
        st.info(f"**Custom Configured Factor:** {e_factor} kgCO2e / {e_unit}")
    else:
        st.info(f"**GHG Protocol Factor:** {e_factor} kgCO2e / {e_unit}")

    if st.button("Log Energy Data", type="primary"):
        if e_qty <= 0:
            st.error("❌ Quantity must be greater than 0. Ghost entries are not allowed.")
        else:
            if utils.add_emission_entry(e_date, defaults["business_unit"], "Energy Consumption", e_cat, e_activity, defaults["country"], defaults["facility"], defaults["responsible_person"], e_qty, e_unit, e_factor):
                st.success(f"✅ Logged {e_qty} {e_unit} of {e_activity}!")

# ── Tab: Waste ──
with tabs[1]:
    st.markdown("### Log Waste Management (Scope 3)")
    w_date = st.date_input("Date", key="w_date")
    
    w_cat = "Waste"
    w_activity = st.selectbox("Disposal Method & Material", get_activities(w_cat))
    
    w_data = ef.get_emission_factor(w_cat, w_activity)
    w_unit = w_data["unit"] if w_data else "kg"
    w_factor = w_data["factor"] if w_data else 0.0

    w_qty = st.number_input(f"Quantity ({w_unit})", min_value=0.0, format="%.2f", key="w_qty")
    st.info(f"**GHG Protocol Factor:** {w_factor} kgCO2e / {w_unit}")

    if st.button("Log Waste Data", type="primary"):
        if w_qty <= 0:
            st.error("❌ Quantity must be greater than 0. Ghost entries are not allowed.")
        else:
            if utils.add_emission_entry(w_date, defaults["business_unit"], "Waste Management", w_cat, w_activity, defaults["country"], defaults["facility"], defaults["responsible_person"], w_qty, w_unit, w_factor):
                st.success(f"Logged {w_qty} {w_unit} of {w_activity} waste!")

# ── Tab: Carbon & Travel ──
with tabs[2]:
    st.markdown("### Log Direct Emissions & Travel")
    c_date = st.date_input("Date", key="c_date")
    
    c_cat = st.selectbox("Emission Category", [
        "Mobile Combustion", 
        "Refrigerants", 
        "Business Travel", 
        "Employee Commuting",
        "Water",
        "Purchased Goods & Services"
    ])
    
    c_activity = st.selectbox("Specific Activity", get_activities(c_cat))
    
    c_data = ef.get_emission_factor(c_cat, c_activity)
    c_unit = c_data["unit"] if c_data else "unit"
    c_factor = c_data["factor"] if c_data else 0.0

    c_qty = st.number_input(f"Quantity ({c_unit})", min_value=0.0, format="%.2f", key="c_qty")
    st.info(f"**GHG Protocol Factor:** {c_factor} kgCO2e / {c_unit}")


    if st.button("Log Carbon Data", type="primary"):
        if c_qty <= 0:
            st.error("❌ Quantity must be greater than 0. Ghost entries are not allowed.")
        else:
            if utils.add_emission_entry(c_date, defaults["business_unit"], "Carbon Emissions", c_cat, c_activity, defaults["country"], defaults["facility"], defaults["responsible_person"], c_qty, c_unit, c_factor):
                st.success(f"Logged {c_qty} {c_unit} for {c_activity}!")

# ── Tab: CSV Upload ──
with tabs[3]:
    st.markdown("### Bulk Data Upload")
    st.warning("Ensure your CSV contains columns matching the exact names generated by the system. Required: `date, scope, category, activity, quantity, unit, emission_factor`")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file and st.button("Process CSV", type="primary"):
        with st.spinner("Hashing rows and verifying duplicates..."):
            utils.process_csv(uploaded_file)

# ── Data Viewer & Safe Delete ──
st.divider()
st.markdown("### Logged Database Entries")

if len(st.session_state.emissions_data) == 0:
    st.info("Database is empty. Add entries above.")
else:
    st.dataframe(st.session_state.emissions_data, use_container_width=True)

    st.markdown("#### Surgical Range Delete")
    max_idx = len(st.session_state.emissions_data) - 1
    col_del1, col_del2, _ = st.columns([1, 1, 2])
    with col_del1: start_idx = st.number_input("From Row", min_value=0, max_value=max_idx, value=0)
    with col_del2: end_idx = st.number_input("To Row", min_value=0, max_value=max_idx, value=0)

    rows_to_delete = list(range(int(start_idx), int(end_idx) + 1))
    confirm = st.checkbox(f"✅ I confirm I want to permanently delete **{len(rows_to_delete)} row(s)**. This cannot be undone.")

    if st.button("🗑️ Delete Selected Range", type="primary", use_container_width=True):
        if not confirm:
            st.warning("Tick the confirmation checkbox above to proceed.")
        elif start_idx > end_idx:
            st.error("'From Row' cannot be greater than 'To Row'.")
        else:
            st.session_state.emissions_data = st.session_state.emissions_data.drop(rows_to_delete, errors="ignore").reset_index(drop=True)
            utils.save_emissions_data()
            st.success(f"Deleted rows {start_idx} through {end_idx}.")
            st.rerun()