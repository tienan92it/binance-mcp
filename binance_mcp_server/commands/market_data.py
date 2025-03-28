# commands/market_data.py
from mcp.server.fastmcp import FastMCP
from binance_mcp_server import binance_api

def register_market_data_commands(mcp: FastMCP):
    """Register MCP commands for market data (prices, order books, historical data)."""
    
    @mcp.tool()
    def get_price(symbol: str) -> float:
        """Get the latest trade price for a given symbol (e.g., 'BTCUSDT')."""
        return binance_api.get_live_price(symbol)
    
    @mcp.tool()
    def get_order_book(symbol: str, depth: int = 10) -> dict:
        """Retrieve the current order book (top bids/asks) for a symbol.
        
        Args:
            symbol: Trading pair symbol, e.g., 'ETHUSDT'.
            depth: Number of price levels to retrieve for each side (default 10).
        """
        # Note: Binance API `limit` parameter accepts specific values (5, 10, 20, 50, 100, 500, etc.)
        return binance_api.get_order_book(symbol, limit=depth)
    
    @mcp.tool()
    def get_historical_prices(symbol: str, interval: str = "1d", limit: int = 100) -> list:
        """Fetch historical OHLC price data for a symbol.
        
        Args:
            symbol: Trading pair, e.g., 'BTCUSDT'.
            interval: Candlestick interval (e.g., '1m', '15m', '1h', '1d').
            limit: Number of data points to retrieve (max 1000 by Binance API).
        """
        return binance_api.get_historical_klines(symbol, interval=interval, limit=limit) 