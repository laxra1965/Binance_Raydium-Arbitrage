import streamlit as st
import requests
import time

# ========== CONFIG ==========
TOKEN_PAIRS = ["SOL/USDT", "RAY/USDT", "SRM/USDT"]
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
RAYDIUM_API_URL = "https://api.raydium.io/pairs"

# ========== FUNCTIONS ==========

def get_binance_prices():
    prices = {}
    try:
        response = requests.get(BINANCE_API_URL)
        data = response.json()
        for item in data:
            symbol = item['symbol']
            for pair in TOKEN_PAIRS:
                token, base = pair.split('/')
                binance_symbol = token + base
                if symbol == binance_symbol:
                    prices[pair] = float(item['price'])
    except Exception as e:
        st.error(f"Error fetching Binance prices: {e}")
    return prices

def get_raydium_prices():
    prices = {}
    try:
        response = requests.get(RAYDIUM_API_URL)
        data = response.json()
        for pair in data:
            market = pair.get("name")  # e.g., SOL/USDC
            if market:
                market_pair = market.replace("USDC", "USDT")
                if market_pair in TOKEN_PAIRS:
                    raydium_price = float(pair.get("price", 0))
                    prices[market_pair] = raydium_price
    except Exception as e:
        st.error(f"Error fetching Raydium prices: {e}")
    return prices

def find_arbitrage(binance_prices, raydium_prices):
    opportunities = []
    for pair in TOKEN_PAIRS:
        binance_price = binance_prices.get(pair)
        raydium_price = raydium_prices.get(pair)
        if binance_price and raydium_price:
            profit_to_raydium = (raydium_price - binance_price) / binance_price * 100
            profit_to_binance = (binance_price - raydium_price) / raydium_price * 100

            if profit_to_raydium > 0.5:
                opportunities.append({
                    "pair": pair,
                    "buy_from": "Binance",
                    "sell_to": "Raydium",
                    "binance_price": binance_price,
                    "raydium_price": raydium_price,
                    "profit_pct": round(profit_to_raydium, 2)
                })
            elif profit_to_binance > 0.5:
                opportunities.append({
                    "pair": pair,
                    "buy_from": "Raydium",
                    "sell_to": "Binance",
                    "binance_price": binance_price,
                    "raydium_price": raydium_price,
                    "profit_pct": round(profit_to_binance, 2)
                })
    return opportunities

def play_audio_alert():
    # Embeds an audio player (HTML5) into Streamlit
    audio_file = open("alert.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

def display_popup(message):
    # Streamlit markdown alert
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 5px; background-color: #FF4136; color: white;">
            <strong>{message}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

# ========== STREAMLIT APP ==========

st.title("Binance ↔ Raydium Arbitrage Scanner with Alerts")
st.write("Scanning Solana tokens for arbitrage opportunities...")

update_interval = st.slider("Refresh interval (seconds)", 5, 60, 10)

# Placeholder for real-time updates
opportunity_placeholder = st.empty()

while True:
    with st.spinner("Fetching latest prices..."):
        binance_prices = get_binance_prices()
        raydium_prices = get_raydium_prices()

        st.subheader("Current Prices")
        st.json({
            "Binance": binance_prices,
            "Raydium": raydium_prices
        })

        opportunities = find_arbitrage(binance_prices, raydium_prices)

        if opportunities:
            opportunity_placeholder.success("🚨 Arbitrage Opportunities Found!")
            for opp in opportunities:
                with st.container():
                    st.write(f"🔔 **{opp['pair']}**")
                    st.write(f"Buy from: **{opp['buy_from']}** at {opp['binance_price'] if opp['buy_from']=='Binance' else opp['raydium_price']}")
                    st.write(f"Sell to: **{opp['sell_to']}** at {opp['raydium_price'] if opp['sell_to']=='Raydium' else opp['binance_price']}")
                    st.write(f"Potential profit: **{opp['profit_pct']}%**")
                    st.markdown("---")

            # Play alert sound
            play_audio_alert()

            # Show popup alert
            display_popup("🚨 Arbitrage opportunity detected!")
        else:
            opportunity_placeholder.warning("No arbitrage opportunities right now.")

    time.sleep(update_interval)
    st.experimental_rerun()
