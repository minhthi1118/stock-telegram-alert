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

# Sideways settings: if price stays within 3% range for 5 days
SIDEWAY_THRESHOLD = 0.03 
SIDEWAY_DAYS = 5

# Base formation settings: sideways range thresholds for 10, 20, 30 days
BASE_THRESHOLD_10 = 0.06
BASE_THRESHOLD_20 = 0.08
BASE_THRESHOLD_30 = 0.10

