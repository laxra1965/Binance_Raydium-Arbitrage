import streamlit as st
import requests
import time

# -------------------------
# Hardcoded Solana Token Pairs
# -------------------------
TOKEN_PAIRS = [
    "YODA/SOL", "PIPSOL/SOL", "SWEEPY/SOL", "$ROGERS/SOL", "TRA/SOL",
    "ORANGELAD/SOL", "PWEASE/SOL", "KAIREN/SOL", "EWON/SOL", "COCORO/SOL",
    "EDELON/SOL", "JAIL MILEI/SOL", "CASH/SOL", "GOOSE/SOL", "LEOVANCE/SOL",
    "BTCR/SOL", "JDWOMEN/SOL", "TRUMPLEY/SOL", "COCORO/SOL", "PABLO/SOL",
    "DB/SOL", "STORE/SOL", "PI/SOL", "GROKCOIN/SOL", "BLOOP/SOL",
    "JESUS/SOL", "MCUBAN/SOL", "LEONAWDO/SOL", "PIP/SOL", "FATCZ/SOL",
    "GROKCOIN/SOL", "COCORO/SOL", "DORIME/SOL", "PVE/SOL", "PUMPPAY/SOL",
    "DIAMONDS/SOL", "BARRON/SOL", "F/SOL", "DOWE/SOL", "WATER/SOL",
    "JEFF/SOL", "BARRON/SOL", "FARTCLUB/SOL", "ARC/SOL", "YE/SOL",
    "SPX/SOL", "GROKCOIN/SOL", "WINE/SOL", "WPEPE/SOL", "COCORO/SOL",
    "DSX/SOL", "BARRON/SOL", "FRANKIE/SOL", "ELIGIUS/SOL", "TITCOIN/SOL",
    "TELEGRAM/SOL", "YZY/SOL", "WILDNOUT/SOL", "1SOL/SOL", "SPACEX/SOL"
]

# -------------------------
# Binance API Function (UPDATED)
# -------------------------
def get_binance_prices():
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url)

        # Check HTTP status
        if response.status_code != 200:
            st.error(f"Binance API error: {response.status_code}")
            return {}

        data = response.json()

        # Validate data type
        if not isinstance(data, list):
            st.error("Unexpected Binance data format.")
            return {}

        prices = {}
        for item in data:
            if isinstance(item, dict) and "symbol" in item and "price" in item:
                symbol = item["symbol"]
                price = float(item["price"])
                prices[symbol] = price
            else:
                st.warning(f"Unexpected data item from Binance: {item}")

        return prices

    except Exception as e:
        st.error(f"Error fetching Binance prices: {e}")
        return {}

# -------------------------
# Raydium API Function
# -------------------------
def get_raydium_prices():
    try:
        url = "https://api.raydium.io/v2/sdk/liquidity/mainnet.json"
        response = requests.get(url)

        if response.status_code != 200:
            st.error(f"Raydium API error: {response.status_code}")
            return {}

        data = response.json()

        if not isinstance(data, dict) or 'official' not in data:
            st.error("Unexpected Raydium data format.")
            return {}

        prices = {}
        for pool in data['official']:
            pair = f"{pool['base']['symbol']}/{pool['quote']['symbol']}"
            price = float(pool['price']) if 'price' in pool else None
            prices[pair.upper()] = price

        return prices

    except Exception as e:
        st.error(f"Error fetching Raydium prices: {e}")
        return {}

# -------------------------
# Arbitrage Detection Function
# -------------------------
def find_arbitrage(binance_prices, raydium_prices, token_pairs):
    opportunities = []

    for pair in token_pairs:
        token, quote = pair.split("/")
        binance_symbol = f"{token}{quote}".replace("/", "").upper()

        binance_price = binance_prices.get(binance_symbol)
        raydium_price = raydium_prices.get(pair.upper())

        if binance_price and raydium_price:
            diff = raydium_price - binance_price
            diff_percent = (diff / binance_price) * 100

            if abs(diff_percent) > 1:  # Arbitrage threshold %
                opportunities.append({
                    "pair": pair,
                    "binance_price": binance_price,
                    "raydium_price": raydium_price,
                    "diff_percent": round(diff_percent, 2)
                })

    return opportunities

# -------------------------
# Streamlit App UI
# -------------------------
st.title("Solana Arbitrage Scanner")
st.markdown("Scanning for arbitrage opportunities between **Binance** and **Raydium.io**")

refresh_rate = st.slider("Refresh rate (seconds)", 10, 300, 60)

placeholder = st.empty()

while True:
    with placeholder.container():
        st.write("Fetching prices...")

        binance_prices = get_binance_prices()
        raydium_prices = get_raydium_prices()

        if binance_prices and raydium_prices:
            opportunities = find_arbitrage(binance_prices, raydium_prices, TOKEN_PAIRS)

            if opportunities:
                st.success(f"Found {len(opportunities)} arbitrage opportunities!")
                for opp in opportunities:
                    st.markdown(f"""
                        **Pair:** {opp['pair']}
                        - Binance Price: `{opp['binance_price']}`
                        - Raydium Price: `{opp['raydium_price']}`
                        - Difference: `{opp['diff_percent']}%`
                    """)
            else:
                st.warning("No arbitrage opportunities found at this time.")

        else:
            st.error("Error fetching prices. Try again later.")

    time.sleep(refresh_rate)
    st.experimental_rerun()  # Triggers refresh in Streamlit Cloud
