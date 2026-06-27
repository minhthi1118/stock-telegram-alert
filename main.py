import os
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from vnstock import Quote
from config import (
    ALL_STOCKS, MA_SHORT, MA_LONG, SIDEWAY_THRESHOLD, SIDEWAY_DAYS,
    BASE_THRESHOLD_10, BASE_THRESHOLD_20, BASE_THRESHOLD_30, WATCHLIST
)

# 1. Setup - Load secrets from .env file (for local testing)
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """Sends a text message to your Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram credentials (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID) not found.")
        return
    
    # The URL for the Telegram Bot API
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        # Secure error printing: we don't print the exception directly because it might contain the URL/token
        print(f"Error sending Telegram message. Status Code: {getattr(e.response, 'status_code', 'Unknown')}")

def calculate_signals(symbol):
    """Fetches data and calculates signals for a single stock."""
    try:
        # Fetch data: we get 150 days to be safe for moving average calculations
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=150)).strftime('%Y-%m-%d')
        
        # vnstock 0.3+ Quote usage: 
        # 1. Initialize with symbol and lowercase source
        # 2. Call history with start, end, and interval
        stock = Quote(symbol=symbol, source='vci')
        df = stock.history(start=start_date, end=end_date, interval='1D')
        
        if df is None or len(df) < MA_LONG:
            return None

        # Ensure we have the standard column names: date, open, high, low, close, volume
        # The Quote().history() usually returns these, but we ensure lowercase for safety
        df.columns = [col.lower() for col in df.columns]
        
        # Calculate Moving Averages
        df['ma20'] = df['close'].rolling(window=MA_SHORT).mean()
        df['ma50'] = df['close'].rolling(window=MA_LONG).mean()
        # Average volume over the last 20 days
        df['vol_avg'] = df['volume'].rolling(window=20).mean()
        
        # Get the most recent day (current) and the day before (previous)
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        signals = []
        price = current['close']
        volume = current['volume']
        avg_vol = current['vol_avg']

        # Parse Latest Trading Date from current['time']
        if 'time' in current and not pd.isna(current['time']):
            if hasattr(current['time'], 'strftime'):
                trading_date = current['time'].strftime('%Y-%m-%d')
            else:
                trading_date = str(current['time'])[:10]
        else:
            trading_date = datetime.now().strftime('%Y-%m-%d')

        # Daily change: (current close - previous close) / previous close
        daily_change = (price - previous['close']) / previous['close'] if previous['close'] else 0.0

        # SIGNAL 1: Breakout above MA20 or MA50 with higher volume
        break_ma20 = current['close'] > current['ma20'] and previous['close'] <= previous['ma20']
        break_ma50 = current['close'] > current['ma50'] and previous['close'] <= previous['ma50']
        if (break_ma20 or break_ma50) and volume > avg_vol:
            signals.append("🚀 Breakout above MA")

        # SIGNAL 2: Breakdown below MA20 with higher volume
        if current['close'] < current['ma20'] and previous['close'] >= previous['ma20']:
            if volume > avg_vol:
                signals.append("⚠️ Breakdown below MA20")

        # SIGNAL 3: MA20 Bounce (Beginner-friendly rule)
        # 1. Low touches or comes near MA20 (within 1%)
        near_ma20 = current['low'] <= current['ma20'] * 1.01
        # 2. Closing price is above MA20
        # 3. Closing price is higher than previous close
        # 4. Volume is healthy (at least 80% of average)
        if near_ma20 and price > current['ma20'] and price > previous['close'] and volume > avg_vol * 0.8:
            signals.append("📈 MA20 Bounce")

        # SIGNAL 4: Drawdown from recent 50-day high
        recent_high = df['high'].tail(50).max()
        drawdown = (recent_high - price) / recent_high
        if drawdown > 0.10: # Only report if fallen more than 10%
            signals.append(f"📉 Drawdown: {drawdown:.1%}")

        # SIGNAL 5: Sideways Duration (5 days)
        # Check if price stayed within a narrow range for the last N days
        last_n_days = df.tail(SIDEWAY_DAYS)
        price_range = (last_n_days['high'].max() - last_n_days['low'].min()) / last_n_days['low'].min()
        if price_range <= SIDEWAY_THRESHOLD:
            signals.append(f"↔️ Sideways ({SIDEWAY_DAYS} days)")

        # Sideways Base Formation (10, 20, 30 days)
        if len(df) >= 10:
            last_10 = df.tail(10)
            range_10 = (last_10['high'].max() - last_10['low'].min()) / last_10['low'].min()
            if range_10 <= BASE_THRESHOLD_10:
                signals.append("↔️ Sideways (10 days)")

        if len(df) >= 20:
            last_20 = df.tail(20)
            range_20 = (last_20['high'].max() - last_20['low'].min()) / last_20['low'].min()
            if range_20 <= BASE_THRESHOLD_20:
                signals.append("↔️ Sideways (20 days)")

        if len(df) >= 30:
            last_30 = df.tail(30)
            range_30 = (last_30['high'].max() - last_30['low'].min()) / last_30['low'].min()
            if range_30 <= BASE_THRESHOLD_30:
                signals.append("↔️ Sideways (30 days)")

        # Breakout from 20-day base
        if len(df) >= 21:
            prev_20 = df.iloc[-21:-1]
            highest_high_20 = prev_20['high'].max()
            if price > highest_high_20 and volume > avg_vol and price > current['ma20']:
                signals.append("🚀 20-Day Base Breakout")

        # Volume Contraction
        if len(df) >= 20:
            vol_avg_5 = df['volume'].tail(5).mean()
            vol_avg_20 = df['volume'].tail(20).mean()
            if vol_avg_5 < vol_avg_20:
                signals.append("🔇 Volume Contraction")

        # Distance from MA20
        ma20_dist = (price - current['ma20']) / current['ma20'] if current['ma20'] and not pd.isna(current['ma20']) else 0.0

        return {
            "symbol": symbol,
            "price": price,
            "signals": signals,
            "above_ma20": price > current['ma20'],
            "ma20_dist": ma20_dist,
            "daily_change": daily_change,
            "trading_date": trading_date
        }
    except Exception as e:
        print(f"Error calculating signals for {symbol}: {e}")
        return None

def main():
    print("--- Starting Daily Stock Alert ---")
    results = []
    
    # Loop through each stock in your watchlist
    for symbol in ALL_STOCKS:
        print(f"Processing {symbol}...")
        res = calculate_signals(symbol)
        if res:
            results.append(res)
        
        # Slow down to avoid "Rate Limit" errors from the data source
        time.sleep(2)
    
    if not results:
        print("No data was fetched. Check your connection or symbols.")
        return

    # 4. Watchlist Breadth calculation
    stocks_above_ma20 = sum(1 for r in results if r['above_ma20'])
    breadth = stocks_above_ma20 / len(results)
    
    # 5. Format the message
    date_str = datetime.now().strftime('%Y-%m-%d')
    # Find the trading date from results
    trading_dates = [r['trading_date'] for r in results if 'trading_date' in r]
    trading_date_str = trading_dates[0] if trading_dates else date_str

    message = f"📊 *VN Stock Daily Alert*\nTrading Date: {trading_date_str} (Run Date: {date_str})\n\n"
    
    # Only show breadth if it's significant (>= 50%)
    if breadth >= 0.5:
        message += f"💡 *Watchlist Health: {breadth:.0%} of stocks above MA20*\n\n"

    # Create mapping from stock symbol to its calculated result
    results_map = {r['symbol']: r for r in results}

    # Section 1: Watchlist Prices (Every stock in the watchlist by sector)
    message += "📈 *Watchlist Prices*\n"
    for sector, symbols in WATCHLIST.items():
        price_strs = []
        for sym in symbols:
            if sym in results_map:
                r = results_map[sym]
                # Format: BVB: 13.8 | Day: -2.1% | MA20: +6.1%
                price_strs.append(f"{sym}: {r['price']:,.1f} | Day: {r['daily_change']:+.1%} | MA20: {r['ma20_dist']:+.1%}")
            else:
                price_strs.append(f"{sym}: N/A")
        message += f"• *{sector}*: {', '.join(price_strs)}\n"
    message += "\n"

    # Section 2: Signal Alerts
    message += "🔔 *Signal Alerts*\n"
    alert_found = False
    for res in results:
        if res['signals']:
            alert_found = True
            message += f"*{res['symbol']}*\n"
            message += f"• Price: {res['price']:,.1f} | Day: {res['daily_change']:+.1%} | MA20: {res['ma20_dist']:+.1%}\n"
            for s in res['signals']:
                message += f"• {s}\n"
            message += "\n"

    if not alert_found:
        message += "No significant signals detected for your watchlist today.\n"

    print("Sending results to Telegram...")
    send_telegram_message(message)
    print("--- Process Complete ---")

if __name__ == "__main__":
    main()
