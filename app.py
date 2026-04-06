import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import urllib.parse

# App Config
st.set_page_config(page_title="Gaon Sabzi Bazar", page_icon="🛒", layout="wide")

# Files for Data
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
    message = f"🥬 *GAON SABZI BAZAR - AAJ KE RATE*\n📅 Date: {today}\n\n💰 *RATE LIST*\n"
    for _, row in rates_df.iterrows():
        message += f"🥔 {row['Sabzi']}: ₹{row['Bhao']}/kg\n"
    message += "\n🛒 *Order ke liye niche link par click karein!*"
    return urllib.parse.quote(message)

# --- HEADER ---
st.markdown('# 🍀 Gaon Sabzi Bazar')
st.divider()

user_type = st.sidebar.radio("👤 Aap Kaun Hain?", ["🛍️ Grahak", "🚜 Dukan Malik"])

# --- CUSTOMER SIDE ---
if user_type == "🛍️ Grahak":
    st.header("🛒 Apna Order Likhein")
    rates_df = load_data(RATES_FILE, ["Sabzi", "Bhao"])
    
    with st.form("customer_order"):
        c_name = st.text_input("Naam *")
        c_village = st.selectbox("Gaon", ["Mera Gaon", "Padosi Gaon 1", "Padosi Gaon 2"])
        c_address = st.text_area("Address *")
        c_item = st.selectbox("Sabzi", rates_df["Sabzi"].tolist() if not rates_df.empty else ["No Items"])
        c_qty = st.number_input("Kitna kg?", min_value=0.25, step=0.25)
        
        if st.form_submit_button("🚚 Order Bhejein"):
            if c_name and c_address:
                df = load_data(ORDERS_FILE, ["Date", "Grahak", "Gaon", "Address", "Sabzi", "Vajan", "Total", "Status"])
                rate = rates_df[rates_df["Sabzi"] == c_item]["Bhao"].values[0]
                new_order = {"Date": date.today().strftime("%d/%m/%Y"), "Grahak": c_name, "Gaon": c_village, "Address": c_address, "Sabzi": c_item, "Vajan": c_qty, "Total": c_qty * rate, "Status": "🆕 Naya"}
                df = pd.concat([df, pd.DataFrame([new_order])], ignore_index=True)
                save_data(df, ORDERS_FILE)
                st.success(f"✅ Order Confirm! Total: ₹{c_qty * rate}")

# --- ADMIN SIDE ---
else:
    st.header("🚜 Admin Dashboard")
    rates_df = load_data(RATES_FILE, ["Sabzi", "Bhao"])
    
    # WhatsApp Share Button
    whatsapp_url = f"https://wa.me/?text={create_whatsapp_message(rates_df)}"
    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">📤 WhatsApp par Rate Bhejein</button></a>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📦 Orders", "💰 Rate Manager"])
    with tab1:
        orders_df = load_data(ORDERS_FILE, ["Date", "Grahak", "Gaon", "Address", "Sabzi", "Vajan", "Total", "Status"])
        st.dataframe(orders_df)
    with tab2:
        with st.form("rate_form"):
            s_name = st.text_input("Sabzi ka Naam")
            s_rate = st.number_input("Rate ₹/kg", min_value=1)
            if st.form_submit_button("➕ Update Rate"):
                rates_df = rates_df[rates_df["Sabzi"] != s_name]
                rates_df = pd.concat([rates_df, pd.DataFrame([{"Sabzi": s_name, "Bhao": s_rate}])])
