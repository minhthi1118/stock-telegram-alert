import pandas as pd

from main import analyze_stock_data


def make_base_dataframe(rows=60, close=100.0, volume=1000.0):
    """
    Create a simple synthetic trading DataFrame for signal tests.

    The default data is intentionally stable:
    - Close stays around 100
    - Volume stays around 1,000
    - Enough history exists for MA50 and Vol20 calculations
    """
    dates = pd.bdate_range("2026-01-05", periods=rows)

    return pd.DataFrame(
        {
            "time": dates,
            "open": [close] * rows,
            "high": [close * 1.01] * rows,
            "low": [close * 0.99] * rows,
            "close": [close] * rows,
            "volume": [volume] * rows,
        }
    )


def signal_exists(result, signal_prefix):
    """Return True when any signal starts with the expected text."""
    return any(signal.startswith(signal_prefix) for signal in result["signals"])


def test_high_volume_sell_off_shb_case():
    """
    Regression case based on the SHB-type scenario:
    - Daily change = -6.7%
    - Current volume = 1.8x previous Vol20

    Expected:
    - High-Volume Sell-Off triggers
    - Volume Dry-Up does not trigger
    """
    df = make_base_dataframe()

    df.loc[df.index[-2], "close"] = 100.0
    df.loc[df.index[-1], "close"] = 93.3
    df.loc[df.index[-1], "open"] = 100.0
    df.loc[df.index[-1], "high"] = 100.0
    df.loc[df.index[-1], "low"] = 93.0
    df.loc[df.index[-1], "volume"] = 1800.0

    result = analyze_stock_data("SHB", df)

    assert result is not None
    assert signal_exists(result, "🔴 High-Volume Sell-Off")
    assert "🔇 Volume Dry-Up" not in result["signals"]


def test_volume_dry_up():
    """
    Recent 5-day average and current volume are both well below Vol20.

    Previous 20 trading days:
    - First 15 days volume = 1,000
    - Last 5 days volume = 600

    Vol20 = 900
    Recent 5D avg = 600 = 0.667x Vol20
    Current volume = 600 = 0.667x Vol20
    """
    df = make_base_dataframe()

    # Lower the five completed trading days before the current day.
    df.loc[df.index[-6:-1], "volume"] = 600.0
    df.loc[df.index[-1], "volume"] = 600.0

    result = analyze_stock_data("TEST", df)

    assert result is not None
    assert "🔇 Volume Dry-Up" in result["signals"]
    assert not signal_exists(result, "🔴 High-Volume Sell-Off")


def test_ma20_bounce():
    """
    MA20 Bounce:
    - Low is within ±1.5% of MA20
    - Close > MA20
    - Close > previous close
    - Volume >= 0.8x Vol20
    """
    df = make_base_dataframe()

    # Previous close remains 100.
    # Current MA20 becomes approximately 100.05.
    df.loc[df.index[-1], "open"] = 100.0
    df.loc[df.index[-1], "low"] = 100.0
    df.loc[df.index[-1], "high"] = 101.5
    df.loc[df.index[-1], "close"] = 101.0
    df.loc[df.index[-1], "volume"] = 1000.0

    result = analyze_stock_data("TEST", df)

    assert result is not None
    assert "📈 MA20 Bounce" in result["signals"]


def test_sideways_priority_uses_longest_qualifying_base():
    """
    A flat 60-day series qualifies for 5D, 10D, 20D, and 30D sideways rules.

    Expected:
    - Only Sideways Base (30D) is shown.
    """
    df = make_base_dataframe()

    result = analyze_stock_data("TEST", df)

    assert result is not None
    assert "↔️ Sideways Base (30D)" in result["signals"]
    assert "↔️ Sideways Base (20D)" not in result["signals"]
    assert "↔️ Sideways Base (10D)" not in result["signals"]
    assert "↔️ Sideways (5 days)" not in result["signals"]


def test_ma20_breakdown():
    """
    MA20 Breakdown:
    - Previous close >= previous MA20
    - Current close < current MA20
    - Current volume = 1.3x Vol20
    """
    df = make_base_dataframe()

    df.loc[df.index[-2], "close"] = 100.0
    df.loc[df.index[-1], "open"] = 100.0
    df.loc[df.index[-1], "high"] = 100.0
    df.loc[df.index[-1], "low"] = 98.5
    df.loc[df.index[-1], "close"] = 99.0
    df.loc[df.index[-1], "volume"] = 1300.0

    result = analyze_stock_data("TEST", df)

    assert result is not None
    assert "⚠️ MA20 Breakdown" in result["signals"]
