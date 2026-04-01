import streamlit as st
import pandas as pd
import os
import json
import shutil
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Set page config for wide layout
st.set_page_config(page_title="GreenOps", page_icon="🌱", layout="wide")

# Initialize session state variables if they don't exist
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'emissions_data' not in st.session_state:
    # Load data if exists, otherwise create empty dataframe
    if os.path.exists('data/emissions.json'):
        try:
            with open('data/emissions.json', 'r') as f:
                data = f.read().strip()
                if data:  # Check if file is not empty
                    try:
                        st.session_state.emissions_data = pd.DataFrame(json.loads(data))
                    except json.JSONDecodeError:
                        # Create a backup of the corrupted file
                        backup_file = f'data/emissions_backup_{int(time.time())}.json'
                        shutil.copy('data/emissions.json', backup_file)
                        st.warning(f"Corrupted emissions data file found. A backup has been created at {backup_file}")
                        # Create empty dataframe
                        st.session_state.emissions_data = pd.DataFrame(columns=[
                            'date', 'scope', 'category', 'activity', 'quantity', 
                            'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
                        ])
                else:
                    # Empty file, create new DataFrame
                    st.session_state.emissions_data = pd.DataFrame(columns=[
                        'date', 'scope', 'category', 'activity', 'quantity', 
                        'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
                    ])
        except Exception as e:
            st.error(f"Error loading emissions data: {str(e)}")
            # Create empty dataframe if loading fails
            st.session_state.emissions_data = pd.DataFrame(columns=[
                'date', 'scope', 'category', 'activity', 'quantity', 
                'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
            ])
            # Make sure data directory exists
            os.makedirs('data', exist_ok=True)
    else:
        st.session_state.emissions_data = pd.DataFrame(columns=[
            'date', 'scope', 'category', 'activity', 'quantity', 
            'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
        ])
        # Make sure data directory exists
        os.makedirs('data', exist_ok=True)
if 'active_page' not in st.session_state:
    st.session_state.active_page = "AI Insights"

# Translation dictionary
translations = {
    'English': {
        'title': 'YourCarbonFootprint',
        'subtitle': 'Carbon Accounting & Reporting Tool for SMEs',
        'dashboard': 'Dashboard',
        'data_entry': 'Data Entry',
        'reports': 'Reports',
        'settings': 'Settings',
        'about': 'About',
        'scope1': 'Scope 1 (Direct Emissions)',
        'scope2': 'Scope 2 (Indirect Emissions - Purchased Energy)',
        'scope3': 'Scope 3 (Other Indirect Emissions)',
        'date': 'Date',
        'scope': 'Scope',
        'category': 'Category',
        'activity': 'Activity',
        'quantity': 'Quantity',
        'unit': 'Unit',
        'emission_factor': 'Emission Factor',
        'emissions': 'Emissions (kgCO2e)',
        'notes': 'Notes',
        'add_entry': 'Add Entry',
        'upload_csv': 'Upload CSV',
        'download_report': 'Download Report',
        'total_emissions': 'Total Emissions',
        'emissions_by_scope': 'Emissions by Scope',
        'emissions_by_category': 'Emissions by Category',
        'emissions_over_time': 'Emissions Over Time',
        'language': 'Language',
        'save': 'Save',
        'cancel': 'Cancel',
        'success': 'Success!',
        'error': 'Error!',
        'entry_added': 'Entry added successfully!',
        'csv_uploaded': 'CSV uploaded successfully!',
        'report_downloaded': 'Report downloaded successfully!',
        'settings_saved': 'Settings saved successfully!',
        'no_data': 'No data available.',
        'welcome_message': 'Welcome to YourCarbonFootprint! Start by adding your emissions data or uploading a CSV file.',
        'custom_category': 'Custom Category',
        'custom_activity': 'Custom Activity',
        'custom_unit': 'Custom Unit',
        'entry_failed': 'Failed to add entry.'
    },
    'Hindi': {
        'title': 'आपका कार्बन फुटप्रिंट',
        'subtitle': 'एसएमई के लिए कार्बन अकाउंटिंग और रिपोर्टिंग टूल',
        'dashboard': 'डैशबोर्ड',
        'data_entry': 'डेटा प्रविष्टि',
        'reports': 'रिपोर्ट',
        'settings': 'सेटिंग्स',
        'about': 'के बारे में',
        'scope1': 'स्कोप 1 (प्रत्यक्ष उत्सर्जन)',
        'scope2': 'स्कोप 2 (अप्रत्यक्ष उत्सर्जन - खरीदी गई ऊर्जा)',
        'scope3': 'स्कोप 3 (अन्य अप्रत्यक्ष उत्सर्जन)',
        'date': 'तारीख',
        'scope': 'स्कोप',
        'category': 'श्रेणी',
        'activity': 'गतिविधि',
        'quantity': 'मात्रा',
        'unit': 'इकाई',
        'emission_factor': 'उत्सर्जन कारक',
        'emissions': 'उत्सर्जन (kgCO2e)',
        'notes': 'नोट्स',
        'add_entry': 'प्रविष्टि जोड़ें',
        'upload_csv': 'CSV अपलोड करें',
        'download_report': 'रिपोर्ट डाउनलोड करें',
        'total_emissions': 'कुल उत्सर्जन',
        'emissions_by_scope': 'स्कोप द्वारा उत्सर्जन',
        'emissions_by_category': 'श्रेणी द्वारा उत्सर्जन',
        'emissions_over_time': 'समय के साथ उत्सर्जन',
        'language': 'भाषा',
        'save': 'सहेजें',
        'cancel': 'रद्द करें',
        'success': 'सफलता!',
        'error': 'त्रुटि!',
        'entry_added': 'प्रविष्टि सफलतापूर्वक जोड़ी गई!',
        'csv_uploaded': 'CSV सफलतापूर्वक अपलोड की गई!',
        'report_downloaded': 'रिपोर्ट सफलतापूर्वक डाउनलोड की गई!',
        'settings_saved': 'सेटिंग्स सफलतापूर्वक सहेजी गईं!',
        'no_data': 'कोई डेटा उपलब्ध नहीं है।',
        'welcome_message': 'आपका कार्बन फुटप्रिंट में आपका स्वागत है! अपना उत्सर्जन डेटा जोड़कर या CSV फ़ाइल अपलोड करके प्रारंभ करें।',
        'custom_category': 'कस्टम श्रेणी',
        'custom_activity': 'कस्टम गतिविधि',
        'custom_unit': 'कस्टम इकाई',
        'entry_failed': 'प्रविष्टि जोड़ने में विफल रहा।'
    }
}

# Function to get translated text
def t(key):
    lang = st.session_state.language
    return translations.get(lang, {}).get(key, key)

# Function to save emissions data
def save_emissions_data():
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Create a backup of the existing file if it exists
        if os.path.exists('data/emissions.json'):
            backup_path = 'data/emissions_backup.json'
            try:
                with open('data/emissions.json', 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            except Exception:
                # Continue even if backup fails
                pass
        
        # Save data to JSON file with proper formatting
        with open('data/emissions.json', 'w') as f:
            if len(st.session_state.emissions_data) > 0:
                json.dump(st.session_state.emissions_data.to_dict(orient='records'), f, indent=2)
            else:
                # Write empty array if no data
                f.write('[]')               
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

# Function to add new emission entry
def add_emission_entry(date, business_unit, project, scope, category, activity, country, facility, responsible_person, quantity, unit, emission_factor, data_quality, verification_status, notes):
    """Add a new emission entry to the emissions data."""
    try:
        # Calculate emissions
        emissions_kgCO2e = float(quantity) * float(emission_factor)
        
        # Create new entry
        new_entry = pd.DataFrame([{
            'date': date.strftime('%Y-%m-%d'),
            'business_unit': business_unit,
            'project': project,
            'scope': scope,
            'category': category,
            'activity': activity,
            'country': country,
            'facility': facility,
            'responsible_person': responsible_person,
            'quantity': float(quantity),
            'unit': unit,
            'emission_factor': float(emission_factor),
            'emissions_kgCO2e': emissions_kgCO2e,
            'data_quality': data_quality,
            'verification_status': verification_status,
            'notes': notes
        }])
        
        # Add to existing data
        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, new_entry], ignore_index=True)
        
        # Save data and return success/failure
        return save_emissions_data()
    except Exception as e:
        st.error(f"Error adding entry: {str(e)}")
        return False

def delete_emission_entry(index):
    try:
        # Make a copy of the current data
        if len(st.session_state.emissions_data) > index:
            # Drop the row at the specified index
            st.session_state.emissions_data = st.session_state.emissions_data.drop(index).reset_index(drop=True)
            
            # Save data and return success/failure
            return save_emissions_data()
        else:
            st.error(f"Index {index} is invalid for deletion, No deletion performed.")
            return False
    except Exception as e:
        st.error(f"Error deleting entry: {str(e)}")
        return False

# Function to process uploaded CSV
def process_csv(uploaded_file):
    """Process uploaded CSV file and add to emissions data."""
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        required_columns = ['date', 'scope', 'category', 'activity', 'quantity', 'unit', 'emission_factor']
        
        # Check if all required columns exist
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV must contain all required columns: {', '.join(required_columns)}")
            return False
        
        # Validate data types
        try:
            # Convert quantity and emission_factor to float
            df['quantity'] = df['quantity'].astype(float)
            df['emission_factor'] = df['emission_factor'].astype(float)
            
            # Validate dates
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        except Exception as e:
            st.error(f"Data validation error: {str(e)}")
            return False
        
        # Calculate emissions if not provided
        if 'emissions_kgCO2e' not in df.columns:
            df['emissions_kgCO2e'] = df['quantity'] * df['emission_factor']
        
        # Add enterprise fields if not present
        enterprise_fields = {
            'business_unit': 'Corporate',
            'project': 'Not Applicable',
            'country': 'India',
            'facility': '',
            'responsible_person': '',
            'data_quality': 'Medium',
            'verification_status': 'Unverified',
            'notes': ''
        }
        
        # Add missing columns with default values
        for field, default_value in enterprise_fields.items():
            if field not in df.columns:
                df[field] = default_value
        
        # Append to existing data
        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, df], ignore_index=True)
        
        # Save data
        if save_emissions_data():
            st.success(f"Successfully added {len(df)} entries")
            return True
        else:
            st.error("Failed to save data")
            return False
    except Exception as e:
        st.error(f"Error processing CSV: {str(e)}")
        return False

# Function to generate PDF report
def generate_report():
    # Create a BytesIO object
    buffer = BytesIO()
    
    # Create a simple CSV report for now
    st.session_state.emissions_data.to_csv(buffer, index=False)
    buffer.seek(0)
    
    return buffer

# Custom CSS
def local_css():
    st.markdown('''
    <style>
    /* Remove default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Base styling */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar styling - IMPORTANT: Override the dark background */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #ffffff !important;
        padding: 2rem 1rem;
    }
    
    /* Sidebar title */
    [data-testid="stSidebar"] h1 {
        color: #2E7D32;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 0;
    }
    
    /* Sidebar subtitle */
    [data-testid="stSidebar"] p {
        color: #555555;
        font-size: 14px;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #2E7D32;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.2rem;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }
    
    /* Card styling */
    div.stCard {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin-bottom: 1.5rem;
        border: none;
    }
    
    /* Card styling */
    .stCard {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border: 1px solid #f0f0f0;
    }
    
    /* AI Insights card styling */
    .stCard p {
        margin-bottom: 10px;
        line-height: 1.6;
    }
    
    .stCard h1, .stCard h2, .stCard h3, .stCard h4 {
        color: #2E7D32;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    .stCard ul, .stCard ol {
        margin-left: 20px;
        margin-bottom: 15px;
    }
    
    .stCard table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 15px;
    }
    
    .stCard th, .stCard td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    .stCard th {
        background-color: #f2f2f2;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border-left: 4px solid #2E7D32;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 0.5rem 0;
        color: #2E7D32;
    }
    
    .metric-label {
        font-size: 14px;
        color: #555555;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #388E3C;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton>button:focus {
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.5);
    }
    
    /* Secondary buttons */
    .stButton>button[kind="secondary"] {
        background-color: #f8f9fa;
        color: #2E7D32;
        border: 1px solid #2E7D32;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background-color: #f1f3f5;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32 !important;
        color: white !important;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #FFF8E1;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #555555;
        font-size: 12px;
        margin-top: 2rem;
        border-top: 1px solid #e9ecef;
    }
    
    /* Form fields */
    [data-baseweb="input"] {
        border-radius: 4px;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        border-radius: 4px;
    }
    
    /* Sidebar navigation buttons */
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        text-align: left;
        background-color: transparent;
        color: #333333;
        border: none;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        font-weight: normal;
        display: flex;
        align-items: center;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #f1f3f5;
        box-shadow: none;
    }
    
    /* Active navigation button */
    [data-testid="stSidebar"] .stButton>button.active {
        background-color: #E8F5E9;
        border-left: 4px solid #2E7D32;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: 0;
        border-top: 1px solid #e9ecef;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        border: 1px solid #e9ecef;
    }
    
    .dataframe th {
        background-color: #f8f9fa;
        color: #333333;
        font-weight: 500;
        text-align: left;
        padding: 0.75rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .dataframe td {
        padding: 0.75rem;
        border-bottom: 1px solid #e9ecef;
    }
    
    .dataframe tr:hover {
        background-color: #f8f9fa;
    }
    </style>
    ''', unsafe_allow_html=True)

# Navigation component
def render_navigation():
    nav_items = [
        {"icon": "🤖", "label": "AI Insights", "id": "AI Insights"},
        {"icon": "📝", "label": "Data Entry", "id": "Data Entry"},
        {"icon": "📊", "label": "Dashboard", "id": "Dashboard"},
        {"icon": "⚙️", "label": "Settings", "id": "Settings"}
    ]
    
    st.markdown("### Navigation")
    
    for item in nav_items:
        active_class = "active" if st.session_state.active_page == item["id"] else ""
        if st.sidebar.button(
            f"{item['icon']} {item['label']}", 
            key=f"nav_{item['id']}",
            help=f"Go to {item['label']}",
            use_container_width=True
        ):
            st.session_state.active_page = item["id"]
            st.rerun()

# Metric card component
def metric_card(title, value, description=None, icon=None, prefix="", suffix=""):
    st.markdown(f'''
    <div class="metric-card">
        {f'<div style="font-size: 24px;">{icon}</div>' if icon else ''}
        <div class="metric-label">{title}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {f'<div style="color: #aaa; font-size: 12px;">{description}</div>' if description else ''}
    </div>
    ''', unsafe_allow_html=True)

# Card component
def card(content, title=None):
    if title:
        st.markdown(f"<div class='stCard'><h3>{title}</h3>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='stCard'>{content}</div>", unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Sidebar
with st.sidebar:
    st.markdown(f"<h1 style='margin-bottom: 0; font-size: 24px;'>{t('title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-top: 0; color: #aaa; font-size: 12px;'>{t('subtitle')}</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Language selector
    language = st.selectbox(t('language'), ['English', 'Hindi'], key='language')
    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()
    
    st.divider()
    
    # Navigation
    render_navigation()
    
    st.divider()
    
    # Footer
    st.markdown(
        "<div class='footer' style='color: #555555;'> 2025 YourCarbonFootprint<br>Product Owner: Sonu Kumar<br>sonu@aianytime.net</div>",
        unsafe_allow_html=True
    )

# Main content
if st.session_state.active_page == "Dashboard":
    st.markdown(f"<h1> {t('dashboard')}</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.emissions_data) == 0:
        st.markdown(f"<div class='info-box'>{t('welcome_message')}</div>", unsafe_allow_html=True)
    else:
        # Calculate metrics
        # Ensure emissions_kgCO2e is numeric
        st.session_state.emissions_data['emissions_kgCO2e'] = pd.to_numeric(st.session_state.emissions_data['emissions_kgCO2e'], errors='coerce')
        
        # Replace NaN with 0
        st.session_state.emissions_data['emissions_kgCO2e'].fillna(0, inplace=True)
        
        total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card(
                title=t('total_emissions'),
                value=f"{total_emissions:.2f}",
                suffix=" kgCO2e",
                icon="🌍"
            )
        with col2:
            if 'date' in st.session_state.emissions_data.columns:
                st.session_state.emissions_data['date'] = pd.to_datetime(st.session_state.emissions_data['date'], errors='coerce')
                if not st.session_state.emissions_data['date'].isnull().all():
                    latest_date = st.session_state.emissions_data['date'].max().strftime('%Y-%m-%d')
                else:
                    latest_date = "No date data"
                metric_card(
                    title="Latest Entry",
                    value=latest_date,
                    icon="📅"
                )
        with col3:
            entry_count = len(st.session_state.emissions_data)
            metric_card(
                title="Total Entries",
                value=str(entry_count),
                icon="📊"
            )
        
        # Charts
        st.markdown(f"<h2>{t('emissions_by_scope')}</h2>", unsafe_allow_html=True)
        
        # Check if there are any non-zero emissions before creating charts
        if total_emissions > 0:
            # Create scope data for pie chart
            scope_data = st.session_state.emissions_data.groupby('scope')['emissions_kgCO2e'].sum().reset_index()
            
            # Only create chart if we have data with emissions
            if not scope_data.empty and scope_data['emissions_kgCO2e'].sum() > 0:
                fig1 = px.pie(
                    scope_data, 
                    values='emissions_kgCO2e', 
                    names='scope', 
                    color='scope', 
                    color_discrete_map={'Scope 1': '#4CAF50', 'Scope 2': '#2196F3', 'Scope 3': '#FFC107'},
                    hole=0.4
                )
                fig1.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    height=400
                )
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No emissions data available for scope breakdown.")
        else:
            st.info("No emissions data available for scope breakdown.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<h2>{t('emissions_by_category')}</h2>", unsafe_allow_html=True)
            
            if total_emissions > 0:
                # Create category data for bar chart
                category_data = st.session_state.emissions_data.groupby('category')['emissions_kgCO2e'].sum().reset_index()
                category_data = category_data.sort_values('emissions_kgCO2e', ascending=False)
                
                # Only create chart if we have data with emissions
                if not category_data.empty and category_data['emissions_kgCO2e'].sum() > 0:
                    fig2 = px.bar(
                        category_data, 
                        x='category', 
                        y='emissions_kgCO2e', 
                        color='category',
                        labels={'emissions_kgCO2e': 'Emissions (kgCO2e)', 'category': 'Category'}
                    )
                    fig2.update_layout(
                        showlegend=False,
                        margin=dict(t=0, b=0, l=0, r=0),
                        height=400
                    )
                    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("No emissions data available for category breakdown.")
            else:
                st.info("No emissions data available for category breakdown.")
        
        with col2:
            st.markdown(f"<h2>{t('emissions_over_time')}</h2>", unsafe_allow_html=True)
            
            if total_emissions > 0 and 'date' in st.session_state.emissions_data.columns:
                # Convert date column to datetime
                time_data = st.session_state.emissions_data.copy()
                time_data['date'] = pd.to_datetime(time_data['date'], errors='coerce')
                
                # Filter out rows with invalid dates
                time_data = time_data.dropna(subset=['date'])
                
                if not time_data.empty:
                    # Create month column for aggregation
                    time_data['month'] = time_data['date'].dt.strftime('%Y-%m')
                    
                    # Group by month and scope
                    time_data = time_data.groupby(['month', 'scope'])['emissions_kgCO2e'].sum().reset_index()
                    
                    if len(time_data['month'].unique()) > 0:
                        # Create line chart
                        fig3 = px.line(
                            time_data, 
                            x='month', 
                            y='emissions_kgCO2e', 
                            color='scope', 
                            markers=True,
                            color_discrete_map={'Scope 1': '#4CAF50', 'Scope 2': '#2196F3', 'Scope 3': '#FFC107'},
                            labels={'emissions_kgCO2e': 'Emissions (kgCO2e)', 'month': 'Month', 'scope': 'Scope'}
                        )
                        fig3.update_layout(
                            margin=dict(t=0, b=0, l=0, r=0),
                            xaxis_title="",
                            yaxis_title="kgCO2e",
                            legend_title="",
                            height=400
                        )
                        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.info("Not enough time data to show emissions over time.")
                else:
                    st.info("No valid date data available for time series chart.")
            else:
                st.info("No emissions data available for time series chart.")

elif st.session_state.active_page == "Data Entry":
    st.markdown(f"<h1> {t('data_entry')}</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs([" Manual Entry", " CSV Upload"])
    
    with tabs[0]:
        st.markdown("<h3>Add New Resource Entry</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True) # Replaces the st.form to allow real-time dropdown updates
        
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input(t('date'), datetime.now(), help="Date when the activity occurred")
            
            # The GTU Pivot: Replaces "Scope"
            resource_category = st.selectbox(
                "Sustainability Category", 
                ["Energy Consumption", "Waste Management", "Carbon Emissions"],
                help="GTU Domain 3: Select the specific resource you are tracking."
            )
            
            # Dynamic Activities based on Resource Category
            if resource_category == "Energy Consumption":
                activity_list = ['Grid Electricity', 'Solar Power', 'Wind Power', 'Diesel Generator', 'Other']
            elif resource_category == "Waste Management":
                activity_list = ['Plastic Waste', 'E-Waste', 'Industrial Solid Waste', 'Organic Waste', 'Other']
            else:
                activity_list = ['Stationary Combustion', 'Mobile Combustion', 'Fugitive Emissions', 'Other']
                
            activity = st.selectbox("Specific Activity", activity_list)
            # The GTU Requirement: Renewable vs Non-Renewable Tracking
            if resource_category == "Energy Consumption":
                if activity in ['Solar Power', 'Wind Power']:
                    energy_type = "Renewable (Clean)"
                    st.success("🌱 Auto-locked to Renewable Energy")
                elif activity == 'Diesel Generator':
                    energy_type = "Non-Renewable (Fossil)"
                    st.warning("🛢️ Auto-locked to Fossil Fuels")
                else:
                    # For Grid or Custom options where it could be either
                    energy_type = st.radio(
                        "Energy Source Type", 
                        ["Non-Renewable (Fossil)", "Renewable (Clean)"]
                    )
            else:
                energy_type = "N/A"# Handled automatically if it's waste or direct carbon
            if activity == 'Other':
                activity = st.text_input("Custom Activity", placeholder="Enter custom activity")
                
            facility = st.text_input("Facility/Location", placeholder="e.g., Main Campus, Factory A")
            
            # Keep the business context for the enterprise look
            business_unit = st.selectbox(
                "Business Unit", 
                ["Corporate", "Manufacturing", "Sales", "Logistics", "Other"]
            )
            if business_unit == "Other":
                business_unit = st.text_input("Custom Business Unit", placeholder="Enter unit name")

            project = st.text_input("Project Name (Optional)", placeholder="e.g., Q3 Manufacturing")

        with col2:
            country_options = ['India', 'United States', 'United Kingdom', 'Japan', 'Indonesia', 'Other']
            country = st.selectbox("Country", country_options)
            if country == 'Other':
                country = st.text_input("Custom Country", placeholder="Enter country name")
                
            responsible_person = st.text_input("Responsible Person", placeholder="Person accountable")

            # Quantity and dynamic Units
            quantity = st.number_input(t('quantity'), min_value=0.0, format="%.2f")
            
            if resource_category == "Waste Management":
                unit_options = ['kg', 'tonnes']
            elif resource_category == "Energy Consumption":
                unit_options = ['kWh', 'MWh', 'GJ']
            else:
                unit_options = ['liter', 'gallon', 'kg', 'Other']
                
            unit = st.selectbox(t('unit'), unit_options)
            if unit == 'Other':
                unit = st.text_input(t('custom_unit'), placeholder="Enter custom unit")
                
            # Simplified Default Factor to prevent the dictionary crash
            default_factor = 0.82 if country == 'India' and resource_category == 'Energy Consumption' else 0.5
            st.info(f"💡 AI Suggestion: Typical impact factor for {resource_category} in {country} is ~{default_factor} per unit.")
            
            emission_factor = st.number_input("Impact Factor", min_value=0.0, value=default_factor, format="%.4f")
            
            data_quality = st.select_slider("Data Quality", options=["Low", "Medium", "High"], value="Medium")
            verification_status = st.selectbox("Verification Status", ["Unverified", "Internally Verified", "Third-Party Verified"])
            notes = st.text_area(t('notes'), placeholder="Additional context...")

        # --- THE SUBMIT BUTTON LOGIC (Outside the columns) ---
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.button(t('add_entry'), type="primary", use_container_width=True)
        
        if submitted:
            if quantity <= 0:
                st.error("Quantity must be greater than zero.")
            else:
                try:
                    # THE ADAPTER: Trick the old backend by passing our new variables into the old slots
                    add_emission_entry(
                        date=date, 
                        business_unit=business_unit, 
                        project=project, 
                        scope=resource_category,     # Dashboard pie chart uses this
                        category=energy_type,        # Dashboard bar chart uses this
                        activity=activity, 
                        country=country, 
                        facility=facility,
                        responsible_person=responsible_person, 
                        quantity=quantity, 
                        unit=unit, 
                        emission_factor=emission_factor, 
                        data_quality=data_quality, 
                        verification_status=verification_status, 
                        notes=notes
                    )
                    st.success(t('entry_added'))
                    time.sleep(1) # Visual feedback pause
                    st.session_state.active_page = "Dashboard"
                    st.rerun()
                except Exception as e:
                    st.error(f"{t('entry_failed')} {str(e)}")
                    
    # --- TABLE AND CSV TABS (Kept mostly intact, updated headers for clarity) ---
    if len(st.session_state.emissions_data) > 0:
        st.markdown("<h3>Existing Resource Data</h3>", unsafe_allow_html=True)
        display_df = st.session_state.emissions_data.copy()
        col_tab1, col_tab2 = st.columns([3, 1])
        
        with col_tab1:
            st.dataframe(
                display_df,
                column_config={
                    "date": st.column_config.DateColumn("Date"),
                    "business_unit": st.column_config.TextColumn("Business Unit"),
                    "project": st.column_config.TextColumn("Project"),
                    "scope": st.column_config.TextColumn("Resource Category"), # Renamed header
                    "category": st.column_config.TextColumn("Energy Type"),    # Renamed header
                    "activity": st.column_config.TextColumn("Activity"),
                    "country": st.column_config.TextColumn("Country"),
                    "facility": st.column_config.TextColumn("Facility"),
                    "responsible_person": st.column_config.TextColumn("Responsible Person"),
                    "quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
                    "unit": st.column_config.TextColumn("Unit"),
                    "emission_factor": st.column_config.NumberColumn("Impact Factor", format="%.4f"),
                    "emissions_kgCO2e": st.column_config.NumberColumn("Total Impact", format="%.2f"),
                    "data_quality": st.column_config.TextColumn("Data Quality"),
                    "verification_status": st.column_config.TextColumn("Verification"),
                    "notes": st.column_config.TextColumn("Notes"),
                },
                use_container_width=True,
                hide_index=False
            )
        
        with col_tab2:
            st.markdown("### Delete Entry")
            entry_to_delete = st.number_input(
                            "Select entry number to delete", 
                            min_value=0, 
                            step=1, 
                            help="Enter the exact row index shown in the table."
                        )
            
            if st.button("🗑️ Delete Selected Entry", type="primary"):
                if delete_emission_entry(entry_to_delete):
                    st.success(f"Entry {entry_to_delete} deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to delete entry {entry_to_delete}")
        
    with tabs[1]:
        st.markdown("<h3>Upload CSV File</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(t('upload_csv'), type='csv')
        if uploaded_file is not None:
            if process_csv(uploaded_file):
                st.success(t('csv_uploaded'))
                st.session_state.active_page = "Dashboard"
                st.rerun()
            else:
                st.error("Failed to process CSV file. Please check the format.")

# Reports page removed - focusing on AI features only

elif st.session_state.active_page == "Settings":
    st.markdown(f"<h1> {t('settings')}</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3>Company Information</h3>", unsafe_allow_html=True)
        
    # Company info form
    with st.form("company_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name")
            industry = st.text_input("Industry")
            location = st.text_input("Location")
        with col2:
            contact_person = st.text_input("Contact Person")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        
        st.markdown("<h4>Export Markets</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            eu_market = st.checkbox("European Union")
        with col2:
            japan_market = st.checkbox("Japan")
        with col3:
            indonesia_market = st.checkbox("Indonesia")
        
        submitted = st.form_submit_button("Save Settings")
        if submitted:
            st.success("Settings saved successfully!")

elif st.session_state.active_page == "AI Insights":
    st.markdown(f"<h1>🤖 AI Insights</h1>", unsafe_allow_html=True)
    
    # Import AI agents
    from ai_agents import CarbonFootprintAgents
    
    # Initialize AI agents
    if 'ai_agents' not in st.session_state:
        st.session_state.ai_agents = CarbonFootprintAgents()
    
    # Create tabs for different AI insights
    ai_tabs = st.tabs(["Data Assistant", "Report Summary", "Offset Advisor", "Regulation Radar", "Emission Optimizer"])
    
    with ai_tabs[0]:
        st.markdown("<h3>Data Entry Assistant</h3>", unsafe_allow_html=True)
        st.markdown("Get help with classifying emissions and mapping them to the correct scope.")
        
        data_description = st.text_area("Describe your emission activity", 
                                      placeholder="Example: We use diesel generators for backup power at our office in Mumbai. How should I categorize this?")
        
        if st.button("Get Assistance", key="data_assistant_btn"):
            if data_description:
                with st.spinner("AI assistant is analyzing your request..."):
                    try:
                        result = st.session_state.ai_agents.run_data_entry_crew(data_description)
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
            else:
                st.warning("Please describe your emission activity first.")
    
    with ai_tabs[1]:
        st.markdown("<h3>Report Summary Generator</h3>", unsafe_allow_html=True)
        st.markdown("Generate a human-readable summary of your emissions data.")
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            if st.button("Generate Summary", key="report_summary_btn"):
                with st.spinner("Generating report summary..."):
                    try:
                        # Convert DataFrame to string representation for the AI
                        emissions_str = st.session_state.emissions_data.to_string()
                        result = st.session_state.ai_agents.run_report_summary_crew(emissions_str)
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
    
    with ai_tabs[2]:
        st.markdown("<h3>Carbon Offset Advisor</h3>", unsafe_allow_html=True)
        st.markdown("Get recommendations for verified carbon offset options based on your profile.")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location", placeholder="e.g., Mumbai, India")
            industry = st.selectbox("Industry", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"])
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
            st.markdown(f"<p>Total emissions to offset: <strong>{total_emissions:.2f} kgCO2e</strong></p>", unsafe_allow_html=True)
            
            if st.button("Get Offset Recommendations", key="offset_advisor_btn"):
                if location:
                    with st.spinner("Finding offset options..."):
                        try:
                            result = st.session_state.ai_agents.run_offset_advice_crew(total_emissions, location, industry)
                            # Handle CrewOutput object by converting it to string
                            result_str = str(result)
                            st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}. Please check your API key and try again.")
                else:
                    st.warning("Please enter your location.")
    
    with ai_tabs[3]:
        st.markdown("<h3>Regulation Radar</h3>", unsafe_allow_html=True)
        st.markdown("Get insights on current and upcoming carbon regulations relevant to your business.")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Company Location", placeholder="e.g., Jakarta, Indonesia", key="reg_location")
            industry = st.selectbox("Industry Sector", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"], key="reg_industry")
        with col2:
            export_markets = st.multiselect("Export Markets", ["European Union", "Japan", "United States", "China", "Indonesia", "India", "Other"])
        
        if st.button("Check Regulations", key="regulation_radar_btn"):
            if location and len(export_markets) > 0:
                with st.spinner("Analyzing regulatory requirements..."):
                    try:
                        result = st.session_state.ai_agents.run_regulation_check_crew(location, industry, ", ".join(export_markets))
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
            else:
                st.warning("Please enter your location and select at least one export market.")
    
    with ai_tabs[4]:
        st.markdown("<h3>Emission Optimizer</h3>", unsafe_allow_html=True)
        st.markdown("Get AI-powered recommendations to reduce your carbon footprint.")
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            if st.button("Generate Optimization Recommendations", key="emission_optimizer_btn"):
                with st.spinner("Analyzing your emissions data..."):
                    try:
                        # Convert DataFrame to string representation for the AI
                        emissions_str = st.session_state.emissions_data.to_string()
                        result = st.session_state.ai_agents.run_optimization_crew(emissions_str)
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
    
# About page removed - focusing on AI features only
