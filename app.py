import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime
import base64
import os

st.set_page_config(page_title="Macro DXY Predictor Pro", page_icon="📈", layout="wide")

# Initialize Session States
if 'journal' not in st.session_state:
    st.session_state['journal'] = []
if 'loaded_data' not in st.session_state:
    st.session_state['loaded_data'] = None

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
    
    /* Save Button Stylish & Compact */
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid #1f77b4 !important;
        background-color: transparent !important;
        color: #1f77b4 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: #1f77b4 !important;
        color: white !important;
        transform: scale(1.05);
    }
    
    /* Ultra-Compact & Elegant Circular Delete Button */
    button[title="Delete this entry"] {
        width: 20px !important; height: 20px !important;
        min-height: 20px !important; min-width: 20px !important;
        padding: 0 !important; border-radius: 50% !important; 
        background-color: transparent !important; color: #ff4b4b !important; 
        border: 1px solid #ff4b4b !important; 
        display: inline-flex !important; align-items: center !important; justify-content: center !important;
        transition: all 0.2s ease !important;
    }
    button[title="Delete this entry"]:hover {
        background-color: #ff4b4b !important; color: white !important; transform: scale(1.1) !important;
    }
    button[title="Delete this entry"] div, button[title="Delete this entry"] p {
        margin: 0 !important; padding: 0 !important; line-height: 1 !important; font-size: 10px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        width: 100% !important; height: 100% !important; color: inherit !important;
    }

    /* Ultra-Compact & Elegant Circular LOAD Button */
    button[title="Load this entry"] {
        width: 20px !important; height: 20px !important;
        min-height: 20px !important; min-width: 20px !important;
        padding: 0 !important; border-radius: 50% !important; 
        background-color: transparent !important; color: #1f77b4 !important; 
        border: 1px solid #1f77b4 !important; 
        display: inline-flex !important; align-items: center !important; justify-content: center !important;
        transition: all 0.2s ease !important;
    }
    button[title="Load this entry"]:hover {
        background-color: #1f77b4 !important; color: white !important; transform: scale(1.1) !important;
    }
    button[title="Load this entry"] div, button[title="Load this entry"] p {
        margin: 0 !important; padding: 0 !important; line-height: 1 !important; font-size: 10px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        width: 100% !important; height: 100% !important; color: inherit !important;
    }
    </style>
""", unsafe_allow_html=True)

def create_gauge_chart(score):
    if score >= 60:
        bar_color = "#00ffcc" 
        gauge_title = "Bullish Strength 🚀"
    elif score <= 40:
        bar_color = "#ff4b4b" 
        gauge_title = "Bearish Strength 📉"
    else:
        bar_color = "#ffc107" 
        gauge_title = "Neutral / Volatile ⚖️"

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

# Helper function to save predictions WITH EXACT INPUTS
def save_to_journal(event_name, score, direction_text, inputs_dict):
    entry = {
        "Date & Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "News Event": event_name,
        "DXY Score": f"{score}%",
        "Predicted Direction": direction_text,
        "Inputs": inputs_dict 
    }
    st.session_state['journal'].append(entry)
    st.toast(f"✅ Saved to Journal!")

# Helper to safely set Selectbox Index when Loading
def get_idx(event_name, input_key, options_list):
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] == event_name:
        val = st.session_state['loaded_data']['Inputs'].get(input_key)
        if val in options_list:
            return options_list.index(val)
    return 0

# Helper to safely set Number Input when Loading
def get_num_val(event_name, input_key, default_val):
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] == event_name:
        return st.session_state['loaded_data']['Inputs'].get(input_key, default_val)
    return default_val

# --- Custom SVG Icons Definition ---
svg_bullish = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#4CAF50"/><path d="M7 15 L10.5 11.5 L13 14 L17 9 M13 9 H17 V13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
svg_bearish = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#F44336"/><path d="M7 9 L10.5 12.5 L13 10 L17 15 M13 15 H17 V11" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
svg_ranging = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#FFC107"/><path d="M8 10 L6 12 L8 14 M16 10 L18 12 L16 14 M6 12 H18" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
svg_volatile = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="12" fill="#FF9800"/><path d="M13 5 L7 13 H12 L11 19 L17 11 H12 L13 5 Z" fill="white" stroke="white" stroke-linejoin="round"/></svg>'''

def render_custom_metric(label, value, svg_icon):
    return f"""
    <div style="display: flex; flex-direction: column; margin-bottom: 10px;">
        <div style="font-size: 12px; color: #a0a0a0; margin-bottom: 5px; white-space: nowrap;">{label}</div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="font-size: 16px; font-weight: bold; color: white;">{value}</div>
            <div style="display: flex; align-items: center;">{svg_icon}</div>
        </div>
    </div>
    """

st.title("📈 Ultimate Macro Indicator & Market Predictor")
st.write("Institutional-grade fundamental analysis & educational tool for DXY, Pairs & Indices.")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🔮 Live Predictor", "📓 Trading Journal", "📚 Historical Case Studies"])

with tab1:
    st.sidebar.header("📅 Select Major News Event")
    
    events_list = ["CPI (Consumer Price Index)", "NFP (Non-Farm Payrolls)", "Core PCE Price Index", "Advance GDP", "FOMC Rate Decision"]
    default_event_idx = 0
    if st.session_state['loaded_data'] and st.session_state['loaded_data']['News Event'] in events_list:
        default_event_idx = events_list.index(st.session_state['loaded_data']['News Event'])

    major_news = st.sidebar.radio("Choose Event:", events_list, index=default_event_idx)

    # --- Bull Matrix Personal Branding Footer ---
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    logo_path = "Bull-Matrix-logo.svg"
    if os.path.exists(logo_path):
        with open(logo_path, "r") as f:
            svg_data = f.read()
        b64_svg = base64.b64encode(svg_data.encode("utf-8")).decode("utf-8")
        # Inverting colors via CSS to make the black SVG white/bright on the dark sidebar
        logo_html = f'''
        <div style="text-align: center; margin-bottom: -10px;">
            <img src="data:image/svg+xml;base64,{b64_svg}" width="65%" style="filter: invert(1) brightness(2);">
        </div>
        '''
        st.sidebar.markdown(logo_html, unsafe_allow_html=True)
        
    st.sidebar.markdown("""
    <div style="text-align: center;">
        <p style="font-size: 22px; font-weight: 800; color: white; margin-bottom: 0px; letter-spacing: 1.5px;">BULL MATRIX</p>
        <p style="font-size: 13px; color: #00ffcc; font-weight: bold; margin-bottom: 15px;">Macro Trader & Educator</p>
        <div style="background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 12px; color: #d0d0d0; line-height: 1.4; margin-bottom: 0; font-style: italic;">
                "Decoding the macroeconomic matrix to empower traders with institutional-grade insights."
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

        st.subheader("🗺️ Expected Impact on Major Pairs & Gold")
        p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns(5)
        p_col1.markdown(render_custom_metric("EUR/USD", eurusd_val, eurusd_svg), unsafe_allow_html=True)
        p_col2.markdown(render_custom_metric("GBP/USD", gbpusd_val, gbpusd_svg), unsafe_allow_html=True)
        p_col3.markdown(render_custom_metric("XAU/USD (Gold)", xauusd_val, xauusd_svg), unsafe_allow_html=True)
        p_col4.markdown(render_custom_metric("USD/JPY", usdjpy_val, usdjpy_svg), unsafe_allow_html=True)
        p_col5.markdown(render_custom_metric("USD/CAD", usdcad_val, usdcad_svg), unsafe_allow_html=True)
        st.markdown("") 
        st.subheader("📊 Expected Impact on Major US Indices")
        i_col1, i_col2, i_col3 = st.columns(3)
        i_col1.markdown(render_custom_metric("NASDAQ (NAS100)", nas100_val, nas100_svg), unsafe_allow_html=True)
        i_col2.markdown(render_custom_metric("US30 (Dow Jones)", us30_val, us30_svg), unsafe_allow_html=True)
        i_col3.markdown(render_custom_metric("S&P 500 (SPX500)", spx500_val, spx500_svg), unsafe_allow_html=True)

    def render_save_button(event_name, score, direction, inputs_dict):
        st.markdown("<br>", unsafe_allow_html=True)
        empty_col, btn_col = st.columns([3, 1.5])
        with btn_col:
            if st.button("💾 Save to Journal", key=f"btn_{event_name}"):
                save_to_journal(event_name, score, direction.replace("🚀", "").replace("📉", "").replace("⚖️", "").strip(), inputs_dict)

    # ----------------- 1. CPI CALCULATOR -----------------
    if major_news == "CPI (Consumer Price Index)":
        st.header("🧮 CPI Leading Data Calculator")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_ppi = ["Higher than Consensus", "Neutral", "Lower than Consensus"]
        opt_gas = ["Rising (Inflationary)", "Stable", "Falling (Deflationary)"]
        opt_nyfed = ["Increased", "Unchanged", "Decreased"]
        opt_pmi = ["Increasing Rapidly (>55)", "Neutral", "Decreasing (<50)"]
        opt_imp = ["Rising", "Stable", "Falling"]
        
        with col_left:
            st.subheader("📥 Input Sub-Report Data")
            col_prev, col_fc = st.columns(2)
            with col_prev:
                cpi_previous = st.number_input("📉 Previous Value (%):", value=get_num_val(major_news, "cpi_prev", 3.1), step=0.1, format="%.1f")
            with col_fc:
                cpi_forecast = st.number_input("📊 Market Forecast (%):", value=get_num_val(major_news, "cpi_fc", 2.9), step=0.1, format="%.1f")
            st.markdown("<br>", unsafe_allow_html=True)
            
            ppi_input = st.selectbox("1. PPI Trend:", opt_ppi, index=get_idx(major_news, "ppi", opt_ppi))
            gasoline = st.selectbox("2. Gasoline / Energy Prices:", opt_gas, index=get_idx(major_news, "gas", opt_gas))
            ny_fed = st.selectbox("3. NY Fed 1-Yr Inflation Expectations:", opt_nyfed, index=get_idx(major_news, "nyfed", opt_nyfed))
            pmi_prices = st.selectbox("4. ISM Services/Mfg Prices Paid:", opt_pmi, index=get_idx(major_news, "pmi", opt_pmi))
            import_prices = st.selectbox("5. Import Prices:", opt_imp, index=get_idx(major_news, "imp", opt_imp))
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader("🔮 Live Market Prediction")
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
            render_save_button("CPI (Consumer Price Index)", score, direction, inputs_dict)
            
            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.15); margin: 25px 0;'/>", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.3 
            exp_value = cpi_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > cpi_previous:
                    dev_signal = "🚀 Hotter & Accelerating (Strong Bullish)"
                    dev_desc = "Actual inflation exceeds both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Hotter BUT Cooling (Fakeout Warning)"
                    dev_desc = "Inflation beat expectations but remains below the previous month's level. Exercise caution as this may lead to short-term volatility."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < cpi_previous:
                    dev_signal = "📉 Cooler & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise in inflation figures. This is a primary bearish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Cooler BUT Sticky (Fakeout Warning)"
                    dev_desc = "Inflation is lower than forecast but shows stickiness relative to the previous month. Potential for a 'fakeout' market reversal."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Inflation figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior."

            lower_bound = exp_value - 0.05
            upper_bound = exp_value + 0.05
            
            st.markdown(f"""
            <div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;">
                <div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    🤖 <b>AI Advanced Forecast Radar</b>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="text-align: left;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div>
                        <div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{cpi_previous:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div>
                        <div style="font-size: 22px; font-weight: bold; color: white;">{cpi_forecast:.1f}%</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected Range</div>
                        <div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div>
                    </div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                    <div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">
                        {dev_signal}
                    </div>
                    <div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">
                        {dev_desc}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ----------------- 2. NFP CALCULATOR -----------------
    elif major_news == "NFP (Non-Farm Payrolls)":
        st.header("💼 NFP Leading Data Calculator")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_adp = ["Strong Beat", "Neutral / As Expected", "Big Miss"]
        opt_ism = ["Expanding (>50)", "Neutral", "Contracting (<50)"]
        opt_jolts = ["Increasing (Strong Demand)", "Neutral", "Decreasing (Weak Demand)"]
        opt_jobless = ["Consistently Low (<200k)", "Neutral", "Rising Rapidly (>250k)"]
        opt_chal = ["Low Layoffs", "Average", "High Layoffs"]
        
        with col_left:
            st.subheader("📥 Input Sub-Report Data")
            col_prev, col_fc = st.columns(2)
            with col_prev:
                nfp_previous = st.number_input("📉 Previous Value (k):", value=int(get_num_val(major_news, "nfp_prev", 200)), step=10, format="%d")
            with col_fc:
                nfp_forecast = st.number_input("📊 Market Forecast (k):", value=int(get_num_val(major_news, "nfp_fc", 180)), step=10, format="%d")
            st.markdown("<br>", unsafe_allow_html=True)

            adp_input = st.selectbox("1. ADP Employment Change:", opt_adp, index=get_idx(major_news, "adp", opt_adp))
            ism_services = st.selectbox("2. ISM Services Employment:", opt_ism, index=get_idx(major_news, "ism", opt_ism))
            jolts = st.selectbox("3. JOLTs Job Openings:", opt_jolts, index=get_idx(major_news, "jolts", opt_jolts))
            jobless = st.selectbox("4. Initial Jobless Claims:", opt_jobless, index=get_idx(major_news, "jobless", opt_jobless))
            challenger = st.selectbox("5. Challenger Job Cuts:", opt_chal, index=get_idx(major_news, "chal", opt_chal))
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader("🔮 Live Market Prediction")
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
            render_save_button("NFP (Non-Farm Payrolls)", score, direction, inputs_dict)

            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.15); margin: 25px 0;'/>", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 50.0 
            exp_value = nfp_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > nfp_previous:
                    dev_signal = "🚀 Strong Beat & Accelerating (Strong Bullish)"
                    dev_desc = "Employment data is projected to exceed both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Beat BUT Decelerating (Fakeout Warning)"
                    dev_desc = "Data is projected to beat expectations but remains below previous levels. Exercise caution as this may lead to short-term volatility."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < nfp_previous:
                    dev_signal = "📉 Big Miss & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise projected. Figures fall below both forecasts and previous data, acting as a primary bearish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Miss BUT Sticky (Fakeout Warning)"
                    dev_desc = "Data misses forecasts but shows stickiness relative to previous figures. Potential for a 'fakeout' market reversal."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Employment figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior."

            lower_bound = exp_value - 10
            upper_bound = exp_value + 10
            
            st.markdown(f"""
            <div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;">
                <div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    🤖 <b>AI Advanced Forecast Radar</b>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="text-align: left;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div>
                        <div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{nfp_previous}k</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div>
                        <div style="font-size: 22px; font-weight: bold; color: white;">{nfp_forecast}k</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected Range</div>
                        <div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.0f}k - {upper_bound:.0f}k</div>
                    </div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                    <div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">
                        {dev_signal}
                    </div>
                    <div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">
                        {dev_desc}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ----------------- 3. CORE PCE CALCULATOR -----------------
    elif major_news == "Core PCE Price Index":
        st.header("🛒 Core PCE Leading Data Calculator")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_cpi = ["Hotter than Expected", "Neutral", "Cooler than Expected"]
        opt_ppi = ["Hotter than Expected", "Neutral", "Cooler than Expected"]
        opt_hr = ["Rising Faster", "Stable", "Cooling Down"]
        opt_ret = ["Strong (High Spending)", "Neutral", "Weak (Low Spending)"]

        with col_left:
            st.subheader("📥 Input Sub-Report Data")
            col_prev, col_fc = st.columns(2)
            with col_prev:
                pce_previous = st.number_input("📉 Previous Value (%):", value=get_num_val(major_news, "pce_prev", 0.3), step=0.1, format="%.1f")
            with col_fc:
                pce_forecast = st.number_input("📊 Market Forecast (%):", value=get_num_val(major_news, "pce_fc", 0.2), step=0.1, format="%.1f")
            st.markdown("<br>", unsafe_allow_html=True)

            cpi_input = st.selectbox("1. Recent Core CPI Release:", opt_cpi, index=get_idx(major_news, "cpi", opt_cpi))
            ppi_input = st.selectbox("2. Recent Core PPI Release:", opt_ppi, index=get_idx(major_news, "ppi", opt_ppi))
            hourly_earnings = st.selectbox("3. Average Hourly Earnings:", opt_hr, index=get_idx(major_news, "hr", opt_hr))
            retail_sales = st.selectbox("4. Retail Sales / Personal Income:", opt_ret, index=get_idx(major_news, "ret", opt_ret))
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader("🔮 Live Market Prediction")
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
            render_save_button("Core PCE Price Index", score, direction, inputs_dict)

            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.15); margin: 25px 0;'/>", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.2 
            exp_value = pce_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > pce_previous:
                    dev_signal = "🚀 Hotter & Accelerating (Strong Bullish)"
                    dev_desc = "Actual inflation exceeds both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Hotter BUT Cooling (Fakeout Warning)"
                    dev_desc = "Inflation beat expectations but remains below the previous month's level. Exercise caution as this may lead to short-term volatility."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < pce_previous:
                    dev_signal = "📉 Cooler & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise in inflation figures. This is a primary bearish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Cooler BUT Sticky (Fakeout Warning)"
                    dev_desc = "Inflation is lower than forecast but shows stickiness relative to the previous month. Potential for a 'fakeout' market reversal."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Inflation figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior."

            lower_bound = exp_value - 0.05
            upper_bound = exp_value + 0.05
            
            st.markdown(f"""
            <div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;">
                <div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    🤖 <b>AI Advanced Forecast Radar</b>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="text-align: left;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div>
                        <div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{pce_previous:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div>
                        <div style="font-size: 22px; font-weight: bold; color: white;">{pce_forecast:.1f}%</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected Range</div>
                        <div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div>
                    </div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                    <div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">
                        {dev_signal}
                    </div>
                    <div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">
                        {dev_desc}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ----------------- 4. ADVANCE GDP CALCULATOR -----------------
    elif major_news == "Advance GDP":
        st.header("🏭 Advance GDP Leading Data Calculator")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_atl = ["Tracking High (>2.5%)", "Neutral", "Tracking Low (<1.0%)"]
        opt_ret = ["Strongly Positive", "Neutral", "Negative"]
        opt_trade = ["Deficit Shrinking (Good)", "Neutral", "Deficit Widening (Bad)"]
        opt_pmi = ["Expanding (>50)", "Neutral (~50)", "Contracting (<50)"]
        opt_dur = ["Rising", "Neutral", "Falling"]

        with col_left:
            st.subheader("📥 Input Sub-Report Data")
            col_prev, col_fc = st.columns(2)
            with col_prev:
                gdp_previous = st.number_input("📉 Previous Value (%):", value=get_num_val(major_news, "gdp_prev", 2.1), step=0.1, format="%.1f")
            with col_fc:
                gdp_forecast = st.number_input("📊 Market Forecast (%):", value=get_num_val(major_news, "gdp_fc", 1.8), step=0.1, format="%.1f")
            st.markdown("<br>", unsafe_allow_html=True)

            atlanta_fed = st.selectbox("1. Atlanta Fed GDPNow Tracker:", opt_atl, index=get_idx(major_news, "atl", opt_atl))
            retail_input = st.selectbox("2. Retail Sales (Quarterly Average):", opt_ret, index=get_idx(major_news, "ret", opt_ret))
            trade_balance = st.selectbox("3. Trade Balance (Net Exports):", opt_trade, index=get_idx(major_news, "trade", opt_trade))
            pmi_input = st.selectbox("4. ISM Composite PMI:", opt_pmi, index=get_idx(major_news, "pmi", opt_pmi))
            durable_goods = st.selectbox("5. Durable Goods Orders:", opt_dur, index=get_idx(major_news, "dur", opt_dur))
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader("🔮 Live Market Prediction")
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
            render_save_button("Advance GDP", score, direction, inputs_dict)

            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.15); margin: 25px 0;'/>", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.5 
            exp_value = gdp_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value > gdp_previous:
                    dev_signal = "🚀 Stronger & Accelerating (Strong Bullish)"
                    dev_desc = "Economic growth exceeds both market forecasts and previous figures. This represents a strong bullish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Stronger BUT Cooling (Fakeout Warning)"
                    dev_desc = "Growth beat expectations but remains below the previous quarter's level. Exercise caution as this may lead to short-term volatility."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < gdp_previous:
                    dev_signal = "📉 Weaker & Decelerating (Strong Bearish)"
                    dev_desc = "Significant downside surprise in economic growth. This is a primary bearish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Weaker BUT Sticky (Fakeout Warning)"
                    dev_desc = "Growth is lower than forecast but shows stickiness relative to the previous quarter. Potential for a 'fakeout' market reversal."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Consensus (Neutral)"
                dev_desc = "Growth figures are aligned with market expectations. Anticipate consolidation or range-bound trading behavior."

            lower_bound = exp_value - 0.1
            upper_bound = exp_value + 0.1
            
            st.markdown(f"""
            <div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;">
                <div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    🤖 <b>AI Advanced Forecast Radar</b>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="text-align: left;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous</div>
                        <div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{gdp_previous:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div>
                        <div style="font-size: 22px; font-weight: bold; color: white;">{gdp_forecast:.1f}%</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected Range</div>
                        <div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div>
                    </div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                    <div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">
                        {dev_signal}
                    </div>
                    <div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">
                        {dev_desc}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ----------------- 5. FOMC RATE DECISION CALCULATOR -----------------
    elif major_news == "FOMC Rate Decision":
        st.header("🦅 FOMC Rate Decision & Statement")
        col_left, col_mid, col_right = st.columns([20, 1, 30])
        opt_fed = ["Pricing Hawk (Hike/Hold)", "Mixed", "Pricing Dove (Cut)"]
        opt_inf = ["Sticky / Rising", "Neutral", "Falling Rapidly"]
        opt_lab = ["Tight (Strong Jobs)", "Neutral", "Cooling (Weak Jobs)"]
        opt_speak = ["Hawkish Rhetoric", "Neutral", "Dovish Rhetoric"]
        opt_fin = ["Loose (Requires Tightening)", "Neutral", "Tight (Requires Easing)"]

        with col_left:
            st.subheader("📥 Input Sub-Report Data")
            col_prev, col_fc = st.columns(2)
            with col_prev:
                fomc_previous = st.number_input("📉 Previous Rate (%):", value=get_num_val(major_news, "fomc_prev", 5.50), step=0.25, format="%.2f")
            with col_fc:
                fomc_forecast = st.number_input("📊 Market Forecast (%):", value=get_num_val(major_news, "fomc_fc", 5.25), step=0.25, format="%.2f")
            st.markdown("<br>", unsafe_allow_html=True)

            fedwatch = st.selectbox("1. CME FedWatch Probability:", opt_fed, index=get_idx(major_news, "fed", opt_fed))
            inflation = st.selectbox("2. Recent Core PCE/CPI Trend:", opt_inf, index=get_idx(major_news, "inf", opt_inf))
            labor = st.selectbox("3. Recent Labor Market (NFP/JOLTs):", opt_lab, index=get_idx(major_news, "lab", opt_lab))
            fedspeak = st.selectbox("4. Recent Fedspeak / Dot Plot:", opt_speak, index=get_idx(major_news, "speak", opt_speak))
            fin_conditions = st.selectbox("5. Financial Conditions Index:", opt_fin, index=get_idx(major_news, "fin", opt_fin))
            
        with col_mid: st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
            
        with col_right:
            st.subheader("🔮 Live Market Prediction")
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
            render_save_button("FOMC Rate Decision", score, direction, inputs_dict)

            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.15); margin: 25px 0;'/>", unsafe_allow_html=True)

            deviation = (score - 50) / 50.0 * 0.25 
            exp_value = fomc_forecast + deviation
            
            if score >= 60:
                dev_color = "#00ffcc"
                if exp_value >= fomc_previous:
                    dev_signal = "🦅 Hawkish Hike / Hold (Strong Bullish)"
                    dev_desc = "Rate projections exceed or maintain previous high levels. This represents a strong bullish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Hawkish rhetoric BUT Rate Capped (Fakeout)"
                    dev_desc = "Rhetoric is hawkish but actual rate projection remains below previous highs. Watch for short-term volatility."
            elif score <= 40:
                dev_color = "#ff4b4b"
                if exp_value < fomc_previous:
                    dev_signal = "🕊️ Dovish Cut & Accelerating (Strong Bearish)"
                    dev_desc = "Aggressive rate cuts projected compared to previous levels. This is a primary bearish catalyst for the DXY."
                else:
                    dev_signal = "⚖️ Dovish rhetoric BUT Sticky Rates (Fakeout)"
                    dev_desc = "Rhetoric is dovish but actual rate projections hold higher than expected. Potential for a 'fakeout' market reversal."
            else:
                dev_color = "#FFC107"
                dev_signal = "⚖️ In-line with Market Pricing (Neutral)"
                dev_desc = "Rate decisions and rhetoric are aligned with market expectations. Anticipate range-bound trading behavior."

            lower_bound = exp_value - 0.05
            upper_bound = exp_value + 0.05
            
            st.markdown(f"""
            <div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px;">
                <div style="font-size: 14px; color: #a0a0a0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    🤖 <b>AI Advanced Forecast Radar</b>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="text-align: left;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Previous Rate</div>
                        <div style="font-size: 22px; font-weight: bold; color: #a0a0a0;">{fomc_previous:.2f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">Forecast</div>
                        <div style="font-size: 22px; font-weight: bold; color: white;">{fomc_forecast:.2f}%</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 11px; color: gray; text-transform: uppercase;">AI Expected Rate</div>
                        <div style="font-size: 22px; font-weight: bold; color: {dev_color};">{lower_bound:.2f}% - {upper_bound:.2f}%</div>
                    </div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
                    <div style="font-size: 14px; color: {dev_color}; font-weight: bold; text-align: center; margin-bottom: 5px;">
                        {dev_signal}
                    </div>
                    <div style="font-size: 12px; color: #d0d0d0; text-align: center; line-height: 1.4;">
                        {dev_desc}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- NEW TAB: TRADING JOURNAL ---
with tab2:
    st.header("📓 My Trading Journal")
    st.write("Review your saved predictions or load them back into the calculator.")
    
    if len(st.session_state['journal']) == 0:
        st.info("Your journal is empty. Go to the 'Live Predictor' tab, analyze a news event, and click 'Save to Journal'!")
    else:
        st.markdown("---")
        h1, h2, h3, h4, h5 = st.columns([2, 3, 2, 3, 1.2]) 
        h1.markdown("**Date & Time**")
        h2.markdown("**News Event**")
        h3.markdown("**DXY Score**")
        h4.markdown("**Prediction**")
        h5.markdown("**Actions**")
        st.markdown("---")
        
        for i, entry in enumerate(st.session_state['journal']):
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 3, 1.2])
            
            row_style = "font-size: 14px; color: #d0d0d0; padding-top: 5px;"
            c1.markdown(f"<div style='{row_style}'>{entry['Date & Time']}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='{row_style}'>{entry['News Event']}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='{row_style}'>{entry['DXY Score']}</div>", unsafe_allow_html=True)
            
            pred = entry["Predicted Direction"]
            if "BULLISH" in pred: color, svg = "#00ffcc", svg_bullish
            elif "BEARISH" in pred: color, svg = "#ff4b4b", svg_bearish
            else: color, svg = "#FFC107", svg_ranging
                
            svg_small = svg.replace('width="24"', 'width="18"').replace('height="24"', 'height="18"')
            
            pred_html = f"""
            <div style="display: flex; align-items: center; gap: 8px; padding-top: 5px;">
                <span style="font-size: 14px; font-weight: bold; color: {color};">{pred}</span>
                <div style="display: flex; align-items: center;">{svg_small}</div>
            </div>
            """
            c4.markdown(pred_html, unsafe_allow_html=True)
            
            btn_col1, btn_col2 = c5.columns(2)
            
            if btn_col1.button("🔄", key=f"load_btn_{i}", help="Load this entry"):
                st.session_state['loaded_data'] = entry
                st.toast("✅ Data Loaded! Go to the 'Live Predictor' tab.")
                st.rerun()
                
            if btn_col2.button("✖", key=f"del_btn_{i}", help="Delete this entry"):
                st.session_state['journal'].pop(i)
                st.rerun()
            
            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.1); margin: 12px 0;'/>", unsafe_allow_html=True)
                
        if st.button("🗑️ Clear All Data", type="primary"):
            st.session_state['journal'] = []
            st.session_state['loaded_data'] = None
            st.rerun()

with tab3:
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