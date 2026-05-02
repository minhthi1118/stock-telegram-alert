# List of stocks to monitor grouped by sector
WATCHLIST = {
    "Securities": ["HCM", "VND", "MBS", "VIX"],
    "Banks": ["MBB", "ACB", "SHB", "BVB", "TPB"],
    "Real Estate": ["DXG", "DIG"],
    "Steel": ["HPG", "NKG"],
    "Consumer/Retail": ["VNM", "MWG"]
}

# Flatten the watchlist into a single list for the script to loop through
ALL_STOCKS = [stock for sector in WATCHLIST.values() for stock in sector]

# Signal Configuration
MA_SHORT = 20
MA_LONG = 50

# Sideways settings: if price stays within 3% range for 5 days
SIDEWAY_THRESHOLD = 0.03 
SIDEWAY_DAYS = 5
