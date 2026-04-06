import os
import pandas as pd
import json
import streamlit as st
import hashlib
import uuid

# --- State Management & Setup ---
def init_session_state():
    os.makedirs("data", exist_ok=True)
    _EMPTY_COLS = ["date", "scope", "category", "activity", "quantity", "unit", "emission_factor", "emissions_kgCO2e"]

    if "emissions_data" not in st.session_state:
        if os.path.exists("data/emissions.json"):
            try:
                with open("data/emissions.json", "r") as fh:
                    raw = fh.read().strip()
                if raw:
                    loaded_df = pd.DataFrame(json.loads(raw))
                    if "date" in loaded_df.columns:
                        loaded_df["date"] = pd.to_datetime(loaded_df["date"], errors="coerce")

                    # BACKFILL UUIDs for older data that doesn't have them
                    if "id" not in loaded_df.columns:
                        loaded_df.insert(0, "id", [str(uuid.uuid4()) for _ in range(len(loaded_df))])
                    st.session_state.emissions_data = loaded_df
            except Exception as exc:
                st.error(f"Error loading emissions data: {exc}")
                st.session_state.emissions_data = pd.DataFrame(columns=_EMPTY_COLS)
        else:
            st.session_state.emissions_data = pd.DataFrame(columns=_EMPTY_COLS)

    if "company_settings" not in st.session_state:
        try:
            with open("data/settings.json", "r") as fh:
                st.session_state.company_settings = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            st.session_state.company_settings = {
                "company_name": "", "industry": "", "location": "",
                "contact_person": "", "email": "", "phone": "", "export_markets": []
            }

# --- Data Operations ---
def save_emissions_data() -> bool:
    try:
        temp_df = st.session_state.emissions_data.copy()
        if "date" in temp_df.columns:
            temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m-%d")
        with open("data/emissions.json", "w") as fh:
            json.dump(temp_df.to_dict("records") if len(temp_df) > 0 else [], fh, indent=2)
        return True
    except Exception as exc:
        st.error(f"Error saving data: {exc}")
        return False

def add_emission_entry(date, business_unit, scope, category, activity, country, facility, responsible_person, quantity, unit, emission_factor) -> bool:
    try:
        emissions_kgCO2e = float(quantity) * float(emission_factor)
        new_entry = pd.DataFrame([{
            "id": str(uuid.uuid4()), # Generate unique ID
            "date": pd.to_datetime(date), "business_unit": business_unit, "scope": scope,
            "category": category, "activity": activity, "country": country,
            "facility": facility, "responsible_person": responsible_person,
            "quantity": float(quantity), "unit": unit, "emission_factor": float(emission_factor),
            "emissions_kgCO2e": emissions_kgCO2e,
        }])
        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, new_entry], ignore_index=True)
        return save_emissions_data()
    except Exception as exc:
        st.error(f"Error adding entry: {exc}")
        return False

def _row_hash(row):
    key = f"{row.get('date', '')}|{row.get('scope', '')}|{row.get('category', '')}|{row.get('activity', '')}|{row.get('quantity', '')}|{row.get('unit', '')}|{row.get('emission_factor', '')}"
    return hashlib.md5(key.encode()).hexdigest()

def process_csv(uploaded_file) -> bool:
    try:
        df = pd.read_csv(uploaded_file)
        
        # 1. FAIL-FAST COLUMN CHECK
        required_cols = ["date", "quantity", "emission_factor"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"Upload failed: CSV is missing required columns {required_cols}.")
            return False

        # 2. SAFE CASTING, STRICT MATH & HASH STANDARDIZATION
        # coerce turns bad text into NaN, fillna(0.0) prevents math errors, round(4) fixes the MD5 bug
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0).round(4)
        df["emission_factor"] = pd.to_numeric(df["emission_factor"], errors="coerce").fillna(0.0).round(4)
        df["emissions_kgCO2e"] = (df["quantity"] * df["emission_factor"]).round(4)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
            
        # 3. SANITIZE TEXT INPUTS (Kill XSS payloads)
        text_cols = ["business_unit", "scope", "category", "activity", "country", "facility", "responsible_person", "unit"]
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'[<>]', '', regex=True)

        # 4. INJECT BATCH UUIDs
        if "id" not in df.columns:
            df.insert(0, "id", [str(uuid.uuid4()) for _ in range(len(df))])

        # 5. DUPLICATE CHECK
        if len(st.session_state.emissions_data) > 0:
            # The hashing here is now mathematically stable due to the round(4) applied above
            existing_hashes = set(st.session_state.emissions_data.apply(_row_hash, axis=1))
            incoming_hashes = df.apply(_row_hash, axis=1)
            is_duplicate = incoming_hashes.isin(existing_hashes)
            dup_count = int(is_duplicate.sum())
            if dup_count > 0:
                st.warning(f"⚠️ {dup_count} duplicate row(s) skipped.")
                df = df[~is_duplicate].copy()
            if df.empty: return False

        cs = st.session_state.get("company_settings", {})
        context_defaults = {"business_unit": cs.get("company_name", "Corporate"), "country": cs.get("location", "India"), "facility": cs.get("location", "HQ"), "responsible_person": cs.get("contact_person", "Admin")}
        for field, default in context_defaults.items():
            if field not in df.columns: df[field] = default

        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, df], ignore_index=True)
        if save_emissions_data():
            st.success(f"✅ {len(df)} new row(s) added successfully.")
            return True
        return False
    except Exception as exc: 
        st.error(f"Error processing CSV: {exc}")
        return False

def compress_data(df: pd.DataFrame) -> str:
    if df.empty: return "No data available."
    total_impact = df["emissions_kgCO2e"].sum()
    scope_summary = df.groupby("scope")["emissions_kgCO2e"].sum().to_dict()
    top_offenders = df.groupby("activity")["emissions_kgCO2e"].sum().nlargest(3).to_dict()
    return f"Total Footprint: {total_impact:.2f} kgCO2e\nBreakdown by Scope: {scope_summary}\nTop 3 Carbon Offenders: {top_offenders}"
