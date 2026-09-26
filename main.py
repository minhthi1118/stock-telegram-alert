import os
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from vnstock import Quote
from config import (
    ALL_STOCKS, MA_SHORT, MA_LONG, SIDEWAY_THRESHOLD, SIDEWAY_DAYS,
    BASE_THRESHOLD_10, BASE_THRESHOLD_20, BASE_THRESHOLD_30, WATCHLIST,
    MA20_TOUCH_TOLERANCE, MA_BREAKOUT_VOLUME_RATIO, HIGH_VOLUME_RATIO,
    VOLUME_DRY_UP_RATIO, HIGH_VOLUME_SELL_OFF_DROP
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
        print(f"Error sending Telegram message. Status Code: {getattr(e.response, 'status_code', 'Unknown')}")

def analyze_stock_data(symbol, df):
    """
    Calculates all signals from a prepared DataFrame.
    This function is pure signal logic and can be tested with synthetic DataFrames.
    """
    try:
        df.columns = [col.lower() for col in df.columns]
        
        # Calculate Moving Averages (rolling including current day)
        df['ma20'] = df['close'].rolling(window=MA_SHORT).mean()
        df['ma50'] = df['close'].rolling(window=MA_LONG).mean()
        
        # Vol20: average volume of previous 20 completed trading days (exclude current day)
        df['vol20'] = df['volume'].shift(1).rolling(window=20).mean()
        
        # 5-day average volume for Volume Dry-Up (exclude current day)
        df['vol5_avg'] = df['volume'].shift(1).rolling(window=5).mean()
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        signals = []
        price = current['close']
        volume = current['volume']
        vol20 = current['vol20']
        vol5_avg = current['vol5_avg']
        
        # Parse Latest Trading Date
        if 'time' in current and not pd.isna(current['time']):
            if hasattr(current['time'], 'strftime'):
                trading_date = current['time'].strftime('%Y-%m-%d')
            else:
                trading_date = str(current['time'])[:10]
        else:
            trading_date = datetime.now().strftime('%Y-%m-%d')

        # Daily change: (current close - previous close) / previous close
        daily_change = (price - previous['close']) / previous['close'] if previous['close'] else 0.0

        # Skip signal detection if vol20 is NaN (not enough history)
        if pd.isna(vol20) or vol20 == 0:
            return {
                "symbol": symbol,
                "price": price,
                "signals": [],
                "above_ma20": price > current['ma20'] if not pd.isna(current['ma20']) else False,
                "ma20_dist": 0.0,
                "daily_change": daily_change,
                "trading_date": trading_date
            }

        # ============================================================
        # SIGNAL: High-Volume Sell-Off
        # ============================================================
        high_vol_sell_off = (
            daily_change <= HIGH_VOLUME_SELL_OFF_DROP and
            volume >= HIGH_VOLUME_RATIO * vol20
        )
        if high_vol_sell_off:
            vol_multiple = volume / vol20
            signals.append(f"🔴 High-Volume Sell-Off ({vol_multiple:.1f}× Vol20)")

        # ============================================================
        # SIGNAL: Volume Dry-Up (replaces Volume Contraction)
        # ============================================================
        # Only check if we have enough data for 5-day average
        volume_dry_up = False
        if not pd.isna(vol5_avg) and vol20 > 0:
            volume_dry_up = (
                vol5_avg <= VOLUME_DRY_UP_RATIO * vol20 and
                volume <= VOLUME_DRY_UP_RATIO * vol20
            )
        # Conflict rule: High-Volume Sell-Off blocks Volume Dry-Up
        if volume_dry_up and not high_vol_sell_off:
            signals.append("🔇 Volume Dry-Up")

        # ============================================================
        # SIGNAL: MA20 Bounce
        # ============================================================
        ma20_bounce = False
        if not pd.isna(current['ma20']) and current['ma20'] > 0:
            ma20_dist_low = abs(current['low'] - current['ma20']) / current['ma20']
            ma20_bounce = (
                ma20_dist_low <= MA20_TOUCH_TOLERANCE and
                price > current['ma20'] and
                price > previous['close'] and
                volume >= VOLUME_DRY_UP_RATIO * vol20
            )
        if ma20_bounce:
            signals.append("📈 MA20 Bounce")

        # ============================================================
        # SIGNAL: MA20 Breakout
        # ============================================================
        ma20_breakout = (
            not pd.isna(current['ma20']) and not pd.isna(previous['ma20']) and
            previous['close'] <= previous['ma20'] and
            price > current['ma20'] and
            volume >= MA_BREAKOUT_VOLUME_RATIO * vol20
        )
        if ma20_breakout:
            signals.append("🚀 MA20 Breakout")

        # ============================================================
        # SIGNAL: MA50 Breakout
        # ============================================================
        ma50_breakout = (
            not pd.isna(current['ma50']) and not pd.isna(previous['ma50']) and
            previous['close'] <= previous['ma50'] and
            price > current['ma50'] and
            volume >= MA_BREAKOUT_VOLUME_RATIO * vol20
        )
        if ma50_breakout:
            signals.append("🚀 MA50 Breakout")

        # ============================================================
        # SIGNAL: MA20 Breakdown
        # ============================================================
        ma20_breakdown = (
            not pd.isna(current['ma20']) and not pd.isna(previous['ma20']) and
            previous['close'] >= previous['ma20'] and
            price < current['ma20'] and
            volume >= MA_BREAKOUT_VOLUME_RATIO * vol20
        )
        if ma20_breakdown:
            signals.append("⚠️ MA20 Breakdown")

        # ============================================================
        # SIGNAL: 50D Drawdown (Context)
        # ============================================================
        recent_high = df['high'].tail(50).max()
        drawdown = (recent_high - price) / recent_high if recent_high > 0 else 0.0
        if drawdown > 0.10:
            signals.append(f"📉 50D Drawdown: {drawdown:.1%}")

        # ============================================================
        # SIGNAL: Sideways / Base Detection (longest qualifying only)
        # ============================================================
        sideways_signal = None
        
        # Check 30D first (longest)
        if len(df) >= 30:
            last_30 = df.tail(30)
            range_30 = (last_30['high'].max() - last_30['low'].min()) / last_30['low'].min()
            if range_30 <= BASE_THRESHOLD_30:
                sideways_signal = "↔️ Sideways Base (30D)"
        
        # Check 20D
        if sideways_signal is None and len(df) >= 20:
            last_20 = df.tail(20)
            range_20 = (last_20['high'].max() - last_20['low'].min()) / last_20['low'].min()
            if range_20 <= BASE_THRESHOLD_20:
                sideways_signal = "↔️ Sideways Base (20D)"
        
        # Check 10D
        if sideways_signal is None and len(df) >= 10:
            last_10 = df.tail(10)
            range_10 = (last_10['high'].max() - last_10['low'].min()) / last_10['low'].min()
            if range_10 <= BASE_THRESHOLD_10:
                sideways_signal = "↔️ Sideways Base (10D)"
        
        # Check 5D (shortest)
        if sideways_signal is None and len(df) >= SIDEWAY_DAYS:
            last_5 = df.tail(SIDEWAY_DAYS)
            range_5 = (last_5['high'].max() - last_5['low'].min()) / last_5['low'].min()
            if range_5 <= SIDEWAY_THRESHOLD:
                sideways_signal = f"↔️ Sideways ({SIDEWAY_DAYS} days)"
        
        if sideways_signal:
            signals.append(sideways_signal)

        # ============================================================
        # SIGNAL: 20-Day Base Breakout
        # ============================================================
        if len(df) >= 21:
            prev_20 = df.iloc[-21:-1]  # Previous 20 days, excluding current
            highest_high_20 = prev_20['high'].max()
            if (
                price > highest_high_20 and
                not pd.isna(current['ma20']) and
                price > current['ma20'] and
                volume >= HIGH_VOLUME_RATIO * vol20
            ):
                signals.append("🚀 20-Day Base Breakout")

        # Distance from MA20
        ma20_dist = 0.0
        if not pd.isna(current['ma20']) and current['ma20'] > 0:
            ma20_dist = (price - current['ma20']) / current['ma20']

        return {
            "symbol": symbol,
            "price": price,
            "signals": signals,
            "above_ma20": price > current['ma20'] if not pd.isna(current['ma20']) else False,
            "ma20_dist": ma20_dist,
            "daily_change": daily_change,
            "trading_date": trading_date
        }
    except Exception as e:
        print(f"Error analyzing signals for {symbol}: {e}")
        return None

def calculate_signals(symbol):
    """Fetches data from vnstock and passes to analyze_stock_data."""
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=150)).strftime('%Y-%m-%d')
        
        stock = Quote(symbol=symbol, source='vci')
        df = stock.history(start=start_date, end=end_date, interval='1D')
        
        if df is None or len(df) < MA_LONG:
            return None
        
        return analyze_stock_data(symbol, df)
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def main():
    print("--- Starting Daily Stock Alert ---")
    results = []
    
    for symbol in ALL_STOCKS:
        print(f"Processing {symbol}...")
        res = calculate_signals(symbol)
        if res:
            results.append(res)
        
        time.sleep(2)
    
    if not results:
        print("No data was fetched. Check your connection or symbols.")
        return

    # Watchlist Breadth calculation
    stocks_above_ma20 = sum(1 for r in results if r['above_ma20'])
    breadth = stocks_above_ma20 / len(results)
    
    # Format the message
    date_str = datetime.now().strftime('%Y-%m-%d')
    trading_dates = [r['trading_date'] for r in results if 'trading_date' in r]
    trading_date_str = trading_dates[0] if trading_dates else date_str

    message = f"📊 *VN Stock Daily Alert*\nTrading Date: {trading_date_str} (Run Date: {date_str})\n\n"
    
    # Always show breadth (removed >= 50% condition)
    message += f"📊 *Watchlist Breadth: {breadth:.0%} above MA20*\n\n"

    # Create mapping from stock symbol to its calculated result
    results_map = {r['symbol']: r for r in results}

    # Section 1: Watchlist Prices (Every stock in the watchlist by sector)
    message += "📈 *Watchlist Prices*\n"
    for sector, symbols in WATCHLIST.items():
        price_strs = []
        for sym in symbols:
            if sym in results_map:
                r = results_map[sym]
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