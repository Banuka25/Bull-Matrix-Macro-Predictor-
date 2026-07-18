import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime
import pytz
import base64
import os
import time
import streamlit.components.v1 as components
from supabase import create_client, Client
import extra_streamlit_components as stx

st.set_page_config(page_title="Macro DXY Predictor Pro", page_icon="📈", layout="wide")

# --- COOKIE MANAGER (For Auto-Login) ---
cookie_manager = stx.CookieManager()

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
if 'load_counter' not in st.session_state:
    st.session_state['load_counter'] = 0

# --- HELPER: CLEAN EMOJIS FROM STRINGS ---
def clean_evt(name):
    for emoji in ["🟢 ", "🟠 ", "🟣 ", "🔵 ", "🔴 "]:
        name = name.replace(emoji, "")
    return name.strip()

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

# --- AUTO-LOGIN VIA COOKIES ---
if st.session_state['user'] is None:
    acc_token = cookie_manager.get('supa_access')
    ref_token = cookie_manager.get('supa_refresh')
    
    if acc_token and ref_token:
        try:
            res = supabase.auth.set_session(acc_token, ref_token)
            st.session_state['user'] = res.user
            fetch_journal()
        except Exception:
            pass # Token expired or invalid

# --- Language Toggle Switch ---
st.sidebar.markdown("<br>", unsafe_allow_html=True)
lang = st.sidebar.radio("🌐 Language / භාෂාව", ["English", "සිංහල"], horizontal=True)
st.sidebar.markdown("---")

# --- LOGIN / SIGNUP UI ---
if st.session_state['user'] is None:
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
                    
                    # Save Tokens to Cookies for Auto-Login
                    cookie_manager.set('supa_access', res.session.access_token)
                    cookie_manager.set('supa_refresh', res.session.refresh_token)
                    
                    fetch_journal()
                    time.sleep(0.5) # Wait a split second to ensure cookies are written
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
                    
    st.stop()

# --- SIDEBAR LOGOUT ---
logout_txt = "Logout" if lang == "English" else "ඉවත් වන්න (Logout)"
st.sidebar.markdown(f"<div style='font-size: 13px; color: gray;'>👤 Logged in as:<br><b style='color: white;'>{st.session_state['user'].email}</b></div>", unsafe_allow_html=True)
if st.sidebar.button(logout_txt):
    # Clear cookies on logout
    cookie_manager.delete('supa_access')
    cookie_manager.delete('supa_refresh')
    time.sleep(0.5)
    supabase.auth.sign_out()
    st.session_state['user'] = None
    st.session_state['journal'] = []
    st.rerun()
st.sidebar.markdown("---")

# --- DYNAMIC LOAD SUFFIX ---
lsuf = f"_{st.session_state['load_counter']}"

# --- MOBILE RESPONSIVE PROFESSIONAL UI CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .bullish-text { color: #00ffcc; font-weight: bold; font-size: 24px; }
    .bearish-text { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    .neutral-text { color: #ffc107; font-weight: bold; font-size: 24px; }
    
    .vertical-divider {
        border-left: 2px solid rgba(255, 255, 255, 0.15);
        height: 100%;
        min-height: 520px;
        margin: 0 auto;
    }
    .radar-divider {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        margin: 25px 0;
    }
    
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
    
    .stDownloadButton > button, .stButton > button[kind="primary"] {
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
        width: 100% !important; 
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
    .mobile-scroll-container > div { flex: 0 0 auto !important; }
    
    .journal-header b { font-size: 15px; }
    .journal-text { font-size: 14px; color: #d0d0d0; padding-top: 5px; }

    /* ACTION BUTTON ALIGNMENT FIX (DESKTOP) */
    div[data-testid="stHorizontalBlock"]:has(.action-btn-marker) {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        gap: 15px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.action-btn-marker) > div[data-testid="column"] {
        flex: 0 1 auto !important;
        width: auto !important;
        min-width: 160px !important;
    }

    @media (max-width: 768px) {
        .vertical-divider { display: none !important; }
        .radar-divider { margin: 15px 0 !important; }

        /* Compact Journal Table - Fits on Mobile Screen */
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            overflow: hidden !important;
            padding-bottom: 5px !important;
            gap: 2px !important;
            align-items: center !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"] {
            padding: 0 2px !important;
            min-width: 0 !important;
        }
        /* Proportional Column Widths */
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(1) { flex: 2 !important; width: 20% !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(2) { flex: 2.2 !important; width: 22% !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(3) { flex: 1.5 !important; width: 15% !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(4) { flex: 2.3 !important; width: 23% !important; }
        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) > div[data-testid="column"]:nth-of-type(5) { flex: 2 !important; width: 20% !important; }
        
        .journal-header b { font-size: 10px !important; line-height: 1.1 !important; word-wrap: break-word !important; display: block !important; }
        .journal-text { font-size: 10px !important; line-height: 1.1 !important; word-wrap: break-word !important; white-space: pre-wrap !important; padding-top: 2px !important; }
        .pred-text { font-size: 9px !important; display: block; }
        .pred-icon svg { width: 12px !important; height: 12px !important; }

        div[data-testid="stHorizontalBlock"]:has(.journal-row-marker) div[data-testid="stHorizontalBlock"] {
             flex-direction: row !important;
             min-width: 0 !important;
             gap: 2px !important;
             justify-content: flex-start !important;
        }
        button[title="Delete this entry"], button[title="Load this entry"] {
            width: 18px !important; height: 18px !important;
            min-height: 18px !important; min-width: 18px !important;
        }

        /* 50/50 Download and Clear Buttons on Mobile */
        div[data-testid="stHorizontalBlock"]:has(.action-btn-marker) > div[data-testid="column"] {
            flex: 1 1 50% !important;
            width: 50% !important;
            min-width: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.action-btn-marker) button {
            font-size: 12px !important;
            padding: 0px 5px !important;
            min-height: 38px !important;
        }
    }
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
    clean_event = clean_evt(event_name)
    
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
        fetch_journal() 
        msg = "✅ Saved to Cloud Journal!" if lang == "English" else "✅ Cloud ජර්නල් එකට සේව් කළා!"
        st.toast(msg)
    except Exception as e:
        st.error(f"Error saving to Cloud: {e}")

# --- UPDATED DATA FETCHING LOGIC ---
def get_num_val(event_name, input_key, default_val):
    evt_cleaned = clean_evt(event_name)
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] == evt_cleaned:
        val = st.session_state['loaded_data']['Inputs'].get(input_key)
        if val is not None:
            try: return float(val)
            except: pass
    return default_val

def get_idx(event_name, input_key, options_list):
    evt_cleaned = clean_evt(event_name)
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] == evt_cleaned:
        val = st.session_state['loaded_data']['Inputs'].get(input_key)
        if val in options_list:
            return options_list.index(val)
    return 0

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

tab_names = ["🔮 Live Predictor", "📅 Live Calendar", "📓 Trading Journal", "📚 Historical Case Studies"] if lang == "English" else ["🔮 සජීවී පුරෝකථනය", "📅 සජීවී දින දර්ශනය", "📓 ට්‍රේඩින් ජර්නල් එක", "📚 අතීත සිදුවීම් අධ්‍යයනය"]
tab1, tab2, tab3, tab4 = st.tabs(tab_names)

with tab1:
    st.sidebar.header("📅 Select Major News Event" if lang == "English" else "📅 ප්‍රධාන නිවුස් එක තෝරන්න")
    
    events_list = ["🟢 CPI (Consumer Price Index)", "🟠 NFP (Non-Farm Payrolls)", "🟣 Core PCE Price Index", "🔵 Advance GDP", "🔴 FOMC Rate Decision"]
    
    default_event_idx = 0
    if st.session_state['loaded_data']:
        loaded_evt = st.session_state['loaded_data']['News Event']
        for i, e in enumerate(events_list):
            if clean_evt(e) == loaded_evt:
                default_event_idx = i
                break

    major_news = st.sidebar.radio("Choose Event:" if lang == "English" else "නිවුස් එක තෝරන්න:", events_list, index=default_event_idx, key=f"evt_radio{lsuf}")

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

    # ----------------- 1. CPI CALCULATOR -----------------
    if major_news.startswith("🟢 CPI"):
        st.header("🟢 🧮 CPI Leading Data Calculator" if lang == "English" else "🟢 🧮 CPI දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_ppi = ["Consensus වලට වඩා වැඩි", "Neutral", "Consensus වලට වඩා අඩු"] if lang == "සිංහල" else ["Higher than Consensus", "Neutral", "Lower than Consensus"]
        opt_gas = ["ඉහළ යනවා (Inflationary)", "ස්ථාවරයි", "පහළ යනවා (Deflationary)"] if lang == "සිංහල" else ["Rising (Inflationary)", "Stable", "Falling (Deflationary)"]
        opt_nyfed = ["වැඩිවී ඇත", "වෙනස් වී නැත", "අඩුවී ඇත"] if lang == "සිංහල" else ["Increased", "Unchanged", "Decreased"]
        opt_pmi = ["වේගයෙන් ඉහළ යයි (>55)", "Neutral", "පහළ යයි (<50)"] if lang == "සිංහල" else ["Increasing Rapidly (>55)", "Neutral", "Decreasing (<50)"]
        opt_imp = ["ඉහළ යනවා", "ස්ථාවරයි", "පහළ යනවා"] if lang == "සිංහල" else ["Rising", "Stable", "Falling"]
        
        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                cpi_previous = st.number_input(f"🟢 📉 {prev_txt} (%):", value=get_num_val(major_news, "cpi_prev", 0.3), step=0.1, format="%.1f", key=f"cpi_prev{lsuf}")
            with col_fc:
                cpi_forecast = st.number_input(f"🟢 📊 {fc_txt} (%):", value=get_num_val(major_news, "cpi_fc", 0.2), step=0.1, format="%.1f", key=f"cpi_fc{lsuf}")
            st.markdown("<br>", unsafe_allow_html=True)

            ppi_input = st.selectbox("🟢 1. PPI Trend:" if lang == "English" else "🟢 1. PPI ප්‍රවණතාව:", opt_ppi, index=get_idx(major_news, "ppi", opt_ppi), key=f"cpi_ppi{lsuf}")
            gasoline = st.selectbox("🟢 2. Gasoline Prices:" if lang == "English" else "🟢 2. ඉන්ධන මිල:", opt_gas, index=get_idx(major_news, "gas", opt_gas), key=f"cpi_gas{lsuf}")
            ny_fed = st.selectbox("🟢 3. NY Fed 1-Yr Inflation:" if lang == "English" else "🟢 3. NY Fed උද්ධමන අපේක්ෂාව:", opt_nyfed, index=get_idx(major_news, "nyfed", opt_nyfed), key=f"cpi_nyfed{lsuf}")
            pmi_prices = st.selectbox("🟢 4. ISM Prices Paid:" if lang == "English" else "🟢 4. ISM Prices Paid අගය:", opt_pmi, index=get_idx(major_news, "pmi", opt_pmi), key=f"cpi_pmi{lsuf}")
            import_prices = st.selectbox("🟢 5. Import Prices:" if lang == "English" else "🟢 5. ආනයන මිල දර්ශකය:", opt_imp, index=get_idx(major_news, "imp", opt_imp), key=f"cpi_imp{lsuf}")
            
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
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### Predicted DXY Direction: <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)

            inputs_dict = {"cpi_prev": cpi_previous, "cpi_fc": cpi_forecast, "ppi": ppi_input, "gas": gasoline, "nyfed": ny_fed, "pmi": pmi_prices, "imp": import_prices}
            render_save_button(major_news, score, direction, inputs_dict)
            
            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)
            deviation = (score - 50) / 50.0 * 0.3 
            exp_value = cpi_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                dev_signal = "🚀 Hotter & Accelerating (Strong Bullish)" if exp_value > cpi_previous else "⚖️ Hotter BUT Cooling (Fakeout Warning)"
            elif score <= 40:
                dev_color = "#ff4b4b"
                dev_signal = "📉 Cooler & Decelerating (Strong Bearish)" if exp_value < cpi_previous else "⚖️ Cooler BUT Sticky (Fakeout Warning)"
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{cpi_previous:.1f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div><div style="font-size: 22px; font-weight: bold; color: white;">{cpi_forecast:.1f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{(exp_value - 0.05):.2f}% - {(exp_value + 0.05):.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center;">{dev_signal}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 2. NFP CALCULATOR -----------------
    elif major_news.startswith("🟠 NFP"):
        st.header("🟠 💼 NFP Leading Data Calculator" if lang == "English" else "🟠 💼 NFP දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_adp = ["ඉතා ඉහළයි (Strong Beat)", "Neutral / සාමාන්‍යයි", "ඉතා අඩුයි (Big Miss)"] if lang == "සිංහල" else ["Strong Beat", "Neutral / As Expected", "Big Miss"]
        opt_ism = ["වර්ධනය වේ (>50)", "Neutral", "අඩු වේ (<50)"] if lang == "සිංහල" else ["Expanding (>50)", "Neutral", "Contracting (<50)"]
        opt_jolts = ["ඉහළ යනවා (ප්‍රබල ඉල්ලුම)", "Neutral", "පහළ යනවා (අඩු ඉල්ලුම)"] if lang == "සිංහල" else ["Increasing (Strong Demand)", "Neutral", "Decreasing (Weak Demand)"]
        opt_jobless = ["අඛණ්ඩව අඩුයි (<200k)", "Neutral", "වේගයෙන් ඉහළ යයි (>250k)"] if lang == "සිංහල" else ["Consistently Low (<200k)", "Neutral", "Rising Rapidly (>250k)"]
        opt_chal = ["අඩු රැකියා කප්පාදුවක්", "සාමාන්‍යයි", "වැඩි රැකියා කප්පාදුවක්"] if lang == "සිංහල" else ["Low Layoffs", "Average", "High Layoffs"]

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                nfp_previous = st.number_input(f"🟠 📉 {prev_txt} (k):", value=int(get_num_val(major_news, "nfp_prev", 200)), step=10, format="%d", key=f"nfp_prev{lsuf}")
            with col_fc:
                nfp_forecast = st.number_input(f"🟠 📊 {fc_txt} (k):", value=int(get_num_val(major_news, "nfp_fc", 180)), step=10, format="%d", key=f"nfp_fc{lsuf}")
            st.markdown("<br>", unsafe_allow_html=True)

            adp_input = st.selectbox("🟠 1. ADP Employment:", opt_adp, index=get_idx(major_news, "adp", opt_adp), key=f"nfp_adp{lsuf}")
            ism_services = st.selectbox("🟠 2. ISM Services Emp:", opt_ism, index=get_idx(major_news, "ism", opt_ism), key=f"nfp_ism{lsuf}")
            jolts = st.selectbox("🟠 3. JOLTs Job Openings:", opt_jolts, index=get_idx(major_news, "jolts", opt_jolts), key=f"nfp_jolts{lsuf}")
            jobless = st.selectbox("🟠 4. Initial Jobless Claims:", opt_jobless, index=get_idx(major_news, "jobless", opt_jobless), key=f"nfp_jobless{lsuf}")
            challenger = st.selectbox("🟠 5. Challenger Job Cuts:", opt_chal, index=get_idx(major_news, "chal", opt_chal), key=f"nfp_chal{lsuf}")
            
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
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### Predicted DXY Direction: <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)
            
            inputs_dict = {"nfp_prev": nfp_previous, "nfp_fc": nfp_forecast, "adp": adp_input, "ism": ism_services, "jolts": jolts, "jobless": jobless, "chal": challenger}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)
            deviation = (score - 50) / 50.0 * 50.0 
            exp_value = nfp_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                dev_signal = "🚀 Strong Beat & Accelerating" if exp_value > nfp_previous else "⚖️ Beat BUT Decelerating (Fakeout Warning)"
            elif score <= 40:
                dev_color = "#ff4b4b"
                dev_signal = "📉 Big Miss & Decelerating" if exp_value < nfp_previous else "⚖️ Miss BUT Sticky (Fakeout Warning)"
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{nfp_previous}k</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div><div style="font-size: 22px; font-weight: bold; color: white;">{nfp_forecast}k</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{(exp_value - 10):.0f}k - {(exp_value + 10):.0f}k</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center;">{dev_signal}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 3. CORE PCE CALCULATOR -----------------
    elif major_news.startswith("🟣 Core"):
        st.header("🟣 🛒 Core PCE Leading Data Calculator" if lang == "English" else "🟣 🛒 Core PCE දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_cpi = ["අපේක්ෂිත අගයට වඩා වැඩි", "Neutral", "අපේක්ෂිත අගයට වඩා අඩු"] if lang == "සිංහල" else ["Hotter than Expected", "Neutral", "Cooler than Expected"]
        opt_ppi = ["අපේක්ෂිත අගයට වඩා වැඩි", "Neutral", "අපේක්ෂිත අගයට වඩා අඩු"] if lang == "සිංහල" else ["Hotter than Expected", "Neutral", "Cooler than Expected"]
        opt_hr = ["ඉතා වේගයෙන් වැඩිවේ", "ස්ථාවරයි", "පහළ යමින් පවතී"] if lang == "සිංහල" else ["Rising Faster", "Stable", "Cooling Down"]
        opt_ret = ["ප්‍රබලයි (වැඩි පාරිභෝගික වියදම්)", "Neutral", "දුර්වලයි (අඩු පාරිභෝගික වියදම්)"] if lang == "සිංහල" else ["Strong (High Spending)", "Neutral", "Weak (Low Spending)"]

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                pce_previous = st.number_input(f"🟣 📉 {prev_txt} (%):", value=get_num_val(major_news, "pce_prev", 0.3), step=0.1, format="%.1f", key=f"pce_prev{lsuf}")
            with col_fc:
                pce_forecast = st.number_input(f"🟣 📊 {fc_txt} (%):", value=get_num_val(major_news, "pce_fc", 0.2), step=0.1, format="%.1f", key=f"pce_fc{lsuf}")
            st.markdown("<br>", unsafe_allow_html=True)

            cpi_input = st.selectbox("🟣 1. Recent Core CPI:", opt_cpi, index=get_idx(major_news, "cpi", opt_cpi), key=f"pce_cpi{lsuf}")
            ppi_input = st.selectbox("🟣 2. Recent Core PPI:", opt_ppi, index=get_idx(major_news, "ppi", opt_ppi), key=f"pce_ppi{lsuf}")
            hourly_earnings = st.selectbox("🟣 3. Avg Hourly Earnings:", opt_hr, index=get_idx(major_news, "hr", opt_hr), key=f"pce_hr{lsuf}")
            retail_sales = st.selectbox("🟣 4. Retail Sales:", opt_ret, index=get_idx(major_news, "ret", opt_ret), key=f"pce_ret{lsuf}")
            
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
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### Predicted DXY Direction: <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)

            inputs_dict = {"pce_prev": pce_previous, "pce_fc": pce_forecast, "cpi": cpi_input, "ppi": ppi_input, "hr": hourly_earnings, "ret": retail_sales}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)
            deviation = (score - 50) / 50.0 * 0.2 
            exp_value = pce_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                dev_signal = "🚀 Hotter & Accelerating" if exp_value > pce_previous else "⚖️ Hotter BUT Cooling"
            elif score <= 40:
                dev_color = "#ff4b4b"
                dev_signal = "📉 Cooler & Decelerating" if exp_value < pce_previous else "⚖️ Cooler BUT Sticky"
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{pce_previous:.1f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div><div style="font-size: 22px; font-weight: bold; color: white;">{pce_forecast:.1f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{(exp_value - 0.05):.2f}% - {(exp_value + 0.05):.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center;">{dev_signal}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 4. ADVANCE GDP CALCULATOR -----------------
    elif major_news.startswith("🔵 Advance"):
        st.header("🔵 🏭 Advance GDP Leading Data Calculator" if lang == "English" else "🔵 🏭 Advance GDP දත්ත කැල්කියුලේටරය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_atl = ["ඉහළ අගයක් ගනී (>2.5%)", "Neutral", "පහළ අගයක් ගනී (<1.0%)"] if lang == "සිංහල" else ["Tracking High (>2.5%)", "Neutral", "Tracking Low (<1.0%)"]
        opt_ret = ["ප්‍රබල ධනාත්මක එකක්", "Neutral", "සෘණාත්මක එකක්"] if lang == "සිංහල" else ["Strongly Positive", "Neutral", "Negative"]
        opt_trade = ["හිඟය අඩු වෙනවා (Good)", "Neutral", "හිඟය වැඩි වෙනවා (Bad)"] if lang == "සිංහල" else ["Deficit Shrinking (Good)", "Neutral", "Deficit Widening (Bad)"]
        opt_pmi = ["වර්ධනය වේ (>50)", "Neutral (~50)", "අඩු වේ (<50)"] if lang == "සිංහල" else ["Expanding (>50)", "Neutral (~50)", "Contracting (<50)"]
        opt_dur = ["ඉහළ යනවා", "සාමාන්‍යයි", "පහළ යනවා"] if lang == "සිංහල" else ["Rising", "Neutral", "Falling"]

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                gdp_previous = st.number_input(f"🔵 📉 {prev_txt} (%):", value=get_num_val(major_news, "gdp_prev", 2.1), step=0.1, format="%.1f", key=f"gdp_prev{lsuf}")
            with col_fc:
                gdp_forecast = st.number_input(f"🔵 📊 {fc_txt} (%):", value=get_num_val(major_news, "gdp_fc", 1.8), step=0.1, format="%.1f", key=f"gdp_fc{lsuf}")
            st.markdown("<br>", unsafe_allow_html=True)

            atlanta_fed = st.selectbox("🔵 1. Atlanta Fed GDPNow:", opt_atl, index=get_idx(major_news, "atl", opt_atl), key=f"gdp_atl{lsuf}")
            retail_input = st.selectbox("🔵 2. Retail Sales (Quarterly):", opt_ret, index=get_idx(major_news, "ret", opt_ret), key=f"gdp_ret{lsuf}")
            trade_balance = st.selectbox("🔵 3. Trade Balance:", opt_trade, index=get_idx(major_news, "trade", opt_trade), key=f"gdp_trade{lsuf}")
            pmi_input = st.selectbox("🔵 4. ISM Composite PMI:", opt_pmi, index=get_idx(major_news, "pmi", opt_pmi), key=f"gdp_pmi{lsuf}")
            durable_goods = st.selectbox("🔵 5. Durable Goods Orders:", opt_dur, index=get_idx(major_news, "dur", opt_dur), key=f"gdp_dur{lsuf}")
            
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
            direction, css_class = ("BULLISH DXY 🚀", "bullish-text") if score >= 60 else ("BEARISH DXY 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### Predicted DXY Direction: <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score)

            inputs_dict = {"gdp_prev": gdp_previous, "gdp_fc": gdp_forecast, "atl": atlanta_fed, "ret": retail_input, "trade": trade_balance, "pmi": pmi_input, "dur": durable_goods}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)
            deviation = (score - 50) / 50.0 * 0.5 
            exp_value = gdp_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                dev_signal = "🚀 Stronger & Accelerating" if exp_value > gdp_previous else "⚖️ Stronger BUT Cooling"
            elif score <= 40:
                dev_color = "#ff4b4b"
                dev_signal = "📉 Weaker & Decelerating" if exp_value < gdp_previous else "⚖️ Weaker BUT Sticky"
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{gdp_previous:.1f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div><div style="font-size: 22px; font-weight: bold; color: white;">{gdp_forecast:.1f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{(exp_value - 0.1):.2f}% - {(exp_value + 0.1):.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center;">{dev_signal}</div></div></div>''', unsafe_allow_html=True)

    # ----------------- 5. FOMC RATE DECISION CALCULATOR -----------------
    elif major_news.startswith("🔴 FOMC"):
        st.header("🔴 🦅 FOMC Rate Decision & Statement" if lang == "English" else "🔴 🦅 FOMC පොලී අනුපාත තීරණය")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_fed = ["Hawk පැත්තට බරයි (Hike/Hold)", "මිශ්‍ර තත්ත්වයක්", "Dove පැත්තට බරයි (Cut)"] if lang == "සිංහල" else ["Pricing Hawk (Hike/Hold)", "Mixed", "Pricing Dove (Cut)"]
        opt_inf = ["ස්ථාවරයි / ඉහළ යයි", "Neutral", "වේගයෙන් පහළ වැටේ"] if lang == "සිංහල" else ["Sticky / Rising", "Neutral", "Falling Rapidly"]
        opt_lab = ["ප්‍රබලයි (වැඩි රැකියා ප්‍රමාණයක්)", "Neutral", "දුර්වලයි (අඩු රැකියා ප්‍රමාණයක්)"] if lang == "සිංහල" else ["Tight (Strong Jobs)", "Neutral", "Cooling (Weak Jobs)"]
        opt_speak = ["Hawkish දැඩි ප්‍රකාශ", "Neutral", "Dovish ලිහිල් ප්‍රකාශ"] if lang == "සිංහල" else ["Hawkish Rhetoric", "Neutral", "Dovish Rhetoric"]
        opt_fin = ["ලිහිල් (මුදල් සැපයුම වැඩියි)", "Neutral", "තදයි (මුදල් සැපයුම අඩුයි)"] if lang == "සිංහල" else ["Loose (Requires Tightening)", "Neutral", "Tight (Requires Easing)"]

        with col_left:
            st.subheader(sub_report_txt)
            col_prev, col_fc = st.columns(2)
            with col_prev:
                fomc_previous = st.number_input(f"🔴 📉 Previous Rate (%):", value=get_num_val(major_news, "fomc_prev", 5.50), step=0.25, format="%.2f", key=f"fomc_prev{lsuf}")
            with col_fc:
                fomc_forecast = st.number_input(f"🔴 📊 Market Forecast (%):", value=get_num_val(major_news, "fomc_fc", 5.25), step=0.25, format="%.2f", key=f"fomc_fc{lsuf}")
            st.markdown("<br>", unsafe_allow_html=True)

            fedwatch = st.selectbox("🔴 1. CME FedWatch Probability:", opt_fed, index=get_idx(major_news, "fed", opt_fed), key=f"fomc_fed{lsuf}")
            inflation = st.selectbox("🔴 2. Recent PCE/CPI Trend:", opt_inf, index=get_idx(major_news, "inf", opt_inf), key=f"fomc_inf{lsuf}")
            labor = st.selectbox("🔴 3. Recent Labor Market:", opt_lab, index=get_idx(major_news, "lab", opt_lab), key=f"fomc_lab{lsuf}")
            fedspeak = st.selectbox("🔴 4. Fedspeak / Dot Plot:", opt_speak, index=get_idx(major_news, "speak", opt_speak), key=f"fomc_speak{lsuf}")
            fin_conditions = st.selectbox("🔴 5. Financial Conditions:", opt_fin, index=get_idx(major_news, "fin", opt_fin), key=f"fomc_fin{lsuf}")
            
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
            direction, css_class = ("HAWKISH (BULLISH DXY) 🚀", "bullish-text") if score >= 60 else ("DOVISH (BEARISH DXY) 📉", "bearish-text") if score <= 40 else ("NEUTRAL / VOLATILE ⚖️", "neutral-text")
            st.markdown(f"### Predicted DXY Direction: <span class='{css_class}'>{direction}</span>", unsafe_allow_html=True)
            render_market_metrics(score, is_fomc=True)

            inputs_dict = {"fomc_prev": fomc_previous, "fomc_fc": fomc_forecast, "fed": fedwatch, "inf": inflation, "lab": labor, "speak": fedspeak, "fin": fin_conditions}
            render_save_button(major_news, score, direction, inputs_dict)

            st.markdown("<hr class='radar-divider' />", unsafe_allow_html=True)
            deviation = (score - 50) / 50.0 * 0.25 
            exp_value = fomc_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                dev_signal = "🦅 Hawkish Hike / Hold" if exp_value >= fomc_previous else "⚖️ Hawkish rhetoric BUT Rate Capped"
            elif score <= 40:
                dev_color = "#ff4b4b"
                dev_signal = "🕊️ Dovish Cut & Accelerating" if exp_value < fomc_previous else "⚖️ Dovish rhetoric BUT Sticky Rates"
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Market Pricing (Neutral)"

            st.markdown(f'''<div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><div style="text-align: left;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div><div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{fomc_previous:.2f}%</div></div><div style="text-align: center;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div><div style="font-size: 22px; font-weight: bold; color: white;">{fomc_forecast:.2f}%</div></div><div style="text-align: right;"><div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected</div><div style="font-size: 22px; font-weight: bold; color: {dev_color};">{(exp_value - 0.05):.2f}% - {(exp_value + 0.05):.2f}%</div></div></div><div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;"><div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center;">{dev_signal}</div></div></div>''', unsafe_allow_html=True)

# --- NEW TAB: LIVE ECONOMIC CALENDAR ---
with tab2:
    st.header("📅 Live Economic Calendar" if lang == "English" else "📅 සජීවී දින දර්ශනය")
    cmap_html = f"""<div class="mobile-scroll-container">
    <div style="min-width: 200px; border-left: 4px solid #00E5FF; padding-left: 10px; background-color: rgba(0,229,255,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #00E5FF; font-size: 14px;">🟢 CPI</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• Core PPI m/m<br>• WTI Crude Oil<br>• NY Fed Expect.<br>• ISM Prices Paid<br>• Import Prices</div></div>
    <div style="min-width: 200px; border-left: 4px solid #FF9800; padding-left: 10px; background-color: rgba(255,152,0,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #FF9800; font-size: 14px;">🟠 NFP</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• ADP Employment<br>• ISM Services Emp.<br>• JOLTs Job Openings<br>• Initial Jobless Claims<br>• Challenger Job Cuts</div></div>
    <div style="min-width: 200px; border-left: 4px solid #E040FB; padding-left: 10px; background-color: rgba(224,64,251,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #E040FB; font-size: 14px;">🟣 Core PCE</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• Core CPI m/m<br>• Core PPI m/m<br>• Avg Hourly Earnings<br>• Retail Sales m/m</div></div>
    <div style="min-width: 200px; border-left: 4px solid #2979FF; padding-left: 10px; background-color: rgba(41,121,255,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #2979FF; font-size: 14px;">🔵 Advance GDP</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• Atlanta Fed GDPNow<br>• Retail Sales (Q. Avg)<br>• Trade Balance<br>• ISM Composite PMI<br>• Durable Goods Orders</div></div>
    <div style="min-width: 200px; border-left: 4px solid #FF5252; padding-left: 10px; background-color: rgba(255,82,82,0.03); padding-top: 10px; padding-bottom: 10px; padding-right: 5px; border-radius: 4px;"><b style="color: #FF5252; font-size: 14px;">🔴 FOMC Decision</b><div style="font-size: 12px; color: #b0b0b0; margin-top: 5px; line-height: 1.4;">• CME FedWatch<br>• Core PCE/CPI Trend<br>• Labor Market Data<br>• Recent Fedspeak<br>• Financial Conditions</div></div>
    </div>"""
    st.markdown(cmap_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
      { "colorTheme": "dark", "isTransparent": true, "width": "100%", "height": "800", "locale": "en", "importanceFilter": "0,1", "countryFilter": "us" }
      </script></div>
    """, height=800, scrolling=True)

# --- NEW TAB: TRADING JOURNAL ---
with tab3:
    st.header("📓 My Trading Journal" if lang == "English" else "📓 මගේ ට්‍රේඩින් ජර්නල් එක")
    
    if len(st.session_state['journal']) == 0:
        st.info("Your journal is empty. Go to the 'Live Predictor' tab, analyze a news event, and click 'Save to Journal'!" if lang == "English" else "ජර්නල් එක හිස්. Live Predictor එකෙන් ඩේටා විශ්ලේෂණය කරලා 'Save to Journal' ඔබන්න!")
    else:
        st.markdown("---")
        h1, h2, h3, h4, h5 = st.columns([2, 3, 2, 3, 1.2]) 
        marker = '<span class="journal-row-marker" style="display:none;"></span>'
        h1.markdown(f"{marker}<div class='journal-header'><b>Date/Time</b></div>" if lang == "English" else f"{marker}<div class='journal-header'><b>දිනය/වේලාව</b></div>", unsafe_allow_html=True)
        h2.markdown("<div class='journal-header'><b>Event</b></div>" if lang == "English" else "<div class='journal-header'><b>නිවුස් එක</b></div>", unsafe_allow_html=True)
        h3.markdown("<div class='journal-header'><b>Score</b></div>" if lang == "English" else "<div class='journal-header'><b>ලකුණ</b></div>", unsafe_allow_html=True)
        h4.markdown("<div class='journal-header'><b>Direction</b></div>" if lang == "English" else "<div class='journal-header'><b>දිශාව</b></div>", unsafe_allow_html=True)
        h5.markdown("<div class='journal-header'><b>Action</b></div>" if lang == "English" else "<div class='journal-header'><b>වෙනස්</b></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        for i, entry in enumerate(st.session_state['journal']):
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 3, 1.2])
            
            short_date = entry['Date & Time'][5:]
            short_event = entry['News Event'].split(" (")[0]
            pred_short = entry['Predicted Direction'].replace(" DXY", "").replace(" / VOLATILE", "")
            
            c1.markdown(f"<div class='journal-text'>{marker}{short_date}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='journal-text'>{short_event}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='journal-text'>{entry['DXY Score']}</div>", unsafe_allow_html=True)
            
            pred = entry["Predicted Direction"]
            if "BULLISH" in pred: color, svg = "#00ffcc", svg_bullish
            elif "BEARISH" in pred: color, svg = "#ff4b4b", svg_bearish
            else: color, svg = "#FFC107", svg_ranging
                
            svg_small = svg.replace('width="24"', 'width="16"').replace('height="24"', 'height="16"')
            
            pred_html = f"""<div style="display: flex; align-items: center; gap: 4px; padding-top: 5px;"><span class='pred-text' style="font-size: 13px; font-weight: bold; color: {color};">{pred_short}</span><div class='pred-icon' style="display: flex; align-items: center;">{svg_small}</div></div>"""
            c4.markdown(pred_html, unsafe_allow_html=True)
            
            btn_col1, btn_col2 = c5.columns(2)
            
            if btn_col1.button("🔄", key=f"load_btn_{entry['id']}", help="Load this entry" if lang == "English" else "දත්ත නැවත Load කරන්න"):
                st.session_state['loaded_data'] = entry
                st.session_state['load_counter'] += 1 
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
                
        # --- FIXED ALIGNMENT ACTION BUTTONS ---
        st.markdown("<br>", unsafe_allow_html=True)
        dl_col, clr_col = st.columns(2)
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
            st.write("**Scenario:** US Inflation hit 9.1% (40-year highs).\n* **Leading Data:** PPI surging. Energy skyrocketing. Import prices massive.\n* **Prediction Tool Score:** 100% Bullish (DXY).\n* **Result:** Fed aggressive hikes. DXY 20-year high.")
        with st.expander("📌 Case Study 2: The Dovish Pivot Expectations (Late 2023 FOMC)"):
            st.write("**Scenario:** Inflation cooling to 3%.\n* **Leading Data:** Core PCE drops. Fedspeak dovish.\n* **Prediction Tool Score:** 35% Bearish (DXY).\n* **Result:** DXY dumped aggressively, Gold/Indices all-time highs.")
    else:
        st.header("📚 අතීත සිදුවීම් අධ්‍යයනය")
        st.write("අතීතයේ ආර්ථික දත්ත ඩොලරයට බලපාපු විදිය මෙතනින් අධ්‍යයනය කරන්න.")
        with st.expander("📌 1 වන අධ්‍යයනය: පශ්චාත්-කොවිඩ් උද්ධමන කම්පනය (2022 CPI)"):
            st.write("**තත්ත්වය:** ඇමෙරිකානු උද්ධමනය 9.1% දක්වා ඉහළ ගියේය.\n* **පෙරගමන් දත්ත:** බලශක්ති මිල, ආනයන මිල සහ PPI විශාල ලෙස ඉහළ ගොස් තිබුණි.\n* **පුරෝකථන මෙවලමේ ලකුණ:** 100% Bullish (DXY).\n* **ප්‍රතිඵලය:** DXY දර්ශකය වසර 20ක උපරිම අගය වූ 114.78 දක්වා ඉහළ ගියේය.")
        with st.expander("📌 2 වන අධ්‍යයනය: Dovish Pivot අපේක්ෂාවන් (2023 අගභාගයේ FOMC)"):
            st.write("**තත්ත්වය:** උද්ධමනය 3% දක්වා වේගයෙන් පහත වැටෙමින් තිබුණි.\n* **පෙරගමන් දත්ත:** Core PCE අඛණ්ඩව පහත වැටෙන බව පෙන්නුම් කළේය.\n* **පුරෝකථන මෙවලමේ ලකුණ:** 35% Bearish (DXY).\n* **ප්‍රතිඵලය:** DXY දර්ශකය වේගයෙන් කඩා වැටුණු අතර, Gold/US Indices උපරිම අගයන් දක්වා ඉහළ ගියේය.")
