# commands/market_data.py
from mcp.server.fastmcp import FastMCP
from binance_mcp_server import binance_api

def register_market_data_commands(mcp: FastMCP):
    """Register MCP commands for market data (prices, order books, historical data)."""
    
    @mcp.tool()
    def ping_binance() -> bool:
        """Test connectivity to the Binance API server.
        
        Returns:
            True if the server is reachable, otherwise an error is raised.
        """
        return binance_api.ping()
    
    @mcp.tool()
    def get_server_time() -> int:
        """Get the current server time from Binance.
        
        Returns:
            Server time in milliseconds (UNIX timestamp).
        """
        return binance_api.get_server_time()
    
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
    
    @mcp.tool()
    def get_ui_klines(symbol: str, interval: str = "1d", limit: int = 100) -> list:
        """Fetch UI-optimized candlestick data for a symbol.
        
        This endpoint returns candlestick data optimized for presentation of a candlestick chart.
        
        Args:
            symbol: Trading pair, e.g., 'BTCUSDT'.
            interval: Candlestick interval (e.g., '1m', '15m', '1h', '1d').
            limit: Number of data points to retrieve (max 1000).
        
        Returns:
            List of candlestick data optimized for UI presentation.
        """
        return binance_api.get_ui_klines(symbol, interval=interval, limit=limit)
    
    @mcp.tool()
    def get_recent_trades(symbol: str, limit: int = 20) -> list:
        """Get recent trades for a symbol.
        
        Retrieves the most recent trades that have occurred for a specific trading pair.
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
            limit: Number of recent trades to fetch (default: 20, max: 1000).
        
        Returns:
            List of recent trades with details including price, quantity, and timestamp.
        """
        return binance_api.get_recent_trades(symbol, limit=limit)
    
    @mcp.tool()
    def get_historical_trades(symbol: str, limit: int = 20, from_id: int = None) -> list:
        """Get historical trades for a symbol.
        
        Retrieves older trades that have occurred for a specific trading pair.
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
            limit: Number of trades to fetch (default: 20, max: 1000).
            from_id: Optional trade ID to fetch from.
        
        Returns:
            List of historical trades with details including price, quantity, and timestamp.
        """
        return binance_api.get_historical_trades(symbol, limit=limit, from_id=from_id)
    
    @mcp.tool()
    def get_aggregate_trades(symbol: str, limit: int = 20) -> list:
        """Get compressed/aggregate trades for a symbol.
        
        Aggregate trades are trades that have been filled at the same time, with the same price from the same order.
        This provides a more compact view of trading activity.
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
            limit: Number of aggregate trades to fetch (default: 20, max: 1000).
        
        Returns:
            List of aggregate trades with details including price, quantity, and timestamp.
        """
        return binance_api.get_aggregate_trades(symbol, limit=limit)
    
    @mcp.tool()
    def get_24hr_ticker(symbol: str) -> dict:
        """Get 24-hour price change statistics for a symbol.
        
        Provides a comprehensive overview of trading activity for a specific symbol over the past 24 hours,
        including price change, volume, high and low prices, etc.
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
        
        Returns:
            Dictionary with 24-hour statistics including price change, volume, and other metrics.
        """
        return binance_api.get_24hr_ticker(symbol)
    
    @mcp.tool()
    def get_all_24hr_tickers() -> list:
        """Get 24-hour price change statistics for all symbols.
        
        Provides comprehensive statistics for all trading pairs on the exchange.
        Note: This can return a large amount of data.
        
        Returns:
            List of dictionaries, each containing 24-hour statistics for a trading pair.
        """
        return binance_api.get_24hr_ticker()
    
    @mcp.tool()
    def get_trading_day_ticker(symbol: str, type: str = "FULL") -> dict:
        """Get trading day price change statistics for a symbol.
        
        Provides statistics for the current trading day (rather than a rolling 24-hour period).
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
            type: Response type ('FULL' or 'MINI'). FULL includes all fields, MINI includes fewer fields.
            
        Returns:
            Dictionary with trading day statistics including price change, volume, and other metrics.
        """
        return binance_api.get_trading_day_ticker(symbol, type=type)
    
    @mcp.tool()
    def get_all_trading_day_tickers(type: str = "FULL") -> list:
        """Get trading day price change statistics for all symbols.
        
        Provides statistics for the current trading day for all trading pairs.
        
        Args:
            type: Response type ('FULL' or 'MINI'). FULL includes all fields, MINI includes fewer fields.
            
        Returns:
            List of dictionaries with trading day statistics for all trading pairs.
        """
        return binance_api.get_trading_day_ticker(type=type)
    
    @mcp.tool()
    def get_rolling_window_ticker(symbol: str, window_size: str = "1d", type: str = "FULL") -> dict:
        """Get rolling window price change statistics for a symbol.
        
        Provides statistics for a specified rolling window period.
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
            window_size: Size of the rolling window (e.g., '1d', '4h').
            type: Response type ('FULL' or 'MINI'). FULL includes all fields, MINI includes fewer fields.
            
        Returns:
            Dictionary with rolling window statistics including price change, volume, and other metrics.
        """
        return binance_api.get_rolling_window_ticker(symbol, windowSize=window_size, type=type)
    
    @mcp.tool()
    def get_all_rolling_window_tickers(window_size: str = "1d", type: str = "FULL") -> list:
        """Get rolling window price change statistics for all symbols.
        
        Provides statistics for a specified rolling window period for all trading pairs.
        
        Args:
            window_size: Size of the rolling window (e.g., '1d', '4h').
            type: Response type ('FULL' or 'MINI'). FULL includes all fields, MINI includes fewer fields.
            
        Returns:
            List of dictionaries with rolling window statistics for all trading pairs.
        """
        return binance_api.get_rolling_window_ticker(windowSize=window_size, type=type)
    
    @mcp.tool()
    def get_average_price(symbol: str) -> float:
        """Get the current average price for a symbol.
        
        The average price is calculated using a weighted average of trades in the last 5 minutes.
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
            
        Returns:
            Current average price as a float.
        """
        return binance_api.get_average_price(symbol)
    
    @mcp.tool()
    def get_book_ticker(symbol: str) -> dict:
        """Get the best price/quantity on the order book for a symbol.
        
        Retrieves the best (top) bid and ask price and quantity on the order book.
        This provides a quick view of the current market for a symbol.
        
        Args:
            symbol: Trading pair symbol, e.g., 'BTCUSDT'.
            
        Returns:
            Dictionary containing the best bid and ask prices and quantities.
        """
        return binance_api.get_book_ticker(symbol)
    
    @mcp.tool()
    def get_all_book_tickers() -> list:
        """Get the best price/quantity on the order book for all symbols.
        
        Retrieves the best bid and ask for all trading pairs in a single request.
        
        Returns:
            List of dictionaries, each containing the best bid and ask for a symbol.
        """
        return binance_api.get_book_ticker() 