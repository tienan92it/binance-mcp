# Developer Guide: Extending the Binance MCP Server

This guide provides instructions for developers who want to extend the Binance MCP Server with additional functionality.

## Project Structure

```
binance_mcp_server/
├── binance_api.py           # REST API functions
├── binance_ws_api.py        # WebSocket API implementation
├── commands/                # MCP command modules
│   ├── __init__.py
│   ├── market_data.py       # Market data commands
│   ├── market_info.py       # Exchange info commands
│   └── websocket_streams.py # WebSocket stream commands
├── server.py                # Main server initialization
├── instructions/            # Documentation
└── tests/                   # Unit tests
```

## Development Workflow

Follow these steps when extending the server:

1. Add new API functions to the appropriate core module (`binance_api.py` or `binance_ws_api.py`)
2. Create MCP tools that wrap these functions in a command module (in the `commands/` directory)
3. Update the server initialization in `server.py` if needed
4. Update documentation to reflect the new functionality
5. Add tests for the new functionality

## Adding New REST API Endpoints

### Step 1: Add a Function to `binance_api.py`

When adding a new REST API endpoint, follow this pattern:

```python
def get_new_endpoint_data(symbol: str, param1: int = None, param2: str = None):
    """
    Fetch data from the new endpoint.
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTCUSDT')
        param1: Optional parameter 1
        param2: Optional parameter 2
        
    Returns:
        The processed response data
        
    Raises:
        Exception: If the request fails
    """
    params = {'symbol': symbol}
    if param1 is not None:
        params['param1'] = param1
    if param2 is not None:
        params['param2'] = param2
        
    # Make the API request
    response = requests.get(f"{BASE_URL}/api/v3/newEndpoint", params=params)
    
    # Check for errors
    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
    data = response.json()
    
    # Process the data (convert strings to numbers, etc.)
    # For example:
    for item in data:
        if 'price' in item:
            item['price'] = float(item['price'])
            
    return data
```

### Step 2: Create an MCP Tool in a Command Module

Add a new function to the appropriate command module:

```python
# In commands/market_data.py or another suitable module

@mcp.tool()
def get_new_data(symbol: str, param1: int = None, param2: str = None):
    """
    Get data from the new endpoint.
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTCUSDT')
        param1: Optional parameter 1
        param2: Optional parameter 2
        
    Returns:
        The processed data from the endpoint
    """
    try:
        result = binance_api.get_new_endpoint_data(symbol, param1, param2)
        return result
    except Exception as e:
        return {"error": str(e)}
```

## Adding WebSocket Streams

### Step 1: Add Support in `binance_ws_api.py`

First, ensure the WebSocket manager supports the new stream type:

```python
# In binance_ws_api.py

# Add a new stream name formatter if needed
def get_new_stream_name(symbol: str, param: str = None):
    """Format the new stream name according to Binance's conventions."""
    symbol = symbol.lower()
    if param:
        return f"{symbol}@newStream_{param}"
    return f"{symbol}@newStream"

# The stream will be handled by the existing WebSocketManager's
# message processing system, but you may need to add specific 
# parsing logic if the data format is unique
```

### Step 2: Create a Subscription Function in `websocket_streams.py`

```python
# In commands/websocket_streams.py

@mcp.tool()
async def subscribe_to_new_stream(symbol: str, param: str = None, queue_size: int = 100):
    """
    Subscribe to a new type of real-time stream.
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTCUSDT')
        param: Optional parameter for the stream
        queue_size: Maximum number of messages to keep in the queue
        
    Returns:
        A subscription ID that can be used to fetch data
    """
    try:
        # Check if already subscribed
        stream_name = binance_ws_api.get_new_stream_name(symbol, param)
        if stream_name in ws_manager.active_streams:
            return {
                "subscription_id": stream_name,
                "status": "already_subscribed",
                "message": f"Already subscribed to {stream_name}"
            }
            
        # Create a queue for this subscription
        queue = asyncio.Queue(maxsize=queue_size)
        
        # Subscribe using the WebSocket manager
        await ws_manager.subscribe(
            stream_name,
            lambda msg: asyncio.create_task(queue.put(msg))
        )
        
        # Store the queue for data retrieval
        active_subscriptions[stream_name] = {
            "queue": queue,
            "latest_data": None,
            "created_at": time.time()
        }
        
        return {
            "subscription_id": stream_name,
            "status": "subscribed",
            "message": f"Successfully subscribed to {stream_name}"
        }
        
    except Exception as e:
        return {"error": str(e)}
```

### Step 3: Add a Data Retrieval Function

```python
@mcp.tool()
async def get_new_stream_data(subscription_id: str, latest_only: bool = True):
    """
    Get data from a new stream subscription.
    
    Args:
        subscription_id: The subscription ID returned from subscribe_to_new_stream
        latest_only: If True, return only the latest message; otherwise, return all queued messages
        
    Returns:
        The stream data or an error message
    """
    if subscription_id not in active_subscriptions:
        return {"error": f"No active subscription found with ID: {subscription_id}"}
        
    subscription = active_subscriptions[subscription_id]
    
    if latest_only and subscription["latest_data"]:
        return {"data": subscription["latest_data"]}
        
    # Get all queued messages
    messages = []
    try:
        # Non-blocking check of the queue
        while not subscription["queue"].empty():
            msg = subscription["queue"].get_nowait()
            subscription["latest_data"] = msg  # Update latest data
            messages.append(msg)
            subscription["queue"].task_done()
    except asyncio.QueueEmpty:
        pass
        
    if not messages and subscription["latest_data"]:
        return {"data": subscription["latest_data"], "note": "No new messages, returning latest known data"}
        
    return {"data": messages if len(messages) > 0 else None}
```

## Updating Server Registration

When adding new command modules, update `server.py` to register them:

```python
# In server.py

from binance_mcp_server.commands import (
    market_data,
    market_info,
    websocket_streams,
    your_new_module  # Import your new module
)

def create_mcp_server():
    # Create FastMCP instance
    mcp_instance = FastMCP(
        # ... existing configuration ...
        dependencies=["requests", "websockets", "uvicorn"]  # Add any new dependencies
    )
    
    # Register commands from all modules
    market_data.register_market_data_commands(mcp_instance)
    market_info.register_market_info_commands(mcp_instance)
    websocket_streams.register_websocket_commands(mcp_instance)
    your_new_module.register_your_commands(mcp_instance)  # Register your new commands
    
    return mcp_instance
```

## Error Handling Best Practices

1. **Wrap API calls in try/except blocks**:
   ```python
   try:
       result = api_function()
       return result
   except Exception as e:
       return {"error": str(e)}
   ```

2. **Validate parameters before making API calls**:
   ```python
   if not symbol:
       return {"error": "Symbol parameter is required"}
   ```

3. **Provide informative error messages**:
   ```python
   except Exception as e:
       return {
           "error": str(e),
           "details": {
               "endpoint": endpoint,
               "parameters": params
           }
       }
   ```

## Type Conversion Guidelines

Binance often returns numeric values as strings. Convert them to appropriate types:

```python
# Convert string prices to floats
for item in data:
    if 'price' in item:
        item['price'] = float(item['price'])
    if 'quantity' in item:
        item['quantity'] = float(item['quantity'])
```

## WebSocket Resource Management

1. **Clean up inactive connections**:
   ```python
   @mcp.tool()
   async def cleanup_inactive_subscriptions(max_age_seconds: int = 3600):
       """Remove subscriptions that haven't been accessed for the specified time."""
       now = time.time()
       count = 0
       
       for stream_id in list(active_subscriptions.keys()):
           sub = active_subscriptions[stream_id]
           if now - sub["last_accessed"] > max_age_seconds:
               await ws_manager.unsubscribe(stream_id)
               del active_subscriptions[stream_id]
               count += 1
               
       return {"removed_count": count}
   ```

2. **Track subscription usage**:
   ```python
   # Update last_accessed timestamp when data is retrieved
   subscription["last_accessed"] = time.time()
   ```

## Testing New Features

Create tests for new functionality in the `tests/` directory:

```python
# In tests/test_new_feature.py

import unittest
from unittest.mock import patch, MagicMock
from binance_mcp_server import binance_api

class TestNewFeature(unittest.TestCase):
    @patch('binance_mcp_server.binance_api.requests.get')
    def test_get_new_endpoint_data(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"price": "123.45", "quantity": "1.23"}]
        mock_get.return_value = mock_response
        
        # Call the function
        result = binance_api.get_new_endpoint_data("BTCUSDT")
        
        # Verify the result
        self.assertEqual(result[0]["price"], 123.45)
        self.assertEqual(result[0]["quantity"], 1.23)
        
        # Verify the API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["symbol"], "BTCUSDT")
```

## Documentation

When adding new features, update the following documentation:

1. Add the new feature to `instructions/api-implementation-status.md`
2. Update the README with examples of the new functionality
3. Add any necessary details to `instructions/binance-api-reference.md`

## Best Practices

1. **Follow existing code patterns**: Match the style of existing code
2. **Use descriptive docstrings**: Make functions self-documenting with clear docstrings
3. **Handle edge cases**: Consider how your code handles unexpected inputs
4. **Resource cleanup**: Ensure WebSocket connections and subscriptions can be cleaned up
5. **Parameter validation**: Validate inputs before making API calls
6. **Error reporting**: Provide clear error messages that are helpful for debugging 