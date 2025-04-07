# binance_ws_api.py
import json
import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any, Union
import websockets
from websockets.exceptions import ConnectionClosed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# WebSocket endpoints
MARKET_WS_BASE_URL = "wss://stream.binance.com:9443"
API_WS_BASE_URL = "wss://ws-api.binance.com:443/ws-api/v3"

# Global connection and subscription state
ws_connections = {}
subscriptions = {}

class BinanceWebSocketManager:
    """Manager for Binance WebSocket connections and subscriptions."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.connections = {}  # Map of connection_id -> websocket connection
        self.subscriptions = {}  # Map of stream_name -> connection_id
        self.callbacks = {}  # Map of stream_name -> callback function
        self.running_tasks = set()  # Set of running tasks
    
    async def connect(self, connection_id: str, base_url: str = MARKET_WS_BASE_URL) -> bool:
        """Establish a WebSocket connection.
        
        Args:
            connection_id: Unique identifier for this connection
            base_url: WebSocket endpoint to connect to
            
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            connection = await websockets.connect(base_url)
            self.connections[connection_id] = connection
            logger.info(f"Established WebSocket connection: {connection_id}")
            
            # Start a task to receive messages
            receive_task = asyncio.create_task(self._receive_messages(connection_id))
            self.running_tasks.add(receive_task)
            receive_task.add_done_callback(self.running_tasks.discard)
            
            return True
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")
            return False
    
    async def disconnect(self, connection_id: str) -> bool:
        """Close a WebSocket connection.
        
        Args:
            connection_id: Identifier for the connection to close
            
        Returns:
            True if disconnection was successful, False otherwise
        """
        if connection_id not in self.connections:
            logger.warning(f"Connection not found: {connection_id}")
            return False
        
        try:
            connection = self.connections[connection_id]
            await connection.close()
            del self.connections[connection_id]
            
            # Remove any subscriptions using this connection
            to_remove = []
            for stream, conn_id in self.subscriptions.items():
                if conn_id == connection_id:
                    to_remove.append(stream)
            
            for stream in to_remove:
                del self.subscriptions[stream]
                if stream in self.callbacks:
                    del self.callbacks[stream]
            
            logger.info(f"Closed WebSocket connection: {connection_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to close WebSocket connection: {e}")
            return False
    
    async def _receive_messages(self, connection_id: str):
        """Background task to receive and process messages for a connection.
        
        Args:
            connection_id: Identifier for the connection to process messages from
        """
        if connection_id not in self.connections:
            logger.error(f"Connection not found for receiver: {connection_id}")
            return
        
        connection = self.connections[connection_id]
        
        try:
            async for message in connection:
                await self._process_message(connection_id, message)
                
        except ConnectionClosed:
            logger.info(f"Connection closed: {connection_id}")
            # Handle reconnection logic if needed
        except Exception as e:
            logger.error(f"Error in message receiver: {e}")
        finally:
            # Clean up if the connection was lost unexpectedly
            if connection_id in self.connections:
                await self.disconnect(connection_id)
    
    async def _process_message(self, connection_id: str, message: str):
        """Process an incoming WebSocket message.
        
        Args:
            connection_id: Identifier for the connection the message came from
            message: The raw message string to process
        """
        try:
            # Parse the message
            data = json.loads(message)
            
            # Handle ping/pong frames for connection keep-alive
            if "ping" in data:
                await self._send_pong(connection_id, data["ping"])
                return
            
            # Handle combined stream messages
            if "stream" in data and "data" in data:
                stream_name = data["stream"]
                stream_data = data["data"]
                
                # Call the appropriate callback if registered
                if stream_name in self.callbacks:
                    callback = self.callbacks[stream_name]
                    await callback(stream_data)
            
            # Handle single stream messages (raw streams)
            else:
                # Try to determine which subscription this is for
                for stream_name, conn_id in self.subscriptions.items():
                    if conn_id == connection_id and stream_name in self.callbacks:
                        callback = self.callbacks[stream_name]
                        await callback(data)
                        break
        
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message as JSON: {message[:100]}...")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _send_pong(self, connection_id: str, ping_payload: Any):
        """Send a pong response to a ping.
        
        Args:
            connection_id: Identifier for the connection to send the pong to
            ping_payload: The payload from the ping message to echo back
        """
        if connection_id not in self.connections:
            return
        
        try:
            connection = self.connections[connection_id]
            pong_message = {"pong": ping_payload}
            await connection.send(json.dumps(pong_message))
        except Exception as e:
            logger.error(f"Error sending pong: {e}")
    
    async def subscribe(self, 
                       stream_name: str, 
                       callback: Callable[[dict], Any], 
                       connection_id: Optional[str] = None,
                       use_combined_stream: bool = True) -> bool:
        """Subscribe to a WebSocket stream.
        
        Args:
            stream_name: Name of the stream to subscribe to (e.g. 'btcusdt@trade')
            callback: Async function to call when a message is received
            connection_id: Optional identifier for an existing connection to use
            use_combined_stream: Whether to use the combined stream endpoint
            
        Returns:
            True if subscription was successful, False otherwise
        """
        # If no connection_id is provided, create a new one
        if not connection_id:
            connection_id = f"conn_{stream_name}_{id(callback)}"
        
        # If the connection doesn't exist yet, create it
        if connection_id not in self.connections:
            if use_combined_stream:
                base_url = f"{MARKET_WS_BASE_URL}/stream"
            else:
                base_url = f"{MARKET_WS_BASE_URL}/ws/{stream_name}"
            
            connected = await self.connect(connection_id, base_url)
            if not connected:
                return False
        
        # Register the subscription and callback
        self.subscriptions[stream_name] = connection_id
        self.callbacks[stream_name] = callback
        
        # If using a combined stream, send the subscription request
        if use_combined_stream:
            try:
                connection = self.connections[connection_id]
                subscribe_msg = {
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": id(callback)
                }
                await connection.send(json.dumps(subscribe_msg))
                logger.info(f"Sent subscription request for: {stream_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to send subscription request: {e}")
                return False
        
        # If using a raw stream, the subscription is already active by connecting to the stream URL
        return True
    
    async def unsubscribe(self, stream_name: str) -> bool:
        """Unsubscribe from a WebSocket stream.
        
        Args:
            stream_name: Name of the stream to unsubscribe from
            
        Returns:
            True if unsubscription was successful, False otherwise
        """
        if stream_name not in self.subscriptions:
            logger.warning(f"No active subscription for: {stream_name}")
            return False
        
        connection_id = self.subscriptions[stream_name]
        
        # Check if we're using a combined stream
        connection = self.connections.get(connection_id)
        if not connection:
            logger.warning(f"Connection not found for: {connection_id}")
            return False
        
        # Check if this is a combined stream by looking at the connection URI
        if "/stream" in str(connection.uri):
            try:
                unsubscribe_msg = {
                    "method": "UNSUBSCRIBE",
                    "params": [stream_name],
                    "id": id(self.callbacks.get(stream_name, lambda: None))
                }
                await connection.send(json.dumps(unsubscribe_msg))
                
                # Remove the subscription and callback
                del self.subscriptions[stream_name]
                if stream_name in self.callbacks:
                    del self.callbacks[stream_name]
                
                logger.info(f"Unsubscribed from: {stream_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to unsubscribe: {e}")
                return False
        else:
            # For raw streams, just disconnect the connection
            return await self.disconnect(connection_id)

# Initialize a singleton WebSocket manager
ws_manager = BinanceWebSocketManager()

# Helper functions for common stream types

async def subscribe_to_trade_stream(symbol: str, callback: Callable[[dict], Any]) -> bool:
    """Subscribe to the trade stream for a symbol.
    
    Args:
        symbol: Trading pair symbol in lowercase (e.g., 'btcusdt')
        callback: Async function to call when a trade message is received
    
    Returns:
        True if subscription was successful, False otherwise
    """
    stream_name = f"{symbol.lower()}@trade"
    return await ws_manager.subscribe(stream_name, callback)

async def subscribe_to_kline_stream(symbol: str, interval: str, callback: Callable[[dict], Any]) -> bool:
    """Subscribe to the kline/candlestick stream for a symbol.
    
    Args:
        symbol: Trading pair symbol in lowercase (e.g., 'btcusdt')
        interval: Kline interval (e.g., '1m', '1h', '1d')
        callback: Async function to call when a kline message is received
    
    Returns:
        True if subscription was successful, False otherwise
    """
    stream_name = f"{symbol.lower()}@kline_{interval}"
    return await ws_manager.subscribe(stream_name, callback)

async def subscribe_to_ticker_stream(symbol: str, callback: Callable[[dict], Any]) -> bool:
    """Subscribe to the ticker stream for a symbol.
    
    Args:
        symbol: Trading pair symbol in lowercase (e.g., 'btcusdt')
        callback: Async function to call when a ticker message is received
    
    Returns:
        True if subscription was successful, False otherwise
    """
    stream_name = f"{symbol.lower()}@ticker"
    return await ws_manager.subscribe(stream_name, callback)

async def subscribe_to_book_ticker_stream(symbol: str, callback: Callable[[dict], Any]) -> bool:
    """Subscribe to the book ticker stream for a symbol.
    
    Args:
        symbol: Trading pair symbol in lowercase (e.g., 'btcusdt')
        callback: Async function to call when a book ticker message is received
    
    Returns:
        True if subscription was successful, False otherwise
    """
    stream_name = f"{symbol.lower()}@bookTicker"
    return await ws_manager.subscribe(stream_name, callback)

async def subscribe_to_all_market_tickers(callback: Callable[[dict], Any]) -> bool:
    """Subscribe to ticker streams for all market pairs.
    
    Args:
        callback: Async function to call when market ticker messages are received
    
    Returns:
        True if subscription was successful, False otherwise
    """
    stream_name = "!ticker@arr"
    return await ws_manager.subscribe(stream_name, callback)

async def subscribe_to_depth_stream(symbol: str, callback: Callable[[dict], Any], levels: Optional[int] = None, update_speed: Optional[int] = None) -> bool:
    """Subscribe to the depth (order book) stream for a symbol.
    
    Args:
        symbol: Trading pair symbol in lowercase (e.g., 'btcusdt')
        callback: Async function to call when depth messages are received
        levels: Optional number of levels to include (5, 10, or 20)
        update_speed: Optional update speed in ms (1000 or 100)
        
    Returns:
        True if subscription was successful, False otherwise
    """
    stream_name = f"{symbol.lower()}@depth"
    
    if levels:
        if levels not in (5, 10, 20):
            logger.warning(f"Invalid depth levels: {levels}. Using default.")
        else:
            stream_name = f"{symbol.lower()}@depth{levels}"
    
    if update_speed == 100:
        stream_name = f"{stream_name}@100ms"
    
    return await ws_manager.subscribe(stream_name, callback)

# Cleanup function for application shutdown
async def cleanup():
    """Close all WebSocket connections when the application is shutting down."""
    for connection_id in list(ws_manager.connections.keys()):
        await ws_manager.disconnect(connection_id) 