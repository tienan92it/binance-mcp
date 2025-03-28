# binance_api.py
import os
import requests

BASE_URL = "https://api.binance.com"  # Base endpoint for Binance Spot API

# (Optional) Read environment variables for API keys if needed in future (not used for public data)
API_KEY = os.getenv("BINANCE_API_KEY")     # Public API key (for future private endpoints)
API_SECRET = os.getenv("BINANCE_API_SECRET")  # API secret (for future use)

def get_live_price(symbol: str) -> float:
    """Fetch the latest trade price for a given symbol (e.g., 'BTCUSDT')."""
    url = f"{BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching price: HTTP {resp.status_code} - {resp.text}")
    data = resp.json()
    # Binance returns JSON like {"symbol": "BTCUSDT", "price": "30000.00"}
    if "price" not in data:
        raise RuntimeError(f"Unexpected response for price: {data}")
    return float(data["price"])

def get_order_book(symbol: str, limit: int = 100) -> dict:
    """Fetch a snapshot of the current order book (bids and asks) for a symbol."""
    url = f"{BASE_URL}/api/v3/depth"
    params = {"symbol": symbol, "limit": limit}
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching order book: {resp.status_code} - {resp.text}")
    data = resp.json()
    # Example data: {"lastUpdateId": 123456, "bids": [["10000.0","0.5"], ...], "asks": [...]} 
    return data  # Return the JSON with bids and asks as lists of [price, quantity]

def get_historical_klines(symbol: str, interval: str = "1d", limit: int = 100) -> list:
    """Fetch historical price data (candlesticks) for a symbol and interval.
    Returns a list of OHLCV candlestick data up to the specified limit."""
    url = f"{BASE_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching klines: {resp.status_code} - {resp.text}")
    data = resp.json()
    # Each entry: [open_time, open, high, low, close, volume, close_time, quote_asset_volume, trades, ...]
    # Convert numeric fields from strings to float for convenience
    candles = []
    for entry in data:
        open_time, open_price, high_price, low_price, close_price, volume = entry[0:6]
        candles.append({
            "open_time": open_time,
            "open": float(open_price),
            "high": float(high_price),
            "low": float(low_price),
            "close": float(close_price),
            "volume": float(volume)
        })
    return candles

def get_exchange_info() -> dict:
    """Retrieve exchange information (trading rules, symbol list, etc.)."""
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    resp = requests.get(url)
    if not resp.ok:
        raise RuntimeError(f"Error fetching exchange info: {resp.status_code}")
    data = resp.json()
    # This returns a lot of metadata including rate limits and all symbols with their filters.
    return data

def get_trading_fees() -> dict:
    """Get current trading fee rates (maker & taker fees). 
    Binance's public API does not expose account-specific fees without authentication.
    Here we return default spot trading fees for illustration."""
    # Default Binance spot trading fees for regular users (VIP 0 tier) 
    # Typically 0.1% maker and 0.1% taker (represented as 0.001 in decimal).
    return {"maker_fee": 0.001, "taker_fee": 0.001} 