import os
import time
import requests
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# ទាញយក Token និង Chat ID ពី Environment Variables លើ Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """អនុវត្តការផ្ញើសារចូល Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(" Error: Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(" Message sent successfully!")
        else:
            print(f" Failed to send message: {response.text}")
    except Exception as e:
        print(f" Error sending Telegram message: {e}")

def analyze_smc_gold():
    """ទាញយកទិន្នន័យមាស និងវិភាគតាមទ្រឹស្តី SMC"""
    print(" Fetching Gold Market Data (GC=F)...")
    ticker = yf.Ticker("GC=F") # GC=F ជា Symbol មាសលើ Yahoo Finance
    df = ticker.history(period="5d", interval="15m")
    
    if df.empty:
        print(" No data retrieved.")
        return

    # គណនា EMA និង ATR សម្រាប់ជំនួយការវិភាគ
    df['EMA_200'] = ta.ema(df['Close'], length=200)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    latest_close = df['Close'].iloc[-1]
    prev_high = df['High'].iloc[-5:-1].max()
    prev_low = df['Low'].iloc[-5:-1].min()
    
    # ស្វែងរកតំបន់ Liquidity Sweep / Break of Structure (BOS)
    signal = None
    if latest_close > prev_high:
        signal = " BULLISH BOS (Break of Structure)"
    elif latest_close < prev_low:
        signal = " BEARISH BOS (Break of Structure)"
        
    if signal:
        msg = (
            f" **SMC Gold Trading Signal** \n\n"
            f" **Asset**: Gold (XAU/USD)\n"
            f" **Current Price**: ${latest_close:.2f}\n"
            f" **Signal**: {signal}\n"
            f" **RSI (14)**: {df['RSI'].iloc[-1]:.2f}\n\n"
            f" Please manage your risk carefully!"
        )
        send_telegram_message(msg)

if __name__ == "__main__":
    send_telegram_message(" **SMC Gold Telegram Bot is now LIVE on Render!**")
    
    # រត់ពិនិត្យទីផ្សាររៀងរាល់ ១៥ នាទីម្តង
    while True:
        try:
            analyze_smc_gold()
        except Exception as e:
            print(f"Error during execution: {e}")
        time.sleep(900)  # 900 វិនាទី = ១៥ នាទី
