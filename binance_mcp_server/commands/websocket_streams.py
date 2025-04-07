# commands/websocket_streams.py
import asyncio
import json
from typing import Dict, List, Any, Optional
import threading
from queue import Queue
from mcp.server.fastmcp import FastMCP
from binance_mcp_server import binance_ws_api

# Global state to store active subscriptions and their data
active_subscriptions = {}
subscription_data = {}
data_queues = {}

# Function to handle incoming WebSocket messages
async def handle_stream_message(stream_name: str, message: dict):
    """Process incoming WebSocket message and store it in the subscription data."""
    global subscription_data
    
    # Store the latest message for this stream
    subscription_data[stream_name] = message
    
    # If there's a queue for this stream, add the message to it
    if stream_name in data_queues:
        # Add to the queue, but don't block if it's full (discard oldest)
        queue = data_queues[stream_name]
        if queue.full():
            try:
                queue.get_nowait()  # Remove oldest item
            except:
                pass
        queue.put(message)

def register_websocket_commands(mcp: FastMCP):
    """Register MCP commands for WebSocket stream interactions."""
    
    @mcp.tool()
    def subscribe_to_trade_stream(symbol: str) -> dict:
        """Subscribe to real-time trade stream for a symbol.
        
        This establishes a WebSocket connection to receive trade events as they occur.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary with subscription status and information.
        """
        symbol = symbol.lower()
        stream_name = f"{symbol}@trade"
        
        # Check if already subscribed
        if stream_name in active_subscriptions:
            return {
                "status": "already_subscribed",
                "stream": stream_name,
                "message": f"Already subscribed to trade stream for {symbol}"
            }
        
        # Create a queue for this stream's data
        data_queues[stream_name] = Queue(maxsize=100)
        
        # Set up callback function
        async def callback(data):
            await handle_stream_message(stream_name, data)
        
        # Run the subscription in a background task
        async def subscribe_task():
            success = await binance_ws_api.subscribe_to_trade_stream(symbol, callback)
            if success:
                active_subscriptions[stream_name] = {
                    "type": "trade",
                    "symbol": symbol
                }
        
        # Use create_task for async operations
        asyncio.create_task(subscribe_task())
        
        return {
            "status": "subscribing",
            "stream": stream_name,
            "message": f"Subscribing to trade stream for {symbol}"
        }
    
    @mcp.tool()
    def subscribe_to_kline_stream(symbol: str, interval: str = "1m") -> dict:
        """Subscribe to real-time candlestick/kline updates for a symbol.
        
        This establishes a WebSocket connection to receive candlestick data as it's updated.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Candlestick interval (e.g., '1m', '5m', '1h', '1d')
            
        Returns:
            Dictionary with subscription status and information.
        """
        symbol = symbol.lower()
        stream_name = f"{symbol}@kline_{interval}"
        
        # Check if already subscribed
        if stream_name in active_subscriptions:
            return {
                "status": "already_subscribed",
                "stream": stream_name,
                "message": f"Already subscribed to kline stream for {symbol} with interval {interval}"
            }
        
        # Create a queue for this stream's data
        data_queues[stream_name] = Queue(maxsize=100)
        
        # Set up callback function
        async def callback(data):
            await handle_stream_message(stream_name, data)
        
        # Run the subscription in a background task
        async def subscribe_task():
            success = await binance_ws_api.subscribe_to_kline_stream(symbol, interval, callback)
            if success:
                active_subscriptions[stream_name] = {
                    "type": "kline",
                    "symbol": symbol,
                    "interval": interval
                }
        
        # Use create_task for async operations
        asyncio.create_task(subscribe_task())
        
        return {
            "status": "subscribing",
            "stream": stream_name,
            "message": f"Subscribing to kline stream for {symbol} with interval {interval}"
        }
    
    @mcp.tool()
    def subscribe_to_ticker_stream(symbol: str) -> dict:
        """Subscribe to real-time ticker updates for a symbol.
        
        Tickers provide a 24-hour rolling window of trading activity for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary with subscription status and information.
        """
        symbol = symbol.lower()
        stream_name = f"{symbol}@ticker"
        
        # Check if already subscribed
        if stream_name in active_subscriptions:
            return {
                "status": "already_subscribed",
                "stream": stream_name,
                "message": f"Already subscribed to ticker stream for {symbol}"
            }
        
        # Create a queue for this stream's data
        data_queues[stream_name] = Queue(maxsize=100)
        
        # Set up callback function
        async def callback(data):
            await handle_stream_message(stream_name, data)
        
        # Run the subscription in a background task
        async def subscribe_task():
            success = await binance_ws_api.subscribe_to_ticker_stream(symbol, callback)
            if success:
                active_subscriptions[stream_name] = {
                    "type": "ticker",
                    "symbol": symbol
                }
        
        # Use create_task for async operations
        asyncio.create_task(subscribe_task())
        
        return {
            "status": "subscribing",
            "stream": stream_name,
            "message": f"Subscribing to ticker stream for {symbol}"
        }
    
    @mcp.tool()
    def subscribe_to_book_ticker_stream(symbol: str) -> dict:
        """Subscribe to real-time book ticker updates for a symbol.
        
        Book tickers provide the best bid and ask prices and quantities in real-time.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary with subscription status and information.
        """
        symbol = symbol.lower()
        stream_name = f"{symbol}@bookTicker"
        
        # Check if already subscribed
        if stream_name in active_subscriptions:
            return {
                "status": "already_subscribed",
                "stream": stream_name,
                "message": f"Already subscribed to book ticker stream for {symbol}"
            }
        
        # Create a queue for this stream's data
        data_queues[stream_name] = Queue(maxsize=100)
        
        # Set up callback function
        async def callback(data):
            await handle_stream_message(stream_name, data)
        
        # Run the subscription in a background task
        async def subscribe_task():
            success = await binance_ws_api.subscribe_to_book_ticker_stream(symbol, callback)
            if success:
                active_subscriptions[stream_name] = {
                    "type": "bookTicker",
                    "symbol": symbol
                }
        
        # Use create_task for async operations
        asyncio.create_task(subscribe_task())
        
        return {
            "status": "subscribing",
            "stream": stream_name,
            "message": f"Subscribing to book ticker stream for {symbol}"
        }
    
    @mcp.tool()
    def subscribe_to_depth_stream(symbol: str, levels: int = 10) -> dict:
        """Subscribe to real-time order book depth updates for a symbol.
        
        Provides partial order book data at the specified number of levels.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            levels: Number of price levels to include (5, 10, or 20)
            
        Returns:
            Dictionary with subscription status and information.
        """
        symbol = symbol.lower()
        
        # Validate levels
        if levels not in (5, 10, 20):
            return {
                "status": "error",
                "message": f"Invalid depth levels: {levels}. Must be 5, 10, or 20."
            }
        
        stream_name = f"{symbol}@depth{levels}"
        
        # Check if already subscribed
        if stream_name in active_subscriptions:
            return {
                "status": "already_subscribed",
                "stream": stream_name,
                "message": f"Already subscribed to depth stream for {symbol} with {levels} levels"
            }
        
        # Create a queue for this stream's data
        data_queues[stream_name] = Queue(maxsize=100)
        
        # Set up callback function
        async def callback(data):
            await handle_stream_message(stream_name, data)
        
        # Run the subscription in a background task
        async def subscribe_task():
            success = await binance_ws_api.subscribe_to_depth_stream(symbol, callback, levels)
            if success:
                active_subscriptions[stream_name] = {
                    "type": "depth",
                    "symbol": symbol,
                    "levels": levels
                }
        
        # Use create_task for async operations
        asyncio.create_task(subscribe_task())
        
        return {
            "status": "subscribing",
            "stream": stream_name,
            "message": f"Subscribing to depth stream for {symbol} with {levels} levels"
        }
    
    @mcp.tool()
    def list_active_subscriptions() -> dict:
        """List all active WebSocket stream subscriptions.
        
        Returns information about all currently active subscriptions.
        
        Returns:
            Dictionary with the list of active subscriptions and their details.
        """
        return {
            "active_subscriptions": active_subscriptions,
            "count": len(active_subscriptions)
        }
    
    @mcp.tool()
    def get_latest_stream_data(stream_name: str) -> dict:
        """Get the latest data received from a WebSocket stream.
        
        Args:
            stream_name: Name of the stream (e.g., 'btcusdt@trade')
            
        Returns:
            Dictionary with the latest data received from the stream.
        """
        if stream_name not in active_subscriptions:
            return {
                "status": "error",
                "message": f"No active subscription for stream: {stream_name}"
            }
        
        if stream_name not in subscription_data:
            return {
                "status": "pending",
                "message": f"Subscription active but no data received yet for: {stream_name}"
            }
        
        return {
            "status": "success",
            "stream": stream_name,
            "data": subscription_data[stream_name]
        }
    
    @mcp.tool()
    def unsubscribe_from_stream(stream_name: str) -> dict:
        """Unsubscribe from a WebSocket stream.
        
        Args:
            stream_name: Name of the stream to unsubscribe from (e.g., 'btcusdt@trade')
            
        Returns:
            Dictionary with the unsubscription status.
        """
        if stream_name not in active_subscriptions:
            return {
                "status": "error",
                "message": f"No active subscription for stream: {stream_name}"
            }
        
        # Run the unsubscription in a background task
        async def unsubscribe_task():
            success = await binance_ws_api.ws_manager.unsubscribe(stream_name)
            if success:
                # Clean up references
                if stream_name in active_subscriptions:
                    del active_subscriptions[stream_name]
                if stream_name in subscription_data:
                    del subscription_data[stream_name]
                if stream_name in data_queues:
                    del data_queues[stream_name]
        
        # Use create_task for async operations
        asyncio.create_task(unsubscribe_task())
        
        return {
            "status": "unsubscribing",
            "stream": stream_name,
            "message": f"Unsubscribing from stream: {stream_name}"
        }
    
    @mcp.tool()
    def cleanup_all_streams() -> dict:
        """Close all active WebSocket connections and clean up resources.
        
        Returns:
            Dictionary with the cleanup status.
        """
        # Run the cleanup in a background task
        async def cleanup_task():
            await binance_ws_api.cleanup()
            
            # Clear all references
            active_subscriptions.clear()
            subscription_data.clear()
            data_queues.clear()
        
        # Use create_task for async operations
        asyncio.create_task(cleanup_task())
        
        return {
            "status": "cleaning_up",
            "message": "Cleaning up all WebSocket connections and resources"
        } 