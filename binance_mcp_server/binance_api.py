# binance_api.py
import os
import requests

BASE_URL = "https://api.binance.com"  # Base endpoint for Binance Spot API

# (Optional) Read environment variables for API keys if needed in future (not used for public data)
API_KEY = os.getenv("BINANCE_API_KEY")     # Public API key (for future private endpoints)
API_SECRET = os.getenv("BINANCE_API_SECRET")  # API secret (for future use)

def ping() -> bool:
    """Test connectivity to the Binance API.
    
    Returns:
        True if ping was successful, False otherwise.
    """
    url = f"{BASE_URL}/api/v3/ping"
    resp = requests.get(url)
    if not resp.ok:
        raise RuntimeError(f"Error pinging Binance API: HTTP {resp.status_code} - {resp.text}")
    return True

def get_server_time() -> int:
    """Get the current server time from Binance.
    
    Returns:
        Server time in milliseconds (UNIX timestamp).
    """
    url = f"{BASE_URL}/api/v3/time"
    resp = requests.get(url)
    if not resp.ok:
        raise RuntimeError(f"Error fetching server time: HTTP {resp.status_code} - {resp.text}")
    data = resp.json()
    return data["serverTime"]

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

def get_ui_klines(symbol: str, interval: str = "1d", limit: int = 100) -> list:
    """Fetch UI optimized candlestick data (UIKlines) for a symbol and interval.
    
    This endpoint returns candlestick data optimized for presentation of a candlestick chart.
    The format is similar to the regular klines endpoint.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        interval: Candlestick interval (e.g., '1m', '15m', '1h', '1d')
        limit: Number of data points to retrieve (max 1000)
        
    Returns:
        List of candlestick data optimized for UI presentation.
    """
    url = f"{BASE_URL}/api/v3/uiKlines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching UI klines: HTTP {resp.status_code} - {resp.text}")
    data = resp.json()
    # Format is same as regular klines
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

def get_recent_trades(symbol: str, limit: int = 500) -> list:
    """Fetch recent trades for a given symbol.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        limit: Number of trades to fetch (default 500, max 1000)
        
    Returns:
        List of recent trades with details like price, quantity, time, etc.
    """
    url = f"{BASE_URL}/api/v3/trades"
    params = {"symbol": symbol, "limit": limit}
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching recent trades: HTTP {resp.status_code} - {resp.text}")
    data = resp.json()
    # Example trade: {"id": 28457, "price": "4.00000100", "qty": "12.00000000", "time": 1499865549590, ...}
    # Convert numeric fields from strings to appropriate types
    trades = []
    for trade in data:
        trades.append({
            "id": trade["id"],
            "price": float(trade["price"]),
            "qty": float(trade["qty"]),
            "time": trade["time"],
            "isBuyerMaker": trade["isBuyerMaker"],
            "isBestMatch": trade["isBestMatch"]
        })
    return trades

def get_historical_trades(symbol: str, limit: int = 500, from_id: int = None) -> list:
    """Fetch historical trades for a given symbol.
    
    Note: This endpoint requires API KEY authentication for requesting beyond the 
    default 500 trades. We'll support the unauthenticated version for simplicity.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        limit: Number of trades to fetch (default 500, max 1000)
        from_id: Trade ID to fetch from (optional)
        
    Returns:
        List of historical trades with details like price, quantity, time, etc.
    """
    url = f"{BASE_URL}/api/v3/historicalTrades"
    params = {"symbol": symbol, "limit": limit}
    if from_id:
        params["fromId"] = from_id
    
    headers = {}
    if API_KEY:
        # If API_KEY is defined, include in request header
        headers["X-MBX-APIKEY"] = API_KEY
    
    resp = requests.get(url, params=params, headers=headers)
    if not resp.ok:
        raise RuntimeError(f"Error fetching historical trades: HTTP {resp.status_code} - {resp.text}")
    data = resp.json()
    
    # Process the data like recent trades
    trades = []
    for trade in data:
        trades.append({
            "id": trade["id"],
            "price": float(trade["price"]),
            "qty": float(trade["qty"]),
            "time": trade["time"],
            "isBuyerMaker": trade["isBuyerMaker"],
            "isBestMatch": trade["isBestMatch"]
        })
    return trades

def get_aggregate_trades(symbol: str, limit: int = 500) -> list:
    """Fetch aggregate trades for a given symbol.
    
    Aggregate trades are trades that have been filled at the same time, with the same price and the same order.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        limit: Number of aggregate trades to fetch (default 500, max 1000)
        
    Returns:
        List of aggregate trades with details like price, quantity, time, etc.
    """
    url = f"{BASE_URL}/api/v3/aggTrades"
    params = {"symbol": symbol, "limit": limit}
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching aggregate trades: HTTP {resp.status_code} - {resp.text}")
    data = resp.json()
    # Example: {"a": 26129, "p": "0.01633102", "q": "4.70443515", "f": 27781, "l": 27781, "T": 1498793709153, ...}
    # Convert numeric fields from strings to appropriate types
    trades = []
    for trade in data:
        trades.append({
            "id": trade["a"],
            "price": float(trade["p"]),
            "qty": float(trade["q"]),
            "first_trade_id": trade["f"],
            "last_trade_id": trade["l"],
            "time": trade["T"],
            "is_buyer_maker": trade["m"],
            "is_best_match": trade["M"]
        })
    return trades

def get_24hr_ticker(symbol: str = None) -> dict:
    """Fetch 24-hour price change statistics.
    
    Args:
        symbol: Optional symbol to get data for. If not provided, returns data for all symbols.
        
    Returns:
        Dictionary containing statistics for the last 24 hours.
    """
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    params = {}
    if symbol:
        params["symbol"] = symbol
    
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching 24hr ticker: HTTP {resp.status_code} - {resp.text}")
    
    data = resp.json()
    # If symbol is provided, we get a single object, otherwise a list of objects
    if symbol:
        # Convert numeric fields to appropriate types
        return {
            "symbol": data["symbol"],
            "priceChange": float(data["priceChange"]),
            "priceChangePercent": float(data["priceChangePercent"]),
            "weightedAvgPrice": float(data["weightedAvgPrice"]),
            "prevClosePrice": float(data["prevClosePrice"]),
            "lastPrice": float(data["lastPrice"]),
            "lastQty": float(data["lastQty"]),
            "bidPrice": float(data["bidPrice"]),
            "bidQty": float(data["bidQty"]),
            "askPrice": float(data["askPrice"]),
            "askQty": float(data["askQty"]),
            "openPrice": float(data["openPrice"]),
            "highPrice": float(data["highPrice"]),
            "lowPrice": float(data["lowPrice"]),
            "volume": float(data["volume"]),
            "quoteVolume": float(data["quoteVolume"]),
            "openTime": data["openTime"],
            "closeTime": data["closeTime"],
            "count": data["count"]
        }
    else:
        # Return the list of ticker data for all symbols (could be large)
        # Consider limiting the number of fields returned if all symbols are requested
        return data

def get_trading_day_ticker(symbol: str = None, type: str = "FULL") -> dict:
    """Fetch trading day ticker statistics.
    
    This endpoint provides price change statistics for the current trading day.
    
    Args:
        symbol: Optional symbol to get data for. If not provided, returns data for all symbols.
        type: Response type (FULL or MINI). FULL includes all fields, MINI includes fewer fields.
        
    Returns:
        Dictionary containing statistics for the current trading day.
    """
    url = f"{BASE_URL}/api/v3/ticker/tradingDay"
    params = {"type": type}
    if symbol:
        params["symbol"] = symbol
    
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching trading day ticker: HTTP {resp.status_code} - {resp.text}")
    
    data = resp.json()
    # If symbol is provided, we get a single object, otherwise a list of objects
    if symbol:
        # Convert numeric fields to appropriate types
        processed_data = {
            "symbol": data["symbol"],
            "priceChange": float(data["priceChange"]),
            "priceChangePercent": float(data["priceChangePercent"]),
            "openPrice": float(data["openPrice"]),
            "highPrice": float(data["highPrice"]),
            "lowPrice": float(data["lowPrice"]),
            "lastPrice": float(data["lastPrice"]),
            "volume": float(data["volume"]),
            "quoteVolume": float(data["quoteVolume"]),
            "openTime": data["openTime"],
            "closeTime": data["closeTime"],
            "firstId": data["firstId"],
            "lastId": data["lastId"],
            "count": data["count"]
        }
        
        # Additional fields for FULL type
        if type == "FULL":
            processed_data.update({
                "weightedAvgPrice": float(data["weightedAvgPrice"]),
                "lastQty": float(data["lastQty"]),
                "bidPrice": float(data["bidPrice"]),
                "bidQty": float(data["bidQty"]),
                "askPrice": float(data["askPrice"]),
                "askQty": float(data["askQty"])
            })
            
        return processed_data
    else:
        # Return the list of ticker data for all symbols
        # We won't process this for efficiency when fetching all symbols
        return data

def get_average_price(symbol: str) -> float:
    """Fetch current average price for a symbol.
    
    The current average price is calculated using the weighted average of the last 5 minutes of trade data.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
    Returns:
        Current average price as a float.
    """
    url = f"{BASE_URL}/api/v3/avgPrice"
    params = {"symbol": symbol}
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching average price: HTTP {resp.status_code} - {resp.text}")
    data = resp.json()
    # Example: {"mins": 5, "price": "9.35751834"}
    return float(data["price"])

def get_rolling_window_ticker(symbol: str = None, windowSize: str = "1d", type: str = "FULL") -> dict:
    """Fetch rolling window price change statistics.
    
    This endpoint provides price change statistics for a specified rolling window.
    
    Args:
        symbol: Optional symbol to get data for. If not provided, returns data for all symbols.
        windowSize: Size of the rolling window (e.g., "1d", "4h")
        type: Response type (FULL or MINI). FULL includes all fields, MINI includes fewer fields.
        
    Returns:
        Dictionary containing statistics for the rolling window.
    """
    url = f"{BASE_URL}/api/v3/ticker"
    params = {"windowSize": windowSize, "type": type}
    if symbol:
        params["symbol"] = symbol
    
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching rolling window ticker: HTTP {resp.status_code} - {resp.text}")
    
    data = resp.json()
    # If symbol is provided, we get a single object, otherwise a list of objects
    if symbol:
        # Convert numeric fields to appropriate types
        processed_data = {
            "symbol": data["symbol"],
            "priceChange": float(data["priceChange"]),
            "priceChangePercent": float(data["priceChangePercent"]),
            "openPrice": float(data["openPrice"]),
            "highPrice": float(data["highPrice"]),
            "lowPrice": float(data["lowPrice"]),
            "lastPrice": float(data["lastPrice"]),
            "volume": float(data["volume"]),
            "quoteVolume": float(data["quoteVolume"]),
            "openTime": data["openTime"],
            "closeTime": data["closeTime"],
            "firstId": data["firstId"],
            "lastId": data["lastId"],
            "count": data["count"]
        }
        
        # Additional fields for FULL type
        if type == "FULL":
            processed_data.update({
                "weightedAvgPrice": float(data["weightedAvgPrice"]),
                "lastQty": float(data["lastQty"]),
                "bidPrice": float(data["bidPrice"]),
                "bidQty": float(data["bidQty"]),
                "askPrice": float(data["askPrice"]),
                "askQty": float(data["askQty"])
            })
            
        return processed_data
    else:
        # Return the list of ticker data for all symbols
        # We won't process this for efficiency when fetching all symbols
        return data

def get_book_ticker(symbol: str = None) -> dict:
    """Fetch best price/qty on the order book for a symbol or all symbols.
    
    Args:
        symbol: Optional symbol to get data for. If not provided, returns data for all symbols.
        
    Returns:
        Dictionary containing the best bid and ask prices and quantities.
    """
    url = f"{BASE_URL}/api/v3/ticker/bookTicker"
    params = {}
    if symbol:
        params["symbol"] = symbol
    
    resp = requests.get(url, params=params)
    if not resp.ok:
        raise RuntimeError(f"Error fetching book ticker: HTTP {resp.status_code} - {resp.text}")
    
    data = resp.json()
    # If symbol is provided, we get a single object, otherwise a list of objects
    if symbol:
        # Example: {"symbol": "LTCBTC", "bidPrice": "4.00000000", "bidQty": "431.00000000", ...}
        return {
            "symbol": data["symbol"],
            "bidPrice": float(data["bidPrice"]),
            "bidQty": float(data["bidQty"]),
            "askPrice": float(data["askPrice"]),
            "askQty": float(data["askQty"])
        }
    else:
        # Return the list of book ticker data for all symbols
        # For all symbols, don't convert to float to save processing time
        return data 