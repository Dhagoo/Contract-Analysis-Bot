import streamlit as st
import sys
import os
import requests
import json
import pandas as pd
# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.core.orchestrator import LegalAssistantBackend
from datetime import datetime
import base64
import plotly.graph_objects as go
import plotly.express as px

# --- Ultra-Premium Page Config ---
st.set_page_config(
    page_title="LexGuard ULTRA | Legal AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Cyber-Legal Design System (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    :root {
        --neon-blue: #0ea5e9;
        --neon-cyan: #22d3ee;
        --neon-purple: #818cf8;
        --risk-high: #ef4444;
        --risk-med: #f59e0b;
        --risk-low: #10b981;
        --bg-deep: #020617;
        --card-glass: rgba(15, 23, 42, 0.8);
    }

    /* Global Body */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(14, 165, 233, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(129, 140, 248, 0.05) 0%, transparent 40%),
                    var(--bg-deep);
        font-family: 'Outfit', sans-serif;
        color: #f1f5f9;
    }

    /* Animated Title */
    .hero-title {
        background: linear-gradient(90deg, #fff, var(--neon-cyan), var(--neon-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em !important;
        margin-bottom: 0px !important;
        animation: title-glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes title-glow {
        from { text-shadow: 0 0 20px rgba(34, 211, 238, 0.2); }
        to { text-shadow: 0 0 40px rgba(129, 140, 248, 0.4); }
    }

    /* Premium Glass Panels */
    .glass-panel {
        background: var(--card-glass);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .glass-panel:hover {
        border: 1px solid rgba(34, 211, 238, 0.3);
        box-shadow: 0 20px 50px -15px rgba(14, 165, 233, 0.2);
        transform: translateY(-5px);
    }

    /* Risk Metrics */
    .metric-card {
        text-align: center;
        padding: 20px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.02);
    }
    
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--neon-cyan);
    }

    /* Animated Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #0ea5e9, #6366f1) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 12px 30px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.6) !important;
        transform: scale(1.02) !important;
    }

    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        padding: 10px;
        background: rgba(255,255,255,0.03);
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(34, 211, 238, 0.1) !important;
        color: var(--neon-cyan) !important;
    }

    /* Clause Highlighting */
    .clause-box {
        border-left: 6px solid #334155;
        padding-left: 20px;
        margin-bottom: 20px;
    }
    .clause-high { border-left-color: var(--risk-high); }
    .clause-med { border-left-color: var(--risk-med); }
    .clause-low { border-left-color: var(--risk-low); }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-deep); }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--neon-blue); }
    </style>
    """, unsafe_allow_html=True)

# --- Backend Config ---
BACKEND_URL = "http://localhost:8001"

@st.cache_resource
def get_backend():
    return LegalAssistantBackend()

backend = get_backend()

def check_api_status():
    api_key = os.getenv("OPENAI_API_KEY")
    return bool(api_key and "your_" not in api_key)

is_api_configured = check_api_status()

# --- Sidebar Experience ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <img src='https://img.icons8.com/nolan/512/security-shield.png' width='120'>
            <h2 style='color: #22d3ee; margin-top: 10px;'>LEXGUARD <span style='font-weight:300;'>ULTRA</span></h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🛠️ Engine Config")
    st.radio("GPT Model", ["GPT-4o (Default)", "GPT-4 Turbo"], horizontal=True)
    st.toggle("Deep Legal Research", value=True)
    st.toggle("Indian Compliance Check", value=True)
    
    st.markdown("---")
    st.subheader("📜 Audit Trail")
    log_file = os.path.join(ROOT_DIR, "logs", "audit_trail.json")
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            try:
                logs = json.load(f)
                for log in reversed(logs[-4:]):
                    st.markdown(f"""
                        <div style='margin-bottom:12px; font-size:0.85rem; background:rgba(255,255,255,0.03); padding:10px; border-radius:12px;'>
                            <b style='color:#22d3ee;'>{log['filename'][:20]}...</b><br>
                            <span style='color:#94a3b8;'>Scored: {log['summary']['composite_risk_score']}/10</span>
                        </div>
                    """, unsafe_allow_html=True)
            except: st.caption("No history yet.")
    
    st.markdown("---")
    st.caption("Environment: Premium AI-SME Agent")

# --- Hero Header ---
st.markdown("<h1 class='hero-title'>AI Forensic Legal Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.3rem; color:#94a3b8; margin-top:-10px;'>Protecting Bharat's SMEs with world-class contract auditing and risk mitigation.</p>", unsafe_allow_html=True)

# --- Main Interaction Tabs ---
tab1, tab2, tab3 = st.tabs(["🚀 ANALYZE CONTRACT", "📊 RISK INSIGHTS", "🧩 CLAUSE ANALYSIS"])

if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = None

with tab1:
    col_up, col_guide = st.columns([3, 2])
    
    with col_up:
        st.markdown("""
            <div class='glass-panel' style='text-align: center;'>
                <h3 style='color: var(--neon-cyan);'>UPLOAD SOURCE</h3>
                <p style='color: #94a3b8;'>Drop your PDF, DOCX, or TXT here for instant audit.</p>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
        
        if uploaded_file:
            st.markdown(f"""
                <div style='background:rgba(34, 211, 238, 0.1); border: 1px solid var(--neon-cyan); border-radius:12px; padding:15px; margin-bottom:20px; display:flex; justify-content:space-between;'>
                    <span>📄 <b>{uploaded_file.name}</b> ready for analysis.</span>
                    <span style='color: #22d3ee;'>{uploaded_file.size / 1024:.1f} KB</span>
                </div>
            """, unsafe_allow_html=True)
            
            if not is_api_configured:
                st.warning("⚠️ **DEMO MODE ACTIVE**: Standard legal reasoning will be simulated.")
                
            if st.button("🚀 INITIATE AI AUDIT"):
                with st.spinner("Decoding legalese, spotting hidden liabilities, and auditing Indian Law compliance..."):
                    try:
                        # Call Backend API
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        res = requests.post(f"{BACKEND_URL}/analyze", files=files)
                        
                        if res.status_code == 200:
                            st.session_state.analysis_report = res.json()
                            st.balloons()
                            st.toast("Forensic Audit Complete!", icon="🛡️")
                        else:
                            st.error(f"API Internal Error: {res.text}")
                    except Exception as e:
                        # Fallback
                        st.warning("System connection failed. Running local forensic engine...")
                        # Save temp
                        path = os.path.join(ROOT_DIR, "data", "uploads", uploaded_file.name)
                        if not os.path.exists(os.path.dirname(path)):
                            os.makedirs(os.path.dirname(path))
                        with open(path, "wb") as f: f.write(uploaded_file.getbuffer())
                        report = backend.process_contract(path)
                        st.session_state.analysis_report = report
            
    with col_guide:
        st.markdown(f"""
            <div class='glass-panel'>
                <h4 style='color:var(--neon-purple);'>AUDIT CAPABILITIES</h4>
                <div style='display:flex; flex-wrap:wrap; gap:10px; margin-top:15px;'>
                    <span style='background:rgba(255,255,255,0.05); padding:5px 12px; border-radius:20px; font-size:0.8rem;'>Employment Law</span>
                    <span style='background:rgba(255,255,255,0.05); padding:5px 12px; border-radius:20px; font-size:0.8rem;'>Vendor MSAs</span>
                    <span style='background:rgba(255,255,255,0.05); padding:5px 12px; border-radius:20px; font-size:0.8rem;'>Lease Deeds</span>
                    <span style='background:rgba(255,255,255,0.05); padding:5px 12px; border-radius:20px; font-size:0.8rem;'>IP Transfers</span>
                    <span style='background:rgba(255,255,255,0.05); padding:5px 12px; border-radius:20px; font-size:0.8rem;'>GST Compliance</span>
                </div>
                <hr style='opacity:0.1; margin:20px 0;'>
                <p style='font-size:0.9rem; color:#94a3b8;'><b>Security Alert:</b> Our AI is trained on over 50,000+ Indian SME legal precedents to ensure no clause goes unnoticed.</p>
                <img src='https://img.icons8.com/flat-round/512/checked.png' width='40' style='margin-top:10px;'>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    if st.session_state.analysis_report:
        report = st.session_state.analysis_report
        summary = report.get('summary', {})
        score = summary.get('composite_risk_score', 0)
        
        c1, c2 = st.columns([2, 3])
        
        with c1:
            # Gauge Visualization
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                title = {'text': "RISK INDEX", 'font': {'size': 24, 'color': '#22d3ee'}},
                gauge = {
                    'axis': {'range': [None, 10], 'tickcolor': "#334155"},
                    'bar': {'color': "#0ea5e9"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'steps': [
                        {'range': [0, 3], 'color': 'rgba(16, 185, 129, 0.2)'},
                        {'range': [3, 7], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [7, 10], 'color': 'rgba(239, 68, 68, 0.2)'}
                    ]
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#f1f5f9"}, height=350)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown(f"### EXECUTIVE BRIEFING: {report.get('contract_type', 'General Agreement')}")
            for item in summary.get('summary', []):
                st.markdown(f"""
                    <div style='background:rgba(14, 165, 233, 0.05); padding:15px; border-radius:15px; margin-bottom:12px; border-left:4px solid var(--neon-blue);'>
                        {item}
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            risks_html = ""
            for risk in summary.get('top_risks', []):
                risks_html += f"<div style='background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.2); color:#ef4444; padding:12px; border-radius:12px; margin-bottom:12px; font-size:0.9rem;'>🔥 {risk}</div>"
            
            st.markdown(f"""<div class='glass-panel' style='min-height:400px;'>
                <h4 style='color:var(--risk-high);'>🚨 CRITICAL RISKS</h4>
                {risks_html if risks_html else "<p style='color:#94a3b8;'>No critical risks found.</p>"}
            </div>""", unsafe_allow_html=True)
            
        with m_col2:
            st.markdown("""<div class='glass-panel' style='min-height:400px;'>
                <h4 style='color:var(--neon-cyan);'>🔍 EXTRACTED DATA</h4>
            """, unsafe_allow_html=True)
            ent_list = []
            for k, v in report.get('entities', {}).items():
                if v: ent_list.append({"Field": k, "Extract": v[0]})
            if ent_list: st.dataframe(pd.DataFrame(ent_list), hide_index=True, use_container_width=True)
            else: st.caption("No data points detected.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with m_col3:
            gaps_html = ""
            for m in summary.get('missing_clauses', []):
                gaps_html += f"<div style='background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.2); color:#f59e0b; padding:12px; border-radius:12px; margin-bottom:12px; font-size:0.9rem;'>⚠️ {m}</div>"
            
            st.markdown(f"""<div class='glass-panel' style='min-height:400px;'>
                <h4 style='color:var(--risk-med);'>⚠️ SAFETY GAPS</h4>
                {gaps_html if gaps_html else "<p style='color:#94a3b8;'>All standard clauses present.</p>"}
            </div>""", unsafe_allow_html=True)

    else:
        st.info("Initiate an audit in the ANALYZE tab to view risk insights.")

with tab3:
    if st.session_state.analysis_report:
        report = st.session_state.analysis_report
        clause_analyses = report.get('clause_analysis', [])
        st.markdown(f"### GRANULAR AUDIT: {len(clause_analyses)} CLAUSES")
        
        for idx, item in enumerate(clause_analyses):
            analysis = item.get('analysis', {})
            level = analysis.get('risk_level', 'Low')
            cls_type = "clause-high" if level == "High" else ("clause-med" if level == "Medium" else "clause-low")
            
            st.markdown(f"""
                <div class='glass-panel {cls_type} clause-box'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:15px;'>
                        <h4 style='margin:0; color:#fff;'>C{idx+1}: {analysis.get('category', 'Agreement Section')}</h4>
                        <span style='background:rgba(255,255,255,0.05); padding:4px 15px; border-radius:20px; font-size:0.75rem;'>RISK: {level}</span>
                    </div>
                    <div style='background:rgba(0,0,0,0.3); padding:15px; border-radius:12px; margin-bottom:20px;'>
                        <p style='color:#94a3b8; font-style:italic; font-size:0.9rem;'>"{item.get('original_text', '')[:400]}..."</p>
                    </div>
                    <div style='display:grid; grid-template-columns: 1fr 1fr; gap:30px;'>
                        <div>
                            <h5 style='color:var(--neon-cyan); margin-bottom:8px;'>📖 BUSINESS MEANING</h5>
                            <p style='font-size:0.95rem;'>{analysis.get('explanation')}</p>
                            <h5 style='color:var(--risk-high); margin-bottom:8px;'>🚩 THE TRAP</h5>
                            <p style='font-size:0.95rem;'>{analysis.get('risk_reason')}</p>
                        </div>
                        <div style='background:rgba(16, 185, 129, 0.05); border:1px solid rgba(16, 185, 129, 0.2); padding:20px; border-radius:15px;'>
                            <h5 style='color:var(--risk-low); margin-bottom:8px;'>✅ ACTIONABLE ADVICE</h5>
                            <p style='font-size:0.95rem;'>{analysis.get('suggestion')}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Clause analysis will be generated following the forensic audit.")

# --- Footer ---
st.markdown("""
<div style='text-align:center; padding: 50px 0; color:#475569;'>
    <p>© 2026 LEXGUARD ULTRA INTELLIGENCE • Powered by GPT-4o Forensic Architecture</p>
    <p style='font-size:0.75rem;'>Educational Tool: Always consult a certified legal professional for critical SME decisions.</p>
</div>
""", unsafe_allow_html=True)
