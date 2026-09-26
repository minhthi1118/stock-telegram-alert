# List of stocks to monitor grouped by sector
WATCHLIST = {
    "Securities": ["HCM", "VND", "MBS", "VIX"],
    "Banks": ["MBB", "ACB", "SHB", "BVB", "TPB"],
    "Real Estate": ["DXG", "DIG"],
    "Steel": ["HPG", "NKG"],
    "Consumer/Retail": ["VNM", "MWG"],
    "Technology": ["FPT"]
}

# Flatten the watchlist into a single list for the script to loop through
ALL_STOCKS = [stock for sector in WATCHLIST.values() for stock in sector]

# Signal Configuration
MA_SHORT = 20
MA_LONG = 50

# MA20 Bounce tolerance (±1.5% around MA20)
MA20_TOUCH_TOLERANCE = 0.015

# Volume ratios
MA_BREAKOUT_VOLUME_RATIO = 1.2      # MA20/MA50 breakout & MA20 breakdown
HIGH_VOLUME_RATIO = 1.5             # High-Volume Sell-Off & 20-Day Base Breakout
VOLUME_DRY_UP_RATIO = 0.8           # Volume Dry-Up (5D avg & current day)

# High-Volume Sell-Off price drop threshold
HIGH_VOLUME_SELL_OFF_DROP = -0.03

# Sideways settings: if price stays within 3% range for 5 days
SIDEWAY_THRESHOLD = 0.03
SIDEWAY_DAYS = 5

# Base formation settings: sideways range thresholds for 10, 20, 30 days
BASE_THRESHOLD_10 = 0.06
BASE_THRESHOLD_20 = 0.08
BASE_THRESHOLD_30 = 0.10

