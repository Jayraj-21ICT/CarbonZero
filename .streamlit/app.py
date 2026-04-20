import streamlit as st
import pandas as pd

st.set_page_config(page_title="CarbonZero App")

st.title("🌱 CarbonZero Calculator")
st.subheader("Estimate your daily carbon footprint")

# Sidebar inputs
st.sidebar.header("Your Daily Activities")

transport_km = st.sidebar.slider("Travel (km/day)", 0, 100, 10)
electricity_kwh = st.sidebar.slider("Electricity usage (kWh/day)", 0, 50, 5)
meat_meals = st.sidebar.slider("Meat-based meals per day", 0, 5, 1)

# Emission factors (approx values)
CAR_EMISSION = 0.21       # kg CO2 per km
ELECTRICITY_EMISSION = 0.82  # kg CO2 per kWh
MEAT_EMISSION = 2.5       # kg CO2 per meal

# Calculation
transport_emission = transport_km * CAR_EMISSION
electricity_emission = electricity_kwh * ELECTRICITY_EMISSION
food_emission = meat_meals * MEAT_EMISSION

total_emission = transport_emission + electricity_emission + food_emission

# Display results
st.write("## 🌍 Your Carbon Footprint")
st.write(f"**Total CO₂ Emission:** {total_emission:.2f} kg/day")

# Breakdown chart
data = pd.DataFrame({
    "Category": ["Transport", "Electricity", "Food"],
    "CO2 Emission": [transport_emission, electricity_emission, food_emission]
})

st.bar_chart(data.set_index("Category"))

# Suggestions
st.write("## 💡 Suggestions to Reduce Emissions")

if total_emission > 20:
    st.warning("Your carbon footprint is high. Consider reducing travel or meat consumption.")
else:
    st.success("Good job! Your carbon footprint is relatively low.")
