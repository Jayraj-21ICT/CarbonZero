import streamlit as st
from dotenv import load_dotenv
import data_store as ds
import ui_components as ui

# Initialize environment and page config MUST be the first Streamlit command
load_dotenv()
st.set_page_config(page_title="GreenOps - ESG Analytics", page_icon="🌱", layout="wide")

# Load global state and base CSS
ds.init_session_state()
ui.load_css()

# --- LANDING PAGE SPECIFIC CSS (ANIMATIONS & HOVER EFFECTS) ---
st.markdown("""
<style>
/* Keyframe Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Hero Section */
.hero-wrapper {
    text-align: center;
    padding: 4rem 2rem 3rem 2rem;
    animation: fadeInUp 0.8s ease-out forwards;
}
.hero-title {
    font-size: 4rem !important;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 0.5rem;
    letter-spacing: -0.03em;
}
.hero-title span {
    color: #10B981; /* Emerald Green */
}
.hero-subtitle {
    font-size: 1.25rem;
    color: #64748B;
    max-width: 800px;
    margin: 0 auto 2rem auto;
    line-height: 1.6;
}

/* Feature Cards */
.lp-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 2rem;
    height: 100%;
    transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    position: relative;
    overflow: hidden;
    animation: fadeInUp 1s ease-out forwards;
}
.lp-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 4px;
    background: linear-gradient(90deg, #10B981, #34D399);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.lp-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(16, 185, 129, 0.04);
    border-color: #A7F3D0;
}
.lp-card:hover::before {
    opacity: 1;
}
.lp-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: inline-block;
}
.lp-card h3 {
    font-size: 1.3rem;
    color: #0F172A;
    margin-bottom: 0.75rem;
}
.lp-card p {
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 0;
}

/* Status Indicator */
.status-pill {
    display: inline-flex;
    align-items: center;
    background: #ECFDF5;
    color: #065F46;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 2rem;
    border: 1px solid #A7F3D0;
}
.status-dot {
    height: 8px; width: 8px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulseGlow 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("""
<div class="hero-wrapper">
    <div class="status-pill">
        <span class="status-dot"></span> System Online & Ready
    </div>
    <h1 class="hero-title">Welcome to <span>GreenOps</span></h1>
    <p class="hero-subtitle">
        The next-generation, AI-powered carbon accounting engine. 
        Engineered to streamline Scope 1, 2, and 3 emissions tracking, ensure CBAM compliance, 
        and provide predictive sustainability insights for modern enterprises.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- CORE CAPABILITIES (3 COLUMNS) ---
st.markdown("<h2 style='text-align: center; margin-bottom: 2rem; font-size: 1.8rem;'>Core Platform Capabilities</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="lp-card" style="animation-delay: 0.1s;">
        <div class="lp-icon">📊</div>
        <h3>GHG Protocol Physics Engine</h3>
        <p>Mathematical rigor matters. Our data ingestion pipeline utilizes strict, regionally-locked DEFRA and IPCC emission factors to eliminate hallucination and guarantee audit-ready Scope 1, 2, and 3 carbon math.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="lp-card" style="animation-delay: 0.2s;">
        <div class="lp-icon">🧠</div>
        <h3>Autonomous AI Advisory</h3>
        <p>Powered by Llama-3, our autonomous agents compress raw vector data to bypass token limits, delivering real-time operational optimization, cost-reduction strategies, and automated executive reporting.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="lp-card" style="animation-delay: 0.3s;">
        <div class="lp-icon">🌍</div>
        <h3>CBAM Regulation Radar</h3>
        <p>Stay ahead of carbon taxes. The system dynamically cross-references your supply chain and export markets (EU CBAM, US, ASEAN) to preemptively flag compliance gaps and border-tax liabilities.</p>
    </div>
    """, unsafe_allow_html=True)

# --- HOW TO NAVIGATE SECTION ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### 🧭 System Navigation")

nav_col1, nav_col2 = st.columns([1, 2])

with nav_col1:
    st.info("""
    **Use the sidebar to begin:**
    1. **⚙️ Settings:** Configure your enterprise profile.
    2. **📝 Data Entry:** Log operations or upload CSVs.
    3. **📊 Dashboard:** View transition trajectories.
    4. **🤖 AI Insights:** Generate compliance reports.
    """)

with nav_col2:
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3B82F6;">
        <h4 style="margin-top: 0; color: #1E3A8A; font-size: 1.1rem;">🔒 Enterprise Grade Architecture</h4>
        <p style="color: #475569; font-size: 0.95rem; margin-bottom: 0;">
            GreenOps is built on a modular, isolated-memory architecture. Data operations are protected by cryptographic MD5 row-hashing to prevent duplicate ingestion, while destructive database actions are guarded by explicit user verification protocols.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 0.85rem;">
    GreenOps Sustainability Engine • v2.0.0
</div>
""", unsafe_allow_html=True)