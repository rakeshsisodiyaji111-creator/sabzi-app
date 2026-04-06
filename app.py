import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import urllib.parse

# App Settings
st.set_page_config(page_title="Gaon Sabzi Bazar", page_icon="🛒", layout="wide")

# Data Files
ORDERS_FILE = "all_orders.csv"
RATES_FILE = "today_rates.csv"

@st.cache_data
def load_data(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

def create_whatsapp_message(rates_df):
    today = date.today().strftime("%d/%m/%Y")
    message = f"🥬 *गाँव सब्जी बाज़ार - आज के भाव*\n📅 तारीख: {today}\n\n💰 *सब्जी रेट लिस्ट*\n"
    for _, row in rates_df.iterrows():
        message += f"🥔 {row['Sabzi']}: ₹{row['Bhao']}/kg\n"
    message += "\n🛒 *ऑर्डर के लिए नीचे लिंक पर क्लिक करें!*"
    return urllib.parse.quote(message)

# --- APP HEADER ---
st.markdown('# 🍀 गाँव सब्जी बाज़ार')
st.divider()

# Sidebar
user_type = st.sidebar.radio("👤 आप कौन हैं?", ["🛍️ ग्राहक (Customer)", "🚜 दुकान मालिक (Admin)"])

# --- GRAHAK SECTION ---
if user_type == "🛍️ ग्राहक (Customer)":
    st.header("🛒 अपना ऑर्डर लिखें")
    rates_df = load_data(RATES_FILE, ["Sabzi", "Bhao"])
    
    if rates_df.empty:
        st.warning("⚠️ अभी रेट लिस्ट खाली है। दुकान मालिक से कहें कि रेट अपडेट करें।")
    else:
        with st.form("customer_order"):
            c_name = st.text_input("आपका नाम *")
            c_village = st.selectbox("आपका गाँव", ["मेरा गाँव", "पड़ोसी गाँव 1", "पड़ोसी गाँव 2"])
            c_address = st.text_area("घर ka पता (Address) *")
            c_item = st.selectbox("सब्जी चुनें", rates_df["Sabzi"].tolist())
            c_qty = st.number_input("कितना किलो (kg) चाहिए?", min_value=0.25, step=0.25)
            
            if st.form_submit_button("🚚 ऑर्डर भेजें"):
                if c_name and c_address:
                    df = load_data(ORDERS_FILE, ["Date", "Grahak", "Gaon", "Address", "Sabzi", "Vajan", "Total", "Status"])
                    rate = rates_df[rates_df["Sabzi"] == c_item]["Bhao"].values[0]
                    new_order = {"Date": date.today().strftime("%d/%m/%Y"), "Grahak": c_name, "Gaon": c_village, "Address": c_address, "Sabzi": c_item, "Vajan": c_qty, "Total": c_qty * rate, "Status": "🆕 नया"}
                    df = pd.concat([df, pd.DataFrame([new_order])], ignore_index=True)
                    save_data(df, ORDERS_FILE)
                    st.success(f"✅ ऑर्डर कन्फर्म! बिल: ₹{c_qty * rate}")
                    st.balloons()
                else:
                    st.error("❌ कृपया नाम और पता भरें!")

# --- ADMIN SECTION ---
else:
    st.header("🚜 दुकान मालिक डैशबोर्ड")
    rates_df = load_data(RATES_FILE, ["Sabzi", "Bhao"])
    
    whatsapp_url = f"https://wa.me/?text={create_whatsapp_message(rates_df)}"
    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 8px; width: 100%; font-size: 16px; cursor: pointer;">📤 व्हाट्सएप पर रेट भेजें</button></a>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📦 नए ऑर्डर", "💰 रेट मैनेजर"])
    with tab1:
        orders_df = load_data(ORDERS_FILE, ["Date", "Grahak", "Gaon", "Address", "Sabzi", "Vajan", "Total", "Status"])
        if not orders_df.empty:
            st.dataframe(orders_df)
        else:
            st.info("अभी कोई नया ऑर्डर नहीं आया है।")

    with tab2:
        with st.form("rate_form"):
            s_name = st.selectbox("सब्जी का नाम चुनें", ["लम्बी ककड़ी", "भिंडी", "गिलकी", "आलू", "प्याज", "टमाटर"])
            s_rate = st.number_input("आज का भाव (₹ प्रति किलो)", min_value=1)
            if st.form_submit_button("➕ रेट अपडेट करें"):
                rates_df = rates_df[rates_df["Sabzi"] != s_name]
                rates_df = pd.concat([rates_df, pd.DataFrame([{"Sabzi": s_name, "Bhao": s_rate}])])
                save_data(rates_df, RATES_FILE)
                st.success(f"✅ {s_name} का रेट ₹{s_rate} सेट हो गया!")
    
