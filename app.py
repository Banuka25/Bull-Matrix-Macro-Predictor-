import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime
import pytz
import base64
import os
import streamlit.components.v1 as components
from supabase import create_client, Client

st.set_page_config(page_title="Macro DXY Predictor Pro", page_icon="📈", layout="wide")

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = "https://dtcwcaojqpsjuyzfdqlu.supabase.co"
SUPABASE_KEY = "sb_publishable_hIHjcXuH_uAciS5Mn0fjqA_e1TGsPfk"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Initialize Session States
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'journal' not in st.session_state:
    st.session_state['journal'] = []
if 'loaded_data' not in st.session_state:
    st.session_state['loaded_data'] = None

# --- DATABASE FETCH FUNCTION ---
def fetch_journal():
    if st.session_state['user']:
        try:
            response = supabase.table('journal_entries').select('*').eq('user_id', st.session_state['user'].id).order('id', desc=True).execute()
            formatted_journal = []
            for row in response.data:
                formatted_journal.append({
                    "id": row["id"],
                    "Date & Time": row["created_at"],
                    "News Event": row["news_event"],
                    "DXY Score": row["dxy_score"],
                    "Predicted Direction": row["prediction"],
                    "Inputs": row["inputs"]
                })
            st.session_state['journal'] = formatted_journal
        except Exception as e:
            st.error(f"Cloud Sync Error: {e}")

# --- Language Toggle Switch ---
st.sidebar.markdown("<br>", unsafe_allow_html=True)
lang = st.sidebar.radio("🌐 Language / භාෂාව", ["English", "සිංහල"], horizontal=True)
st.sidebar.markdown("---")

# --- LOGIN / SIGNUP UI ---
if st.session_state['user'] is None:
    # Basic CSS for Login Page
    st.markdown("""<style>.main { background-color: #0e1117; color: #ffffff; }</style>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        title_txt = "🔐 Login to Bull Matrix Predictor" if lang == "English" else "🔐 ඇප් එකට ලොග් වෙන්න"
        st.title(title_txt)
        st.write("Secure Cloud Database Enabled." if lang == "English" else "ඔබගේ දත්ත Cloud එකේ ආරක්ෂිතව සේව් වේ.")
        
        tab_login, tab_signup = st.tabs(["Login / ඇතුල්වන්න", "Sign Up / ලියාපදිංචි වන්න"])
        
        with tab_login:
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Password", type="password", key="login_pwd")
            if st.button("Login", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                    st.session_state['user'] = res.user
                    fetch_journal()
                    st.rerun()
                except Exception as e:
                    st.error("Login Failed! Please check your credentials." if lang == "English" else "ලොග් වීමට නොහැක! Email සහ Password නිවැරදිදැයි බලන්න.")
                    
        with tab_signup:
            email_up = st.text_input("New Email", key="up_email")
            pwd_up = st.text_input("New Password", type="password", key="up_pwd")
            if st.button("Sign Up", use_container_width=True):
                try:
                    res = supabase.auth.sign_up({"email": email_up, "password": pwd_up})
                    st.success("Account created successfully! Please login from the 'Login' tab." if lang == "English" else "ගිණුම සාර්ථකව සැකසුවා! කරුණාකර 'Login' ටැබ් එකෙන් ඇතුල්වන්න.")
                except Exception as e:
                    st.error(f"Sign Up Failed: {e}")
                    
    st.stop() # Stops execution of the rest of the app until logged in

# --- SIDEBAR LOGOUT ---
logout_txt = "Logout" if lang == "English" else "ඉවත් වන්න (Logout)"
st.sidebar.markdown(f"<div style='font-size: 13px; color: gray;'>👤 Logged in as:<br><b style='color: white;'>{st.session_state['user'].email}</b></div>", unsafe_allow_html=True)
if st.sidebar.button(logout_txt):
    supabase.auth.sign_out()
    st.session_state['user'] = None
    st.session_state['journal'] = []
    st.rerun()
st.sidebar.markdown("---")


# --- MOBILE RESPONSIVE PROFESSIONAL UI CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .bullish-text { color: #00ffcc; font-weight: bold; font-size: 24px; }
    .bearish-text { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    .neutral-text { color: #ffc107; font-weight: bold; font-size: 24px; }
    
    /* Elegant Vertical Line Styling */
    .vertical-divider {
        border-left: 2px solid rgba(255, 255, 255, 0.15);
        height: 100%;
        min-height: 520px;
        margin: 0 auto;
    }
    
    /* Radar Divider */
    .radar-divider {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        margin: 25px 0;
    }
    
    /* General Standard Button (Save to Journal) */
    .stButton > button[kind="secondary"] {
        border-radius: 20px !important;
        border: 1px solid #1f77b4 !important;
        background-color: transparent !important;
        color: #1f77b4 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #1f77b4 !important;
        color: white !important;
        transform: scale(1.05);
    }
    
    /* DOWNLOAD & CLEAR BUTTONS RESPONSIVENESS */
    .stDownloadButton > button,
    .stButton > button[kind="primary"] {
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
        width: 100% !important; /* Full width inside flex container */
    }
    .stDownloadButton > button {
        border: 1px solid #1f77b4 !important;
        background-color: transparent !important;
        color: #1f77b4 !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1f77b4 !important;
        color: white !important;
        transform: scale(1.05);
    }
    .stButton > button[kind="primary"] {
        border: 1px solid #ff4b4b !important;
        background-color: transparent !important;
        color: #ff4b4b !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #ff4b4b !important;
        color: white !important;
        transform: scale(1.05);
    }
    
    /* Ultra-Compact & Elegant Circular Delete/Load Buttons */
    button[title="Delete this entry"], button[title="Load this entry"] {
        width: 20px !important; height: 20px !important;
        min-height: 20px !important; min-width: 20px !important;
        padding: 0 !important; border-radius: 50% !important; 
        background-color: transparent !important; 
        display: inline-flex !important; align-items: center !important; justify-content: center !important;
        transition: all 0.2s ease !important;
    }
    button[title="Delete this entry"] { border: 1px solid #ff4b4b !important; color: #ff4b4b !important; }
    button[title="Delete this entry"]:hover { background-color: #ff4b4b !important; color: white !important; transform: scale(1.1) !important; }
    
    button[title="Load this entry"] { border: 1px solid #1f77b4 !important; color: #1f77b4 !important; }
    button[title="Load this entry"]:hover { background-color: #1f77b4 !important; color: white !important; transform: scale(1.1) !important; }
    
    button[title="Delete this entry"] div, button[title="Delete this entry"] p,
    button[title="Load this entry"] div, button[title="Load this entry"] p {
        margin: 0 !important; padding: 0 !important; line-height: 1 !important; font-size: 10px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        width: 100% !important; height: 100% !important; color: inherit !important;
    }

    /* ------------------------------------------------------------------- */
    /* UI FIX 1: Tooltips (Popups) cutoff fix on mobile */
    div[data-baseweb="tooltip"], div[data-baseweb="popover"], div[role="tooltip"] {
        max-width: 85vw !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    div[data-baseweb="tooltip"] > div, div[data-baseweb="popover"] > div {
        max-width: 100% !important;
        white-space: normal !important;
    }

    /* UI FIX 2: Horizontal Scrolling Wrapper for Mobile Cards */
    .mobile-scroll-container {
        display: flex;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 15px;
        padding-bottom: 10px;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
    }
    .mobile-scroll-container::-webkit-scrollbar { height: 6px; }
    .mobile-scroll-container::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }
    .mobile-scroll-container > div {
        flex: 0 0 auto !important;
    }
    
    /* Custom Journal Classes for Desktop */
    .journal-header b { font-size: 15px; }
    .journal-text { font-size: 14px; color: #d0d0d0; padding-top: 5px; }

    /* UI FIX 3 & 4: Mobile Specific Adjustments */
    @media (max-width: 768px) {
        /* Hide vertical divider on mobile to prevent huge gaps */
        .vertical-divider { display: none !important; }
        .radar-divider { margin: 15px 0 !important; }

        /* Journal Text Styling for Mobile */
        .journal-header b { font-size: 11px !important; }
        .journal-text { font-size: 11px !important; padding-top: 2px !important; white-space: normal !important; }
        .pred-text { font-size: 11px !important; }
        .pred-icon svg { width: 14px !important; height: 14px !important; }

        /* Force Journal Rows to be horizontal and scrollable on phone with exact widths */
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            padding-bottom: 10px !important;
            gap: 5px !important; /* Smaller gap */
            -webkit-overflow-scrolling: touch;
        }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"] {
            width: auto !important;
            flex: 0 0 auto !important;
            padding: 0 !important;
        }
        /* Lock specific widths for journal columns to prevent stretching */
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(1) { width: 105px !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(2) { width: 125px !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(3) { width: 65px !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(4) { width: 140px !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(5) { width: 60px !important; }
        
        /* Stop journal buttons from stacking */
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) div[data-testid="stHorizontalBlock"] {
             flex-direction: row !important;
             min-width: 50px !important;
             gap: 5px !important;
        }
        button[title="Delete this entry"], button[title="Load this entry"] {
            width: 18px !important; height: 18px !important;
            min-height: 18px !important; min-width: 18px !important;
        }

        /* Force Download & Clear Buttons to be small and closer together */
        div[data-testid="stHorizontalBlock"]:has(.action-btn-marker) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            justify-content: flex-start !important; /* Align left */
            gap: 10px !important; /* Closer together */
        }
        div[data-testid="stHorizontalBlock"]:has(.action-btn-marker) > div[data-testid="column"] {
            width: auto !important;
            flex: 0 1 auto !important;
            min-width: 0 !important;
        }
        /* Make button text and padding smaller */
        div[data-testid="stHorizontalBlock"]:has(.action-btn-marker) button {
            font-size: 11px !important;
            padding: 2px 10px !important;
            min-height: 32px !important;
        }
    }
    /* ------------------------------------------------------------------- */
    </style>
""", unsafe_allow_html=True)

def create_gauge_chart(score):
    if score >= 60:
        bar_color = "#00ffcc" 
        gauge_title = "Bullish Strength 🚀" if lang == "English" else "Bullish ශක්තිය 🚀"
    elif score <= 40:
        bar_color = "#ff4b4b" 
        gauge_title = "Bearish Strength 📉" if lang == "English" else "Bearish ශක්තිය 📉"
    else:
        bar_color = "#ffc107" 
        gauge_title = "Neutral / Volatile ⚖️" if lang == "English" else "Neutral / Volatile ⚖️"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score, domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': gauge_title, 'font': {'size': 18, 'color': '#a0a0a0'}},
        number = {'font': {'size': 50, 'color': bar_color}, 'suffix': "%"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#2b2b2b", 'tickfont': {'color': 'gray'}},
            'bar': {'color': bar_color, 'thickness': 0.8}, 'bgcolor': "#1a1c24", 'borderwidth': 0,
        }
    ))
    fig.update_layout(paper_bgcolor="#0e1117", font={'color': "white"}, height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def save_to_journal(event_name, score, direction_text, inputs_dict):
    sl_tz = pytz.timezone('Asia/Colombo')
    current_time = datetime.datetime.now(sl_tz).strftime("%Y-%m-%d %H:%M")
    clean_event = event_name.replace("🟢 ", "").replace("🟠 ", "").replace("🟣 ", "").replace("🔵 ", "").replace("🔴 ", "")
    
    db_entry = {
        "user_id": st.session_state['user'].id,
        "created_at": current_time,
        "news_event": clean_event,
        "dxy_score": f"{score}%",
        "prediction": direction_text,
        "inputs": inputs_dict
    }
    
    try:
        supabase.table('journal_entries').insert(db_entry).execute()
        fetch_journal() # Reload data to get the new ID and update state
        msg = "✅ Saved to Cloud Journal!" if lang == "English" else "✅ Cloud ජර්නල් එකට සේව් කළා!"
        st.toast(msg)
    except Exception as e:
        st.error(f"Error saving to Cloud: {e}")

def get_idx(event_name, input_key, options_list):
    clean_event = event_name.replace("🟢 ", "").replace("🟠 ", "").replace("🟣 ", "").replace("🔵 ", "").replace("🔴 ", "")
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] == clean_event:
        val = st.session_state['loaded_data']['Inputs'].get(input_key)
        if val in options_list:
            return options_list.index(val)
    return 0

def get_num_val(event_name, input_key, default_val):
    clean_event = event_name.replace("🟢 ", "").replace("🟠 ", "").replace("🟣 ", "").replace("🔵 ", "").replace("🔴 ", "")
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] == clean_event:
        return st.session_state['loaded_data']['Inputs'].get(input_key, default_val)
    return default_val

svg_bullish = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#4CAF50"/><path d="M7 15 L10.5 11.5 L13 14 L17 9 M13 9 H17 V13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
svg_bearish = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#F44336"/><path d="M7 9 L10.5 12.5 L13 10 L17 15 M13 15 H17 V11" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
svg_ranging = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#FFC107"/><path d="M8 10 L6 12 L8 14 M16 10 L18 12 L16 14 M6 12 H18" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
svg_volatile = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#FF9800"/><path d="M13 5 L7 13 H12 L11 19 L17 11 H12 L13 5 Z" fill="white" stroke="white" stroke-linejoin="round"/></svg>'''

def render_custom_metric(label, value, svg_icon):
    return f"""<div style="display: flex; flex-direction: column; margin-bottom: 10px;"><div style="font-size: 12px; color: #a0a0a0; margin-bottom: 5px; white-space: nowrap;">{label}</div><div style="display: flex; align-items: center; gap: 8px;"><div style="font-size: 16px; font-weight: bold; color: white;">{value}</div><div style="display: flex; align-items: center;">{svg_icon}</div></div></div>"""

# --- Header Texts ---
if lang == "English":
    st.title("📈 Ultimate Macro Indicator & Market Predictor")
    st.write("Institutional-grade fundamental analysis & educational tool for DXY, Pairs & Indices.")
else:
    st.title("📈 ප්‍රධාන ආර්ථික දර්ශකය සහ වෙළඳපොළ පුරෝකථනය")
    st.write("DXY සහ අනෙකුත් වෙළඳපොළවල් සඳහා ආයතනික මට්ටමේ මූලික විශ්ලේෂණ මෙවලම.")

st.markdown("---")

# Ordered Tabs
tab_names = ["🔮 Live Predictor", "📅 Live Calendar", "📓 Trading Journal", "📚 Historical Case Studies"] if lang == "English" else ["🔮 සජීවී පුරෝකථනය", "📅 සජීවී දින දර්ශනය", "📓 ට්‍රේඩින් ජර්නල් එක", "📚 අතීත සිදුවීම් අධ්‍යයනය"]
tab1, tab2, tab3, tab4 = st.tabs(tab_names)

with tab1:
    st.sidebar.header("📅 Select Major News Event" if lang == "English" else "📅 ප්‍රධාන නිවුස් එක තෝරන්න")
    
    events_list = ["🟢 CPI (Consumer Price Index)", "🟠 NFP (Non-Farm Payrolls)", "🟣 Core PCE Price Index", "🔵 Advance GDP", "🔴 FOMC Rate Decision"]
    default_event_idx = 0
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] in [e[4:] for e in events_list]:
        raw_events = [e[4:] for e in events_list]
        default_event_idx = raw_events.index(st.session_state['loaded_data']['News Event'])

    major_news = st.sidebar.radio("Choose Event:" if lang == "English" else "නිවුස් එක තෝරන්න:", events_list, index=default_event_idx)

    # --- Bull Matrix Personal Branding Footer ---
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    logo_path = "Bull-Matrix-logo.svg"
    if os.path.exists(logo_path):
        with open(logo_path, "r") as f:
            svg_data = f.read()
        b64_svg = base64.b64encode(svg_data.encode("utf-8")).decode("utf-8")
        logo_html = f'''<div style="text-align: center; margin-bottom: -10px;"><img src="data:image/svg+xml;base64,{b64_svg}" width="65%" style="filter: invert(1) brightness(2);"></div>'''
        st.sidebar.markdown(logo_html, unsafe_allow_html=True)
        
    quote_text = '"Decoding the macroeconomic matrix to empower traders with institutional-grade insights."' if lang == "English" else '"ආයතනික මට්ටමේ විශ්ලේෂණයන් හරහා සාර්ථක ට්‍රේඩර්ස්ලා බිහිකිරීමේ මෙහෙයුම."'
    st.sidebar.markdown(f'''<div style="text-align: center;"><p style="font-size: 22px; font-weight: 800; color: white; margin-bottom: 0px; letter-spacing: 1.5px;">BULL MATRIX</p><p style="font-size: 13px; color: #00ffcc; font-weight: bold; margin-bottom: 15px;">Macro Trader & Educator</p><div style="background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);"><p style="font-size: 12px; color: #d0d0d0; line-height: 1.4; margin-bottom: 0; font-style: italic;">{quote_text}</p></div></div>''', unsafe_allow_html=True)

    def render_market_metrics(score, is_fomc=False):
        if score >= 60:
            eurusd_val, eurusd_svg = "BEARISH", svg_bearish
            gbpusd_val, gbpusd_svg = "BEARISH", svg_bearish
            xauusd_val, xauusd_svg = "BEARISH", svg_bearish
            usdjpy_val, usdjpy_svg = "BULLISH", svg_bullish
            usdcad_val, usdcad_svg = "BULLISH", svg_bullish
            nas100_val, nas100_svg = "BEARISH", svg_bearish
            us30_val, us30_svg = "BEARISH", svg_bearish
            spx500_val, spx500_svg = "BEARISH", svg_bearish
        elif score <= 40:
            eurusd_val, eurusd_svg = "BULLISH", svg_bullish
            gbpusd_val, gbpusd_svg = "BULLISH", svg_bullish
            xauusd_val, xauusd_svg = "BULLISH", svg_bullish
            usdjpy_val, usdjpy_svg = "BEARISH", svg_bearish
            usdcad_val, usdcad_svg = "BEARISH", svg_bearish
            nas100_val, nas100_svg = "BULLISH", svg_bullish
            us30_val, us30_svg = "BULLISH", svg_bullish
            spx500_val, spx500_svg = "BULLISH", svg_bullish
        else:
            if is_fomc: status_val, status_svg = "VOLATILE", svg_volatile
            else: status_val, status_svg = "RANGES", svg_ranging
            
            eurusd_val = gbpusd_val = xauusd_val = usdjpy_val = usdcad_val = status_val
            eurusd_svg = gbpusd_svg = xauusd_svg = usdjpy_svg = usdcad_svg = status_svg
            nas100_val = us30_val = spx500_val = status_val
            nas100_svg = us30_svg = spx500_svg = status_svg

        # UI FIX 4: Pairs and Indices are now perfectly responsive & horizontal on mobile via Flexbox
        st.subheader("🗺️ Expected Impact on Major Pairs & Gold" if lang == "English" else "🗺️ ප්‍රධාන වෙළඳපොළවල් සඳහා බලපෑම")
        pairs_html = f"""<div class="mobile-scroll-container">
        <div style="min-width: 140px;">{render_custom_metric('EUR/USD', eurusd_val, eurusd_svg)}</div>
        <div style="min-width: 140px;">{render_custom_metric('GBP/USD', gbpusd_val, gbpusd_svg)}</div>
        <div style="min-width: 140px;">{render_custom_metric('XAU/USD (Gold)', xauusd_val, xauusd_svg)}</div>
        <div style="min-width: 140px;">{render_custom_metric('USD/JPY', usdjpy_val, usdjpy_svg)}</div>
        <div style="min-width: 140px;">{render_custom_metric('USD/CAD', usdcad_val, usdcad_svg)}</div>
        </div>"""
        st.markdown(pairs_html, unsafe_allow_html=True)
        
        st.subheader("📊 Expected Impact on Major US Indices" if lang == "English" else "📊 ප්‍රධාන දර්ශක (Indices) සඳහා බලපෑම")
        # Indices rendered horizontally even on mobile
        indices_html = f"""<div class="mobile-scroll-container">
        <div style="min-width: 160px;">{render_custom_metric('NASDAQ (NAS100)', nas100_val, nas100_svg)}</div>
        <div style="min-width: 160px;">{render_custom_metric('US30 (Dow Jones)', us30_val, us30_svg)}</div>
        <div style="min-width: 160px;">{render_custom_metric('S&P 500 (SPX500)', spx500_val, spx500_svg)}</div>
        </div>"""
        st.markdown(indices_html, unsafe_allow_html=True)

    def render_save_button(event_name, score, direction, inputs_dict):
        st.markdown("<br>", unsafe_allow_html=True)
        empty_col, btn_col = st.columns([3, 1.5])
        with btn_col:
            btn_txt = "💾 Save to Journal" if lang == "English" else "💾 ජර්නල් එකට සේව් කරන්න"
            if st.button(btn_txt, key=f"btn_{event_name}"):
                save_to_journal(event_name, score, direction.replace("🚀", "").replace("📉", "").replace("⚖️", "").strip(), inputs_dict)

    sub_report_txt = "📥 Input Sub-Report Data" if lang == "English" else "📥 අනු-වාර්තා දත්ත ඇතුළත් කරන්න"
    live_pred_txt = "🔮 Live Market Prediction" if lang == "English" else "🔮 සජීවී වෙළඳපොළ පුරෝකථනය"
    prev_txt = "Previous Value" if lang == "English" else "පෙර අගය (Previous)"
    fc_txt = "Market Forecast" if lang == "English" else "වෙළඳපොළ අපේක්ෂාව (Forecast)"

    # ----------------- 1. CPI CALCULATOR (GREEN 🟢) -----------------
    if major_news.startswith("🟢 CPI"):
        st.header("🟢 🧮 CPI Leading Data Calculator" if lang == "English" else "🟢 🧮 CPI දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_ppi = ["Consensus වලට වඩා වැඩි", "Neutral", "Consensus වලට වඩා අඩු"] if lang == "සිංහල" else ["Higher than Consensus", "Neutral", "Lower than Consensus"]
        opt_gas = ["ඉහළ යනවා (Inflationary)", "ස්ථාවරයි", "පහළ යනවා (Deflationary)"] if lang == "සිංහල" else ["Rising (Inflationary)", "Stable", "Falling (Deflationary)"]
        opt_nyfed = ["වැඩිවී ඇත", "වෙනස් වී නැත", "අඩුවී ඇත"] if lang == "සිංහල" else ["Increased", "Unchanged", "Decreased"]
        opt_pmi = ["වේගයෙන් ඉහළ යයි (>55)", "Neutral", "පහළ යයි (<50)"] if lang == "සිංහල" else ["Increasing Rapidly (>55)", "Neutral", "Decreasing (<50)"]
        opt_imp = ["ඉහළ යනවා", "ස්ථාවරයි", "පහළ යනවා"] if lang == "සිංහල" else ["Rising", "Stable", "Falling"]
        
        tt_cpi_prev = "Use 'Core CPI m/m' from Forex Factory. Previous is the actual figure from the last month." if lang == "English" else "Forex Factory හි 'Core CPI m/m' (මාසික අගය) භාවිතා කරන්න. Previous යනු පසුගිය මාසයේ සැබෑ අගයයි."
        tt_cpi_fc = "Enter the Market Forecast for 'Core CPI m/m' from Forex Factory." if lang == "English" else "Forex Factory හි 'Core CPI m/m' සඳහා වෙළඳපොළ බලාපොරොත්තු වන Forecast අගය මෙහි යොදන්න."
        tt_ppi = "Check the 'Core PPI m/m' or 'PPI m/m' data released prior to the CPI news." if lang == "English" else "Forex Factory හි CPI නිවුස් එකට පෙර නිකුත් වූ 'Core PPI m/m' හෝ 'PPI m/m' දත්තය දෙස බලන්න."
        tt_gas = "Observe the Crude Oil (WTI) or Gasoline chart on TradingView for the past month's trend." if lang == "English" else "TradingView හි Crude Oil (WTI) හෝ Gasoline චාට් එක පසුගිය මාසය පුරා ඉහළ ගියේද යන්න බලන්න."
        tt_nyfed = "Check if the 'NY Fed 1-Year Inflation Expectations' released early in the month increased." if lang == "English" else "මස මුලදී නිකුත් වූ 'NY Fed 1-Year Inflation' වාර්තාවේ උද්ධමන බලාපොරොත්තුව වැඩිවී ඇත්දැයි බලන්න."
        tt_pmi = "Look at the 'Prices Paid' sub-index in the ISM Services or Manufacturing report." if lang == "English" else "මස මුලදී ආපු ISM Services හෝ Manufacturing නිවුස් එක ඇතුළේ තියෙන 'Prices Paid' අනු-දර්ශකය බලන්න."
        tt_imp = "Check if the 'Import Price Index m/m' on Forex Factory has increased." if lang == "English" else "Forex Factory හි 'Import Price Index m/m' නිවුස් අගය ඉහළ ගොස් තිබේදැයි බලන්න."

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                cpi_previous = st.number_input(f"🟢 📉 {prev_txt} (%):", value=get_num_val(major_news, "cpi_prev", 0.3), step=0.1, format="%.1f", help=tt_cpi_prev)
            with col_fc:
                cpi_forecast = st.number_input(f"🟢 📊 {fc_txt} (%):", value=get_num_val(major_news, "cpi_fc", 0.2), step=0.1, format="%.1f", help=tt_cpi_fc)
            st.markdown("<br>", unsafe_allow_html=True)
            
            l1 = "🟢 1. PPI Trend:" if lang == "English" else "🟢 1. PPI ප්‍රවණතාව:"
            l2 = "🟢 2. Gasoline / Energy Prices:" if lang == "English" else "🟢 2. ඉන්ධන / බලශක්ති මිල:"
            l3 = "🟢 3. NY Fed 1-Yr Inflation Expectations:" if lang == "English" else "🟢 3. NY Fed උද්ධමන අපේක්ෂාව:"
            l4 = "🟢 4. ISM Services/Mfg Prices Paid:" if lang == "English" else "🟢 4. ISM Prices Paid අගය:"
            l5 = "🟢 5. Import Prices:" if lang == "English" else "🟢 5. ආනයන මිල දර්ශකය:"

            ppi_input = st.selectbox(l1, opt_ppi, index=get_idx(major_news, "ppi", opt_ppi), help=tt_ppi)
            gasoline = st.selectbox(l2, opt_gas, index=get_idx(major_news, "gas", opt_gas), help=tt_gas)
            ny_fed = st.selectbox(l3, opt_nyfed, index=get_idx(major_news, "nyfed", opt_nyfed), help=tt_nyfed)
            pmi_prices = st.selectbox(l4, opt_pmi, index=get_idx(major_news, "pmi", opt_pmi), help=tt_pmi)
            import_prices = st.selectbox(l5, opt_imp, index=get_idx(major_news, "imp", opt_imp), help=tt_imp)
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader(live_pred_txt)
            score = 0
            if ppi_input == opt_ppi[0]: score += 25
            elif ppi_input == opt_ppi[1]: score += 12.5
            if gasoline == opt_gas[0]: score += 20
            elif gasoline == opt_gas[1]: score += 10
            if ny_fed == opt_nyfed[0]: score += 20
            elif ny_fed == opt_nyfed[1]: score += 10
            if pmi_prices == opt_pmi[0]: score += 20
            elif pmi_prices == opt_pmi[1]: score += 10
            if import_prices == opt_imp[0]: score += 15
            elif import_prices == opt_imp[1]: score += 7.5
            
            st.plotly_chart(create_gauge_chart(score), use_container_width=True)
            dir_txt = "Predicted DXY Direction:" if lang == "English" else "අපේක්ෂිත DXY දිශාව:"
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### {dir_txt} <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)

            inputs_dict = {"cpi_prev": cpi_previous, "cpi_fc": cpi_forecast, "ppi": ppi_input, "gas": gasoline, "nyfed": ny_fed, "pmi": pmi_prices, "imp": import_prices}
            render_save_button(major_news, score, direction, inputs_dict)
            
            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.3 
            exp_value = cpi_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > cpi_previous:
                    dev_signal = "🚀 Hotter & Accelerating (Strong Bullish)"
                    dev_desc = "Actual inflation exceeds both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY." if lang == "English" else "උද්ධමනය බලාපොරොත්තු වූවාටත් වඩා ඉහළ ගොස් ඇත. මෙය DXY එක ඉහළ යාමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Hotter BUT Cooling (Fakeout Warning)"
                    dev_desc = "Inflation beat expectations but remains below the previous month's level. Exercise caution as this may lead to short-term volatility." if lang == "English" else "උද්ධමනය අපේක්ෂාවන්ට වඩා ඉහළ ගියත් පෙර මාසයට වඩා අඩු වී ඇත. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < cpi_previous:
                    dev_signal = "📉 Cooler & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise in inflation figures. This is a primary bearish catalyst for the DXY." if lang == "English" else "උද්ධමනය ප්‍රබල ලෙස පහත වැටී ඇත. මෙය DXY එක කඩා වැටීමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Cooler BUT Sticky (Fakeout Warning)"
                    dev_desc = "Inflation is lower than forecast but shows stickiness relative to the previous month. Potential for a 'fakeout' market reversal." if lang == "English" else "උද්ධමනය අඩුවී ඇතත් පෙර මාසයට සාපේක්ෂව ඒ මට්ටමේම පවතී. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Inflation figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior." if lang == "English" else "දත්තයන් වෙළඳපොළ බලාපොරොත්තු වූ මට්ටමේම පවතී. Market එක එකම සීමාවක (Range) ගමන් කළ හැක."

            lower_bound = exp_value - 0.05
            upper_bound = exp_value + 0.05
            
            p_lbl = "Previous" if lang == "English" else "Previous (පෙර)"
            f_lbl = "Forecast" if lang == "English" else "Forecast (අපේක්ෂාව)"
            r_lbl = "AI Expected Range" if lang == "English" else "AI Expected Range (අනුමානය)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">🤖 <b>AI Advanced Forecast Radar</b></div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{p_lbl}</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{cpi_previous:.1f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{f_lbl}</div><div style="font-size: 22px; font-weight: bold; color: white;">{cpi_forecast:.1f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{r_lbl}</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">{dev_signal}</div><div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">{dev_desc}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 2. NFP CALCULATOR (ORANGE 🟠) -----------------
    elif major_news.startswith("🟠 NFP"):
        st.header("🟠 💼 NFP Leading Data Calculator" if lang == "English" else "🟠 💼 NFP දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_adp = ["ඉතා ඉහළයි (Strong Beat)", "Neutral / සාමාන්‍යයි", "ඉතා අඩුයි (Big Miss)"] if lang == "සිංහල" else ["Strong Beat", "Neutral / As Expected", "Big Miss"]
        opt_ism = ["වර්ධනය වේ (>50)", "Neutral", "අඩු වේ (<50)"] if lang == "සිංහල" else ["Expanding (>50)", "Neutral", "Contracting (<50)"]
        opt_jolts = ["ඉහළ යනවා (ප්‍රබල ඉල්ලුම)", "Neutral", "පහළ යනවා (අඩු ඉල්ලුම)"] if lang == "සිංහල" else ["Increasing (Strong Demand)", "Neutral", "Decreasing (Weak Demand)"]
        opt_jobless = ["අඛණ්ඩව අඩුයි (<200k)", "Neutral", "වේගයෙන් ඉහළ යයි (>250k)"] if lang == "සිංහල" else ["Consistently Low (<200k)", "Neutral", "Rising Rapidly (>250k)"]
        opt_chal = ["අඩු රැකියා කප්පාදුවක්", "සාමාන්‍යයි", "වැඩි රැකියා කප්පාදුවක්"] if lang == "සිංහල" else ["Low Layoffs", "Average", "High Layoffs"]
        
        tt_nfp_prev = "Use 'Non-Farm Employment Change' from Forex Factory. (e.g., For 200K, enter 200)." if lang == "English" else "Forex Factory හි 'Non-Farm Employment Change' අගය භාවිතා කරන්න. (උදා: 200K නම් 200 ලෙස පමණක් යොදන්න)."
        tt_nfp_fc = "Enter the Market Forecast for 'Non-Farm Employment Change'." if lang == "English" else "Forex Factory හි 'Non-Farm Employment Change' සඳහා වෙළඳපොළ බලාපොරොත්තු වන Forecast අගය මෙහි යොදන්න."
        tt_adp = "Check the 'ADP Non-Farm Employment Change' released on Wednesday of the NFP week." if lang == "English" else "NFP සතියේ බදාදා නිකුත් වන 'ADP Non-Farm Employment Change' දත්තය බලන්න."
        tt_ism = "Look at the 'Employment' sub-index in the ISM Services PMI report." if lang == "English" else "මස මුලදී නිකුත් වන ISM Services PMI නිවුස් එක ඇතුළේ තියෙන 'Employment' අනු-දර්ශකය බලන්න."
        tt_jolts = "Check if job vacancies increased in the recently released 'JOLTs Job Openings' report." if lang == "English" else "මෑතකදී නිකුත් වූ 'JOLTs Job Openings' වාර්තාවේ රැකියා පුරප්පාඩු වැඩි වී ඇත්දැයි බලන්න."
        tt_jobless = "Observe the 4-week average of 'Initial Jobless Claims'. (Is it consistently low?)." if lang == "English" else "පසුගිය මාසයේ සතිපතා නිකුත් වූ 'Unemployment Claims' වල සාමාන්‍යය 200k-250k අතර කෙසේ තිබුණේදැයි බලන්න."
        tt_chal = "Check the 'Challenger Job Cuts' report released on Thursday of the NFP week." if lang == "English" else "NFP සතියේ බ්‍රහස්පතින්දා නිකුත් වන 'Challenger Job Cuts' වාර්තාව දෙස බලන්න."

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                nfp_previous = st.number_input(f"🟠 📉 {prev_txt} (k):", value=int(get_num_val(major_news, "nfp_prev", 200)), step=10, format="%d", help=tt_nfp_prev)
            with col_fc:
                nfp_forecast = st.number_input(f"🟠 📊 {fc_txt} (k):", value=int(get_num_val(major_news, "nfp_fc", 180)), step=10, format="%d", help=tt_nfp_fc)
            st.markdown("<br>", unsafe_allow_html=True)

            l1 = "🟠 1. ADP Employment Change:" if lang == "English" else "🟠 1. ADP රැකියා දත්තය:"
            l2 = "🟠 2. ISM Services Employment:" if lang == "English" else "🟠 2. ISM සේවා අංශයේ රැකියා:"
            l3 = "🟠 3. JOLTs Job Openings:" if lang == "English" else "🟠 3. JOLTs රැකියා පුරප්පාඩු:"
            l4 = "🟠 4. Initial Jobless Claims:" if lang == "English" else "🟠 4. සතිපතා රැකියා විරහිත දත්තය:"
            l5 = "🟠 5. Challenger Job Cuts:" if lang == "English" else "🟠 5. ආයතනික රැකියා කප්පාදුව:"

            adp_input = st.selectbox(l1, opt_adp, index=get_idx(major_news, "adp", opt_adp), help=tt_adp)
            ism_services = st.selectbox(l2, opt_ism, index=get_idx(major_news, "ism", opt_ism), help=tt_ism)
            jolts = st.selectbox(l3, opt_jolts, index=get_idx(major_news, "jolts", opt_jolts), help=tt_jolts)
            jobless = st.selectbox(l4, opt_jobless, index=get_idx(major_news, "jobless", opt_jobless), help=tt_jobless)
            challenger = st.selectbox(l5, opt_chal, index=get_idx(major_news, "chal", opt_chal), help=tt_chal)
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader(live_pred_txt)
            score = 0
            if adp_input == opt_adp[0]: score += 20
            elif adp_input == opt_adp[1]: score += 10
            if ism_services == opt_ism[0]: score += 25
            elif ism_services == opt_ism[1]: score += 12.5
            if jolts == opt_jolts[0]: score += 20
            elif jolts == opt_jolts[1]: score += 10
            if jobless == opt_jobless[0]: score += 20
            elif jobless == opt_jobless[1]: score += 10
            if challenger == opt_chal[0]: score += 15
            elif challenger == opt_chal[1]: score += 7.5
            
            st.plotly_chart(create_gauge_chart(score), use_container_width=True)
            dir_txt = "Predicted DXY Direction:" if lang == "English" else "අපේක්ෂිත DXY දිශාව:"
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### {dir_txt} <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)
            
            inputs_dict = {"nfp_prev": nfp_previous, "nfp_fc": nfp_forecast, "adp": adp_input, "ism": ism_services, "jolts": jolts, "jobless": jobless, "chal": challenger}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 50.0 
            exp_value = nfp_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > nfp_previous:
                    dev_signal = "🚀 Strong Beat & Accelerating (Strong Bullish)"
                    dev_desc = "Employment data is projected to exceed both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY." if lang == "English" else "රැකියා දත්ත බලාපොරොත්තු වූවාටත් වඩා ඉහළ ගොස් ඇත. මෙය DXY එක ඉහළ යාමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Beat BUT Decelerating (Fakeout Warning)"
                    dev_desc = "Data is projected to beat expectations but remains below previous levels. Exercise caution as this may lead to short-term volatility." if lang == "English" else "අපේක්ෂාවන්ට වඩා ඉහළ ගියත් පෙර මාසයට වඩා අඩු වී ඇත. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < nfp_previous:
                    dev_signal = "📉 Big Miss & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise projected. Figures fall below both forecasts and previous data, acting as a primary bearish catalyst for the DXY." if lang == "English" else "රැකියා දත්ත ප්‍රබල ලෙස පහත වැටී ඇත. මෙය DXY එක කඩා වැටීමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Miss BUT Sticky (Fakeout Warning)"
                    dev_desc = "Data misses forecasts but shows stickiness relative to previous figures. Potential for a 'fakeout' market reversal." if lang == "English" else "දත්ත අඩුවී ඇතත් පෙර මාසයට සාපේක්ෂව ඒ මට්ටමේම පවතී. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Employment figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior." if lang == "English" else "දත්තයන් වෙළඳපොළ බලාපොරොත්තු වූ මට්ටමේම පවතී. Market එක එකම සීමාවක (Range) ගමන් කළ හැක."

            lower_bound = exp_value - 10
            upper_bound = exp_value + 10
            
            p_lbl = "Previous" if lang == "English" else "Previous (පෙර)"
            f_lbl = "Forecast" if lang == "English" else "Forecast (අපේක්ෂාව)"
            r_lbl = "AI Expected Range" if lang == "English" else "AI Expected Range (අනුමානය)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">🤖 <b>AI Advanced Forecast Radar</b></div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{p_lbl}</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{nfp_previous}k</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{f_lbl}</div><div style="font-size: 22px; font-weight: bold; color: white;">{nfp_forecast}k</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{r_lbl}</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.0f}k - {upper_bound:.0f}k</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">{dev_signal}</div><div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">{dev_desc}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 3. CORE PCE CALCULATOR (PURPLE 🟣) -----------------
    elif major_news.startswith("🟣 Core"):
        st.header("🟣 🛒 Core PCE Leading Data Calculator" if lang == "English" else "🟣 🛒 Core PCE දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_cpi = ["අපේක්ෂිත අගයට වඩා වැඩි", "Neutral", "අපේක්ෂිත අගයට වඩා අඩු"] if lang == "සිංහල" else ["Hotter than Expected", "Neutral", "Cooler than Expected"]
        opt_ppi = ["අපේක්ෂිත අගයට වඩා වැඩි", "Neutral", "අපේක්ෂිත අගයට වඩා අඩු"] if lang == "සිංහල" else ["Hotter than Expected", "Neutral", "Cooler than Expected"]
        opt_hr = ["ඉතා වේගයෙන් වැඩිවේ", "ස්ථාවරයි", "පහළ යමින් පවතී"] if lang == "සිංහල" else ["Rising Faster", "Stable", "Cooling Down"]
        opt_ret = ["ප්‍රබලයි (වැඩි පාරිභෝගික වියදම්)", "Neutral", "දුර්වලයි (අඩු පාරිභෝගික වියදම්)"] if lang == "සිංහල" else ["Strong (High Spending)", "Neutral", "Weak (Low Spending)"]

        tt_pce_prev = "Use 'Core PCE Price Index m/m' from Forex Factory. Previous is the actual figure from the last month." if lang == "English" else "Forex Factory හි 'Core PCE Price Index m/m' (මාසික අගය) භාවිතා කරන්න. Previous යනු පසුගිය මාසයේ සැබෑ අගයයි."
        tt_pce_fc = "Enter the Market Forecast for 'Core PCE m/m'." if lang == "English" else "Forex Factory හි 'Core PCE m/m' සඳහා වෙළඳපොළ බලාපොරොත්තු වන Forecast අගය මෙහි යොදන්න."
        tt_cpi_rc = "Check the 'Core CPI m/m' released earlier for the same month." if lang == "English" else "PCE නිවුස් එකට පෙර නිකුත් වූ එම මාසයටම අදාළ 'Core CPI m/m' දත්තය දෙස බලන්න."
        tt_ppi_rc = "Check the 'Core PPI m/m' released earlier for the same month." if lang == "English" else "PCE නිවුස් එකට පෙර නිකුත් වූ එම මාසයටම අදාළ 'Core PPI m/m' දත්තය දෙස බලන්න."
        tt_hr = "Check the wage growth pace in the 'Average Hourly Earnings m/m' released on NFP day." if lang == "English" else "NFP දින නිකුත් වූ 'Average Hourly Earnings m/m' හි පඩි වැඩිවීමේ වේගය බලන්න."
        tt_ret = "Check if 'Retail Sales m/m' or 'Personal Income m/m' have increased." if lang == "English" else "Forex Factory හි 'Retail Sales m/m' හෝ 'Personal Income m/m' දත්තයන් ඉහළ ගොස් ඇත්දැයි බලන්න."

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                pce_previous = st.number_input(f"🟣 📉 {prev_txt} (%):", value=get_num_val(major_news, "pce_prev", 0.3), step=0.1, format="%.1f", help=tt_pce_prev)
            with col_fc:
                pce_forecast = st.number_input(f"🟣 📊 {fc_txt} (%):", value=get_num_val(major_news, "pce_fc", 0.2), step=0.1, format="%.1f", help=tt_pce_fc)
            st.markdown("<br>", unsafe_allow_html=True)

            l1 = "🟣 1. Recent Core CPI Release:" if lang == "English" else "🟣 1. මෑතකදී ආපු Core CPI අගය:"
            l2 = "🟣 2. Recent Core PPI Release:" if lang == "English" else "🟣 2. මෑතකදී ආපු Core PPI අගය:"
            l3 = "🟣 3. Average Hourly Earnings:" if lang == "English" else "🟣 3. පැයකට ලබන සාමාන්‍ය ආදායම:"
            l4 = "🟣 4. Retail Sales / Personal Income:" if lang == "English" else "🟣 4. සිල්ලර වෙළඳාම / පුද්ගලික ආදායම:"

            cpi_input = st.selectbox(l1, opt_cpi, index=get_idx(major_news, "cpi", opt_cpi), help=tt_cpi_rc)
            ppi_input = st.selectbox(l2, opt_ppi, index=get_idx(major_news, "ppi", opt_ppi), help=tt_ppi_rc)
            hourly_earnings = st.selectbox(l3, opt_hr, index=get_idx(major_news, "hr", opt_hr), help=tt_hr)
            retail_sales = st.selectbox(l4, opt_ret, index=get_idx(major_news, "ret", opt_ret), help=tt_ret)
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader(live_pred_txt)
            score = 0
            if cpi_input == opt_cpi[0]: score += 35
            elif cpi_input == opt_cpi[1]: score += 17.5
            if ppi_input == opt_ppi[0]: score += 25
            elif ppi_input == opt_ppi[1]: score += 12.5
            if hourly_earnings == opt_hr[0]: score += 20
            elif hourly_earnings == opt_hr[1]: score += 10
            if retail_sales == opt_ret[0]: score += 20
            elif retail_sales == opt_ret[1]: score += 10
            
            st.plotly_chart(create_gauge_chart(score), use_container_width=True)
            dir_txt = "Predicted DXY Direction:" if lang == "English" else "අපේක්ෂිත DXY දිශාව:"
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### {dir_txt} <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)

            inputs_dict = {"pce_prev": pce_previous, "pce_fc": pce_forecast, "cpi": cpi_input, "ppi": ppi_input, "hr": hourly_earnings, "ret": retail_sales}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.2 
            exp_value = pce_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > pce_previous:
                    dev_signal = "🚀 Hotter & Accelerating (Strong Bullish)"
                    dev_desc = "Actual inflation exceeds both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY." if lang == "English" else "උද්ධමනය බලාපොරොත්තු වූවාටත් වඩා ඉහළ ගොස් ඇත. මෙය DXY එක ඉහළ යාමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Hotter BUT Cooling (Fakeout Warning)"
                    dev_desc = "Inflation beat expectations but remains below the previous month's level. Exercise caution as this may lead to short-term volatility." if lang == "English" else "උද්ධමනය අපේක්ෂාවන්ට වඩා ඉහළ ගියත් පෙර මාසයට වඩා අඩු වී ඇත. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < pce_previous:
                    dev_signal = "📉 Cooler & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise in inflation figures. This is a primary bearish catalyst for the DXY." if lang == "English" else "උද්ධමනය ප්‍රබල ලෙස පහත වැටී ඇත. මෙය DXY එක කඩා වැටීමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Cooler BUT Sticky (Fakeout Warning)"
                    dev_desc = "Inflation is lower than forecast but shows stickiness relative to the previous month. Potential for a 'fakeout' market reversal." if lang == "English" else "උද්ධමනය අඩුවී ඇතත් පෙර මාසයට සාපේක්ෂව ඒ මට්ටමේම පවතී. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Inflation figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior." if lang == "English" else "දත්තයන් වෙළඳපොළ බලාපොරොත්තු වූ මට්ටමේම පවතී. Market එක එකම සීමාවක (Range) ගමන් කළ හැක."

            lower_bound = exp_value - 0.05
            upper_bound = exp_value + 0.05
            
            p_lbl = "Previous" if lang == "English" else "Previous (පෙර)"
            f_lbl = "Forecast" if lang == "English" else "Forecast (අපේක්ෂාව)"
            r_lbl = "AI Expected Range" if lang == "English" else "AI Expected Range (අනුමානය)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">🤖 <b>AI Advanced Forecast Radar</b></div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{p_lbl}</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{pce_previous:.1f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{f_lbl}</div><div style="font-size: 22px; font-weight: bold; color: white;">{pce_forecast:.1f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{r_lbl}</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">{dev_signal}</div><div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">{dev_desc}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 4. ADVANCE GDP CALCULATOR (BLUE 🔵) -----------------
    elif major_news.startswith("🔵 Advance"):
        st.header("🔵 🏭 Advance GDP Leading Data Calculator" if lang == "English" else "🔵 🏭 Advance GDP දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_atl = ["ඉහළ අගයක් ගනී (>2.5%)", "Neutral", "පහළ අගයක් ගනී (<1.0%)"] if lang == "සිංහල" else ["Tracking High (>2.5%)", "Neutral", "Tracking Low (<1.0%)"]
        opt_ret = ["ප්‍රබල ධනාත්මක එකක්", "Neutral", "සෘණාත්මක එකක්"] if lang == "සිංහල" else ["Strongly Positive", "Neutral", "Negative"]
        opt_trade = ["හිඟය අඩු වෙනවා (Good)", "Neutral", "හිඟය වැඩි වෙනවා (Bad)"] if lang == "සිංහල" else ["Deficit Shrinking (Good)", "Neutral", "Deficit Widening (Bad)"]
        opt_pmi = ["වර්ධනය වේ (>50)", "Neutral (~50)", "අඩු වේ (<50)"] if lang == "සිංහල" else ["Expanding (>50)", "Neutral (~50)", "Contracting (<50)"]
        opt_dur = ["ඉහළ යනවා", "සාමාන්‍යයි", "පහළ යනවා"] if lang == "සිංහල" else ["Rising", "Neutral", "Falling"]

        tt_gdp_prev = "Use 'Advance GDP q/q' from Forex Factory. Previous is the final figure from the last quarter." if lang == "English" else "Forex Factory හි 'Advance GDP q/q' (කාර්තුමය අගය) භාවිතා කරන්න. Previous යනු පසුගිය කාර්තුවේ අවසන් අගයයි."
        tt_gdp_fc = "Enter the Market Forecast for 'Advance GDP q/q'." if lang == "English" else "Forex Factory හි 'Advance GDP q/q' සඳහා වෙළඳපොළ බලාපොරොත්තු වන Forecast අගය මෙහි යොදන්න."
        tt_atl = "Check the 'GDPNow' Live Tracker on the official Atlanta Fed website." if lang == "English" else "Atlanta Fed නිල වෙබ් අඩවියේ ඇති 'GDPNow' Live Tracker අගය බලන්න."
        tt_ret_q = "Observe the average trend of 'Retail Sales m/m' over the past 3 months." if lang == "English" else "පසුගිය මාස 3 තුළ නිකුත් වූ 'Retail Sales m/m' වල සාමාන්‍ය හැසිරීම බලන්න."
        tt_trade = "Check if the export-import gap has narrowed via the 'Trade Balance' news." if lang == "English" else "'Trade Balance' නිවුස් හරහා අපනයන සහ ආනයන පරතරය අඩු වී ඇත්දැයි බලන්න."
        tt_pmi_c = "Look at the average of ISM Manufacturing and Services PMIs over the past 3 months." if lang == "English" else "පසුගිය මාස 3 තුළ ISM Manufacturing සහ Services PMI වල සාමාන්‍ය තත්ත්වය බලන්න."
        tt_dur = "Check the recently released 'Core Durable Goods Orders m/m' data." if lang == "English" else "මෑතකදී නිකුත් වූ 'Core Durable Goods Orders m/m' දත්තය දෙස බලන්න."

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                gdp_previous = st.number_input(f"🔵 📉 {prev_txt} (%):", value=get_num_val(major_news, "gdp_prev", 2.1), step=0.1, format="%.1f", help=tt_gdp_prev)
            with col_fc:
                gdp_forecast = st.number_input(f"🔵 📊 {fc_txt} (%):", value=get_num_val(major_news, "gdp_fc", 1.8), step=0.1, format="%.1f", help=tt_gdp_fc)
            st.markdown("<br>", unsafe_allow_html=True)

            l1 = "🔵 1. Atlanta Fed GDPNow Tracker:" if lang == "English" else "🔵 1. Atlanta Fed GDPNow අගය:"
            l2 = "🔵 2. Retail Sales (Quarterly Average):" if lang == "English" else "🔵 2. සිල්ලර වෙළඳාම (කාර්තුමය):"
            l3 = "🔵 3. Trade Balance (Net Exports):" if lang == "English" else "🔵 3. වෙළඳ ශේෂය (Trade Balance):"
            l4 = "🔵 4. ISM Composite PMI:" if lang == "English" else "🔵 4. ISM Composite PMI අගය:"
            l5 = "🔵 5. Durable Goods Orders:" if lang == "English" else "🔵 5. කල්පවතින භාණ්ඩ ඇණවුම්:"

            atlanta_fed = st.selectbox(l1, opt_atl, index=get_idx(major_news, "atl", opt_atl), help=tt_atl)
            retail_input = st.selectbox(l2, opt_ret, index=get_idx(major_news, "ret", opt_ret), help=tt_ret_q)
            trade_balance = st.selectbox(l3, opt_trade, index=get_idx(major_news, "trade", opt_trade), help=tt_trade)
            pmi_input = st.selectbox(l4, opt_pmi, index=get_idx(major_news, "pmi", opt_pmi), help=tt_pmi_c)
            durable_goods = st.selectbox(l5, opt_dur, index=get_idx(major_news, "dur", opt_dur), help=tt_dur)
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader(live_pred_txt)
            score = 0
            if atlanta_fed == opt_atl[0]: score += 25
            elif atlanta_fed == opt_atl[1]: score += 12.5
            if retail_input == opt_ret[0]: score += 30
            elif retail_input == opt_ret[1]: score += 15
            if trade_balance == opt_trade[0]: score += 10
            elif trade_balance == opt_trade[1]: score += 5
            if pmi_input == opt_pmi[0]: score += 20
            elif pmi_input == opt_pmi[1]: score += 10
            if durable_goods == opt_dur[0]: score += 15
            elif durable_goods == opt_dur[1]: score += 7.5
            
            st.plotly_chart(create_gauge_chart(score), use_container_width=True)
            dir_txt = "Predicted DXY Direction:" if lang == "English" else "අපේක්ෂිත DXY දිශාව:"
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### {dir_txt} <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)

            inputs_dict = {"gdp_prev": gdp_previous, "gdp_fc": gdp_forecast, "atl": atlanta_fed, "ret": retail_input, "trade": trade_balance, "pmi": pmi_input, "dur": durable_goods}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.5 
            exp_value = gdp_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > gdp_previous:
                    dev_signal = "🚀 Stronger & Accelerating (Strong Bullish)"
                    dev_desc = "Economic growth exceeds both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY." if lang == "English" else "ආර්ථික වර්ධනය බලාපොරොත්තු වූවාටත් වඩා ඉහළ ගොස් ඇත. මෙය DXY එක ඉහළ යාමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Stronger BUT Cooling (Fakeout Warning)"
                    dev_desc = "Growth beat expectations but remains below the previous quarter's level. Exercise caution as this may lead to short-term volatility." if lang == "English" else "අපේක්ෂාවන්ට වඩා ඉහළ ගියත් පෙර කාර්තුවට වඩා අඩු වී ඇත. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < gdp_previous:
                    dev_signal = "📉 Weaker & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise in economic growth. This is a primary bearish catalyst for the DXY." if lang == "English" else "ආර්ථික වර්ධනය ප්‍රබල ලෙස පහත වැටී ඇත. මෙය DXY එක කඩා වැටීමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Weaker BUT Sticky (Fakeout Warning)"
                    dev_desc = "Growth is lower than forecast but shows stickiness relative to the previous quarter. Potential for a 'fakeout' market reversal." if lang == "English" else "වර්ධනය අඩුවී ඇතත් පෙර කාර්තුවට සාපේක්ෂව ඒ මට්ටමේම පවතී. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Growth figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior." if lang == "English" else "දත්තයන් වෙළඳපොළ බලාපොරොත්තු වූ මට්ටමේම පවතී. Market එක එකම සීමාවක (Range) ගමන් කළ හැක."

            lower_bound = exp_value - 0.1
            upper_bound = exp_value + 0.1
            
            p_lbl = "Previous" if lang == "English" else "Previous (පෙර)"
            f_lbl = "Forecast" if lang == "English" else "Forecast (අපේක්ෂාව)"
            r_lbl = "AI Expected Range" if lang == "English" else "AI Expected Range (අනුමානය)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">🤖 <b>AI Advanced Forecast Radar</b></div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{p_lbl}</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{gdp_previous:.1f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{f_lbl}</div><div style="font-size: 22px; font-weight: bold; color: white;">{gdp_forecast:.1f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{r_lbl}</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">{dev_signal}</div><div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">{dev_desc}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 5. FOMC RATE DECISION CALCULATOR (RED 🔴) -----------------
    elif major_news.startswith("🔴 FOMC"):
        st.header("🔴 🦅 FOMC Rate Decision & Statement" if lang == "English" else "🔴 🦅 FOMC පොලී අනුපාත තීරණය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_fed = ["Hawk පැත්තට බරයි (Hike/Hold)", "මිශ්‍ර තත්ත්වයක්", "Dove පැත්තට බරයි (Cut)"] if lang == "සිංහල" else ["Pricing Hawk (Hike/Hold)", "Mixed", "Pricing Dove (Cut)"]
        opt_inf = ["ස්ථාවරයි / ඉහළ යයි", "Neutral", "වේගයෙන් පහළ වැටේ"] if lang == "සිංහල" else ["Sticky / Rising", "Neutral", "Falling Rapidly"]
        opt_lab = ["ප්‍රබලයි (වැඩි රැකියා ප්‍රමාණයක්)", "Neutral", "දුර්වලයි (අඩු රැකියා ප්‍රමාණයක්)"] if lang == "සිංහල" else ["Tight (Strong Jobs)", "Neutral", "Cooling (Weak Jobs)"]
        opt_speak = ["Hawkish දැඩි ප්‍රකාශ", "Neutral", "Dovish ලිහිල් ප්‍රකාශ"] if lang == "සිංහල" else ["Hawkish Rhetoric", "Neutral", "Dovish Rhetoric"]
        opt_fin = ["ලිහිල් (මුදල් සැපයුම වැඩියි)", "Neutral", "තදයි (මුදල් සැපයුම අඩුයි)"] if lang == "සිංහල" else ["Loose (Requires Tightening)", "Neutral", "Tight (Requires Easing)"]

        tt_fomc_prev = "Use 'Federal Funds Rate' from Forex Factory. Previous is the currently existing interest rate." if lang == "English" else "Forex Factory හි 'Federal Funds Rate' අගය භාවිතා කරන්න. Previous යනු දැනට පවතින පොලී අනුපාතයයි."
        tt_fomc_fc = "Enter the Market Forecast for the 'Federal Funds Rate'." if lang == "English" else "Forex Factory හි 'Federal Funds Rate' සඳහා වෙළඳපොළ බලාපොරොත්තු වන Forecast අගය මෙහි යොදන්න."
        tt_fed = "Check the probability expected by investors via the 'FedWatch Tool' on the CME Group website." if lang == "English" else "CME Group වෙබ් අඩවියේ 'FedWatch Tool' හරහා ආයෝජකයින් බලාපොරොත්තු වන ප්‍රතිශතය බලන්න."
        tt_inf = "Observe the direction of US Core CPI and Core PCE inflation over the past 2-3 months." if lang == "English" else "පසුගිය මාස 2-3 තුළ ඇමෙරිකානු Core CPI සහ Core PCE උද්ධමනය ගමන් කළ දිශාව බලන්න."
        tt_lab = "Consider the strength of recently released NFP and Jobless Claims data." if lang == "English" else "මෑතකදී නිකුත් වූ NFP සහ Jobless Claims දත්ත වල ශක්තිමත්භාවය සලකා බලන්න."
        tt_speak = "Determine if recent speeches by Fed officials (Powell, Waller, etc.) were Hawkish or Dovish." if lang == "English" else "Fed නිලධාරීන් (Powell, Waller ආදීන්) මෑතකදී කළ කතාබහ Hawkish ද Dovish ද යන්න බලන්න."
        tt_fin = "Check the market money supply via indices like the Chicago Fed NFCI." if lang == "English" else "Chicago Fed NFCI වැනි දර්ශක හරහා වෙළඳපොළේ මුදල් සැපයුම කෙසේදැයි බලන්න."

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                pr_txt = "📉 Previous Rate" if lang == "English" else "📉 පෙර අනුපාතය"
                fomc_previous = st.number_input(f"🔴 {pr_txt} (%):", value=get_num_val(major_news, "fomc_prev", 5.50), step=0.25, format="%.2f", help=tt_fomc_prev)
            with col_fc:
                fomc_forecast = st.number_input(f"🔴 📊 {fc_txt} (%):", value=get_num_val(major_news, "fomc_fc", 5.25), step=0.25, format="%.2f", help=tt_fomc_fc)
            st.markdown("<br>", unsafe_allow_html=True)

            l1 = "🔴 1. CME FedWatch Probability:" if lang == "English" else "🔴 1. CME FedWatch අනුපාතය:"
            l2 = "🔴 2. Recent Core PCE/CPI Trend:" if lang == "English" else "🔴 2. මෑතකාලීන Core PCE/CPI ගමන:"
            l3 = "🔴 3. Recent Labor Market (NFP/JOLTs):" if lang == "English" else "🔴 3. රැකියා වෙළඳපොළේ තත්ත්වය:"
            l4 = "🔴 4. Recent Fedspeak / Dot Plot:" if lang == "English" else "🔴 4. Fed නිලධාරීන්ගේ ප්‍රකාශ/Dot Plot:"
            l5 = "🔴 5. Financial Conditions Index:" if lang == "English" else "🔴 5. මූල්‍ය තත්ත්ව දර්ශකය (FCI):"

            fedwatch = st.selectbox(l1, opt_fed, index=get_idx(major_news, "fed", opt_fed), help=tt_fed)
            inflation = st.selectbox(l2, opt_inf, index=get_idx(major_news, "inf", opt_inf), help=tt_inf)
            labor = st.selectbox(l3, opt_lab, index=get_idx(major_news, "lab", opt_lab), help=tt_lab)
            fedspeak = st.selectbox(l4, opt_speak, index=get_idx(major_news, "speak", opt_speak), help=tt_speak)
            fin_conditions = st.selectbox(l5, opt_fin, index=get_idx(major_news, "fin", opt_fin), help=tt_fin)
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader(live_pred_txt)
            score = 0
            if fedwatch == opt_fed[0]: score += 30
            elif fedwatch == opt_fed[1]: score += 15
            if inflation == opt_inf[0]: score += 25
            elif inflation == opt_inf[1]: score += 12.5
            if labor == opt_lab[0]: score += 15
            elif labor == opt_lab[1]: score += 7.5
            if fedspeak == opt_speak[0]: score += 15
            elif fedspeak == opt_speak[1]: score += 7.5
            if fin_conditions == opt_fin[0]: score += 15
            elif fin_conditions == opt_fin[1]: score += 7.5
            
            st.plotly_chart(create_gauge_chart(score), use_container_width=True)
            dir_txt = "Predicted DXY Direction:" if lang == "English" else "අපේක්ෂිත DXY දිශාව:"
            direction, css_class = ("HAWKISH (BULLISH DXY) 🚀", "bullish-text") if score >= 60 else ("DOVISH (BEARISH DXY) 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### {dir_txt} <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score, is_fomc=True)

            inputs_dict = {"fomc_prev": fomc_previous, "fomc_fc": fomc_forecast, "fed": fedwatch, "inf": inflation, "lab": labor, "speak": fedspeak, "fin": fin_conditions}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.25 
            exp_value = fomc_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value >= fomc_previous:
                    dev_signal = "🦅 Hawkish Hike / Hold (Strong Bullish)"
                    dev_desc = "Rate projections exceed or maintain previous high levels. This represents a strong bullish catalyst for the DXY." if lang == "English" else "පොලී අනුපාත ඉහළ අගයක පවත්වා ගනී. මෙය DXY එක ඉහළ යාමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Hawkish rhetoric BUT Rate Capped (Fakeout)"
                    dev_desc = "Rhetoric is hawkish but actual rate projection remains below previous highs. Watch for short-term volatility." if lang == "English" else "ප්‍රකාශ දැඩි වුවත් පොලී අනුපාත වැඩි කර නොමැත. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < fomc_previous:
                    dev_signal = "🕊️ Dovish Cut & Accelerating (Strong Bearish)"
                    dev_desc = "Aggressive rate cuts projected compared to previous levels. This is a primary bearish catalyst for the DXY." if lang == "English" else "පොලී අනුපාත ප්‍රබල ලෙස කපා හැර ඇත. මෙය DXY එක කඩා වැටීමට ප්‍රබල හේතුවකි."
                else:
                    dev_signal = "⚖️ Dovish rhetoric BUT Sticky Rates (Fakeout)"
                    dev_desc = "Rhetoric is dovish but actual rate projections hold higher than expected. Potential for a 'fakeout' market reversal." if lang == "English" else "ප්‍රකාශ ලිහිල් වුවත් පොලී අනුපාත අඩු කර නොමැත. ක්ෂණික රැවටිලි (Fakeouts) ඇතිවිය හැක."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Market Pricing (Neutral)"
                dev_desc = "Rate decisions and rhetoric are aligned with market expectations. Anticipate range-bound trading behavior." if lang == "English" else "තීරණයන් වෙළඳපොළ බලාපොරොත්තු වූ මට්ටමේම පවතී. Market එක එකම සීමාවක (Range) ගමන් කළ හැක."

            lower_bound = exp_value - 0.05
            upper_bound = exp_value + 0.05
            
            p_lbl = "Previous Rate" if lang == "English" else "Previous Rate (පෙර)"
            f_lbl = "Forecast" if lang == "English" else "Forecast (අපේක්ෂාව)"
            r_lbl = "AI Expected Rate" if lang == "English" else "AI Expected Rate (අනුමානය)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">🤖 <b>AI Advanced Forecast Radar</b></div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{p_lbl}</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{fomc_previous:.2f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{f_lbl}</div><div style="font-size: 22px; font-weight: bold; color: white;">{fomc_forecast:.2f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">{r_lbl}</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">{dev_signal}</div><div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">{dev_desc}</div></div></div>''', unsafe_allow_html=True)

# --- NEW TAB: LIVE ECONOMIC CALENDAR WITH BULL MATRIX GUIDE MAP ---
with tab2:
    if lang == "English":
        st.header("📅 Live Economic Calendar & Macro Guide Map")
        st.write("Use the Color Map below to find the specific Leading Indicators inside the Live Calendar window.")
    else:
        st.header("📅 සජීවී දින දර්ශනය සහ මැක්‍රෝ වර්ණ සිතියම")
        st.write("පහත දැක්වෙන වර්ණ සිතියම (Color Map) උපකාර කරගෙන සජීවී දින දර්ශනය තුළ ඇති අදාළ පෙරගමන් දත්ත (Leading Indicators) පහසුවෙන් සොයාගන්න.")
    
    st.markdown("#### 🎨 🗺️ Bull Matrix Macro Color Map" if lang == "English" else "#### 🎨 🗺️ Bull Matrix මැක්‍රෝ වර්ණ සිතියම")

    cmap_html = f"""<div class="mobile-scroll-container">
    <div style="min-width: 200px; border-left: 4px solid #00E5FF; padding-left: 10px; background-color: rgba(0,229,255,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #00E5FF; font-size: 14px;">🟢 CPI</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• Core PPI m/m<br>• WTI Crude Oil<br>• NY Fed Expect.<br>• ISM Prices Paid<br>• Import Prices</div></div>
    <div style="min-width: 200px; border-left: 4px solid #FF9800; padding-left: 10px; background-color: rgba(255,152,0,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #FF9800; font-size: 14px;">🟠 NFP</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• ADP Employment<br>• ISM Services Emp.<br>• JOLTs Job Openings<br>• Initial Jobless Claims<br>• Challenger Job Cuts</div></div>
    <div style="min-width: 200px; border-left: 4px solid #E040FB; padding-left: 10px; background-color: rgba(224,64,251,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #E040FB; font-size: 14px;">🟣 Core PCE</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• Core CPI m/m<br>• Core PPI m/m<br>• Avg Hourly Earnings<br>• Retail Sales m/m</div></div>
    <div style="min-width: 200px; border-left: 4px solid #2979FF; padding-left: 10px; background-color: rgba(41,121,255,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #2979FF; font-size: 14px;">🔵 Advance GDP</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• Atlanta Fed GDPNow<br>• Retail Sales (Q. Avg)<br>• Trade Balance<br>• ISM Composite PMI<br>• Durable Goods Orders</div></div>
    <div style="min-width: 200px; border-left: 4px solid #FF5252; padding-left: 10px; background-color: rgba(255,82,82,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #FF5252; font-size: 14px;">🔴 FOMC Decision</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• CME FedWatch<br>• Core PCE/CPI Trend<br>• Labor Market Data<br>• Recent Fedspeak<br>• Financial Conditions</div></div>
    </div>"""
    st.markdown(cmap_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Live TradingView Calendar Window
    components.html("""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
      {
      "colorTheme": "dark",
      "isTransparent": true,
      "width": "100%",
      "height": "800",
      "locale": "en",
      "importanceFilter": "0,1",
      "countryFilter": "us"
    }
      </script>
    </div>
    """, height=800, scrolling=True)

    # --- Reference Guide Below Calendar ---
    st.markdown("---")
    if lang == "English":
        st.subheader("📖 Macro Leading Indicators Data Guide")
        st.write("Where to find the specific data points required for the predictions.")
        
        with st.expander("📅 1. Data Found Directly in the Economic Calendar"):
            st.markdown("""
            * **🟢 CPI:** Core PPI m/m, NY Fed 1-Year Inflation Expectations, ISM Prices Paid, Import Price Index m/m.
            * **🟠 NFP:** ADP Non-Farm Employment Change, ISM Services Employment, JOLTs Job Openings, Initial Jobless Claims, Challenger Job Cuts.
            * **🟣 Core PCE:** Core CPI m/m, Core PPI m/m, Average Hourly Earnings m/m, Retail Sales m/m.
            * **🔵 Advance GDP:** Retail Sales m/m (Quarterly Average), Trade Balance, ISM Composite PMI, Core Durable Goods Orders m/m.
            * **🔴 FOMC Rate Decision:** Core PCE/CPI Trend, Labor Market Data (NFP/Claims).
            """)
            
        with st.expander("🌍 2. External Data (Not in the Calendar)"):
            st.markdown("""
            * **WTI Crude Oil / Gasoline Prices (🟢 CPI):** Check the trend on TradingView charts (`USOIL` or `CL1!`).
            * **Atlanta Fed GDPNow Tracker (🔵 Advance GDP):** Search for "Atlanta Fed GDPNow" on Google to see the official live tracker.
            * **CME FedWatch Probability (🔴 FOMC):** Check the official CME Group "FedWatch Tool" for investor rate expectations.
            * **Recent Fedspeak Rhetoric (🔴 FOMC):** Read news summaries on Forex Factory News Feed, Bloomberg, or Financial Twitter (X).
            * **Financial Conditions Index (🔴 FOMC):** Check the Chicago Fed official website or TradingView chart for `NFCI`.
            """)
    else:
        st.subheader("📖 මැක්‍රෝ පෙරගමන් දත්ත මාර්ගෝපදේශය")
        st.write("පුරෝකථනය සඳහා අවශ්‍ය දත්ත ලබාගත යුතු නිවැරදිම මූලාශ්‍ර.")
        
        with st.expander("📅 1. ආර්ථික දින දර්ශනයෙන් (Calendar) සෘජුවම ගතහැකි දත්ත"):
            st.markdown("""
            * **🟢 CPI:** Core PPI m/m, NY Fed 1-Year Inflation Expectations, ISM Prices Paid, Import Price Index m/m.
            * **🟠 NFP:** ADP Non-Farm Employment Change, ISM Services Employment, JOLTs Job Openings, Initial Jobless Claims, Challenger Job Cuts.
            * **🟣 Core PCE:** Core CPI m/m, Core PPI m/m, Average Hourly Earnings m/m, Retail Sales m/m.
            * **🔵 Advance GDP:** Retail Sales m/m (Quarterly Average), Trade Balance, ISM Composite PMI, Core Durable Goods Orders m/m.
            * **🔴 FOMC Rate Decision:** Core PCE/CPI Trend, Labor Market Data (NFP/Claims).
            """)
            
        with st.expander("🌍 2. දින දර්ශනයේ නොමැති බාහිර දත්ත (External Sources)"):
            st.markdown("""
            * **WTI Crude Oil / Gasoline Prices (🟢 CPI):** TradingView චාට් එකෙන් (`USOIL` / `CL1!`) තෙල් මිලේ ප්‍රවණතාවය බැලීම.
            * **Atlanta Fed GDPNow Tracker (🔵 Advance GDP):** Google හි "Atlanta Fed GDPNow" සර්ච් කර නිල වෙබ් අඩවියෙන් ලයිව් ප්‍රතිශතය බැලීම.
            * **CME FedWatch Probability (🔴 FOMC):** CME Group වෙබ් අඩවියේ ඇති "FedWatch Tool" හරහා ආයෝජකයන්ගේ අපේක්ෂාව බැලීම.
            * **Recent Fedspeak Rhetoric (🔴 FOMC):** Forex Factory News Feed, Bloomberg, හෝ Financial Twitter (X) හරහා Fed නිලධාරීන්ගේ කතාවල සාරාංශය කියවීම.
            * **Financial Conditions Index (🔴 FOMC):** Chicago Fed නිල වෙබ් අඩවිය හෝ TradingView හි `NFCI` චාට් එක.
            """)

# --- NEW TAB: TRADING JOURNAL ---
with tab3:
    st.header("📓 My Trading Journal" if lang == "English" else "📓 මගේ ට්‍රේඩින් ජර්නල් එක")
    st.write("Review your saved predictions or load them back into the calculator." if lang == "English" else "ඔබ සේව් කරපු දත්ත මෙතනින් බලන්න හෝ නැවත ඇප් එකට Load කරන්න.")
    
    if len(st.session_state['journal']) == 0:
        st.info("Your journal is empty. Go to the 'Live Predictor' tab, analyze a news event, and click 'Save to Journal'!" if lang == "English" else "ජර්නල් එක හිස්. Live Predictor එකෙන් ඩේටා විශ්ලේෂණය කරලා 'Save to Journal' ඔබන්න!")
    else:
        st.markdown("---")
        h1, h2, h3, h4, h5 = st.columns([2, 3, 2, 3, 1.2]) 
        marker = '<span class="journal-row-marker" style="display:none;"></span>'
        h1.markdown(f"{marker}<div class='journal-header'><b>Date & Time</b></div>" if lang == "English" else f"{marker}<div class='journal-header'><b>දිනය සහ වේලාව</b></div>", unsafe_allow_html=True)
        h2.markdown("<div class='journal-header'><b>News Event</b></div>" if lang == "English" else "<div class='journal-header'><b>නිවුස් එක</b></div>", unsafe_allow_html=True)
        h3.markdown("<div class='journal-header'><b>DXY Score</b></div>" if lang == "English" else "<div class='journal-header'><b>DXY ලකුණ</b></div>", unsafe_allow_html=True)
        h4.markdown("<div class='journal-header'><b>Prediction</b></div>" if lang == "English" else "<div class='journal-header'><b>පුරෝකථනය</b></div>", unsafe_allow_html=True)
        h5.markdown("<div class='journal-header'><b>Actions</b></div>" if lang == "English" else "<div class='journal-header'><b>ක්‍රියාමාර්ග</b></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        for i, entry in enumerate(st.session_state['journal']):
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 3, 1.2])
            
            c1.markdown(f"<div class='journal-text'>{marker}{entry['Date & Time']}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='journal-text'>{entry['News Event']}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='journal-text'>{entry['DXY Score']}</div>", unsafe_allow_html=True)
            
            pred = entry["Predicted Direction"]
            if "BULLISH" in pred: color, svg = "#00ffcc", svg_bullish
            elif "BEARISH" in pred: color, svg = "#ff4b4b", svg_bearish
            else: color, svg = "#FFC107", svg_ranging
                
            svg_small = svg.replace('width="24"', 'width="18"').replace('height="24"', 'height="18"')
            
            pred_html = f"""<div style="display: flex; align-items: center; gap: 6px; padding-top: 5px;"><span class='pred-text' style="font-size: 14px; font-weight: bold; color: {color};">{pred}</span><div class='pred-icon' style="display: flex; align-items: center;">{svg_small}</div></div>"""
            c4.markdown(pred_html, unsafe_allow_html=True)
            
            btn_col1, btn_col2 = c5.columns(2)
            
            if btn_col1.button("🔄", key=f"load_btn_{entry['id']}", help="Load this entry" if lang == "English" else "දත්ත නැවත Load කරන්න"):
                st.session_state['loaded_data'] = entry
                st.toast("✅ Data Loaded! Go to the 'Live Predictor' tab." if lang == "English" else "✅ දත්ත Load කළා! 'සජීවී පුරෝකථනය' ටැබ් එකට යන්න.")
                st.rerun()
                
            if btn_col2.button("✖", key=f"del_btn_{entry['id']}", help="Delete this entry" if lang == "English" else "මෙම දත්තය මකා දමන්න"):
                try:
                    supabase.table('journal_entries').delete().eq('id', entry['id']).execute()
                    fetch_journal()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {e}")
            
            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.1); margin: 12px 0;'/>", unsafe_allow_html=True)
                
        # --- UI Balanced Action Buttons (Download & Clear) ---
        st.markdown("<br>", unsafe_allow_html=True)
        dl_col, clr_col, _empty1, _empty2 = st.columns([1.5, 1.5, 1, 3])
        marker_btn = '<span class="action-btn-marker" style="display:none;"></span>'
        
        with dl_col:
            st.markdown(marker_btn, unsafe_allow_html=True)
            df = pd.DataFrame(st.session_state['journal'])
            df_export = df.drop(columns=['Inputs', 'id']) 
            csv = df_export.to_csv(index=False).encode('utf-8')
            dl_txt = "📥 Download CSV" if lang == "English" else "📥 Download CSV" 
            st.download_button(label=dl_txt, data=csv, file_name='macro_journal.csv', mime='text/csv')
            
        with clr_col:
            clr_txt = "🗑️ Clear All Data" if lang == "English" else "🗑️ සියලු දත්ත මකන්න" 
            if st.button(clr_txt, type="primary"): 
                try:
                    supabase.table('journal_entries').delete().eq('user_id', st.session_state['user'].id).execute()
                    st.session_state['journal'] = []
                    st.session_state['loaded_data'] = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear data: {e}")

# --- NEW TAB: HISTORICAL CASE STUDIES ---
with tab4:
    if lang == "English":
        st.header("📚 Historical Case Studies")
        st.write("Review how past macroeconomic data impacted the US Dollar (DXY).")
        
        with st.expander("📌 Case Study 1: The Post-COVID Inflation Shock (2022 CPI)"):
            st.write("""
            **Scenario:** US Inflation hit 9.1% (40-year highs).
            * **Leading Data:** PPI was surging due to supply chain issues. Energy prices (Oil) skyrocketed due to the Russia-Ukraine war. Import prices were massive.
            * **Prediction Tool Score:** 100% Bullish (DXY).
            * **Result:** The Fed was forced into aggressive rate hikes. DXY rallied to a 20-year high of 114.78. EUR/USD dropped below parity (1.0000). US30 and NASDAQ crashed heavily.
            """)
            
        with st.expander("📌 Case Study 2: The Dovish Pivot Expectations (Late 2023 FOMC)"):
            st.write("""
            **Scenario:** Inflation was cooling down rapidly towards 3%.
            * **Leading Data:** Core PCE showed consecutive drops. Jobless claims started to edge higher. Fedspeak shifted from 'hike more' to 'hold and wait'.
            * **Prediction Tool Score:** 35% Bearish (DXY).
            * **Result:** Jerome Powell delivered a dovish press conference, and the Dot Plot showed 3 rate cuts for 2024. DXY dumped aggressively, sending XAU/USD (Gold) and US Indices (NASDAQ/US30) to all-time highs.
            """)
    else:
        st.header("📚 අතීත සිදුවීම් අධ්‍යයනය")
        st.write("අතීතයේ ආර්ථික දත්ත ඩොලරයට බලපාපු විදිය මෙතනින් අධ්‍යයනය කරන්න.")
        
        with st.expander("📌 1 වන අධ්‍යයනය: පශ්චාත්-කොවිඩ් උද්ධමන කම්පනය (2022 CPI)"):
            st.write("""
            **තත්ත්වය:** ඇමෙරිකානු උද්ධමනය 9.1% දක්වා (වසර 40ක උපරිමයට) ඉහළ ගියේය.
            * **පෙරගමන් දත්ත:** සැපයුම් ජාලයේ ගැටලු නිසා PPI ඉහළ යමින් තිබුණි. රුසියානු-යුක්රේන යුද්ධය නිසා බලශක්ති (ඉන්ධන) මිල ගණන් අහසට නැග තිබුණි. ආනයන මිලද විශාල ලෙස ඉහළ ගොස් තිබුණි.
            * **පුරෝකථන මෙවලමේ ලකුණ:** 100% Bullish (DXY).
            * **ප්‍රතිඵලය:** ෆෙඩරල් බැංකුවට (Fed) දැඩි ලෙස පොලී අනුපාත වැඩි කිරීමට සිදුවිය. DXY දර්ශකය වසර 20ක උපරිම අගය වූ 114.78 දක්වා ඉහළ ගියේය. EUR/USD අගය 1.0000 ට වඩා පහත වැටුණි. US30 සහ NASDAQ දර්ශක දැඩි ලෙස කඩා වැටුණි.
            """)
            
        with st.expander("📌 2 වන අධ්‍යයනය: Dovish Pivot අපේක්ෂාවන් (2023 අගභාගයේ FOMC)"):
            st.write("""
            **තත්ත්වය:** උද්ධමනය 3% දක්වා වේගයෙන් පහත වැටෙමින් තිබුණි.
            * **පෙරගමන් දත්ත:** Core PCE අඛණ්ඩව පහත වැටෙන බව පෙන්නුම් කළේය. Jobless claims (රැකියා විරහිත දත්ත) තරමත් ඉහළ යාමට පටන් ගෙන තිබුණි. Fed නිලධාරීන්ගේ ප්‍රකාශ (Fedspeak) 'තවත් පොලී වැඩි කළ යුතුයි' යන තැනින් මිදී 'දැනට ඇති, අපි බලා සිටිමු' යන තැනට මාරු වී තිබුණි.
            * **පුරෝකථන මෙවලමේ ලකුණ:** 35% Bearish (DXY).
            * **ප්‍රතිඵලය:** ජෙරොම් පවෙල් (Jerome Powell) විසින් Dovish මාධ්‍ය සාකච්ඡාවක් ලබා දුන් අතර, Dot Plot මගින් 2024 වසර සඳහා පොලී අනුපාත කප්පාදු 3ක් පෙන්වා දෙන ලදී. මේ නිසා DXY දර්ශකය වේගයෙන් කඩා වැටුණු අතර, XAU/USD (රන්) සහ US Indices (NASDAQ/US30) සර්වකාලීන උපරිම අගයන් (All-time highs) දක්වා ඉහළ ගියේය.
            """)
