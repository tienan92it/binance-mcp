# Building an MCP Server for Binance Data with Python

In this tutorial, we will build a **Model Context Protocol (MCP)** server in Python that exposes Binance exchange data to Large Language Model (LLM) agents. We’ll use the official Python MCP SDK to define structured commands (tools/resources) that map to Binance’s REST API endpoints. The project will be organized for clarity, separating the Binance API integration, command definitions, and core server setup. Each step below includes code examples and explanations, guiding you through the implementation and design decisions.

## 1. Project Setup and Dependencies

First, set up a Python project and install necessary packages. We need the **MCP SDK** and an HTTP client for Binance’s REST API (we’ll use `requests` for simplicity):

```bash
# Create a project directory and navigate into it
mkdir binance_mcp_server && cd binance_mcp_server

# (Optional) Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the MCP SDK and requests library
pip install mcp requests
```

The MCP SDK will let us easily create an MCP server and define commands as Python functions. The `requests` library will handle HTTP calls to Binance’s REST endpoints (we won’t use WebSockets as per requirements). 

**Project Structure:** Create the following file layout to organize the code: 

```
binance_mcp_server/  
├── server.py          # Core MCP server setup and launch  
├── binance_api.py     # Module for Binance REST API interactions  
└── commands/          # Package for MCP command definitions  
    ├── __init__.py  
    ├── market_data.py # Commands for live prices, historical data, order book  
    └── market_info.py # Commands for exchange info, trading fees, metadata  
```

This structure separates concerns: 
- **`binance_api.py`:** Low-level functions to call Binance’s REST API.  
- **`commands/`:** High-level MCP command definitions that use `binance_api` functions.  
- **`server.py`:** Initializes the MCP server and registers all commands.

## 2. Implementing Binance REST API Module (`binance_api.py`)

Next, implement the module that interacts with Binance’s public REST API. This module will contain helper functions to fetch data like current prices, historical candlesticks, order book snapshots, etc. All functions use **public endpoints** (no API key required). We’ll ensure only HTTP GET requests are used (no WebSockets).

Open `binance_api.py` and add the following code:

```python
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
```

**Key points in the implementation:**

- We set a `BASE_URL` for Binance’s API (`api.binance.com`). All requests append specific path endpoints to this base.
- Each function uses `requests.get` with appropriate query parameters. We check `resp.ok` (HTTP 200) and raise an error if the request failed, including the status code and response text for debugging.
- We parse the JSON response:
  - `get_live_price`: returns a single floating-point price value from the JSON (after converting from string).
  - `get_order_book`: returns the JSON dictionary containing bids and asks arrays.
  - `get_historical_klines`: returns a list of candlestick data points. We choose to parse the first 6 fields (timestamp, OHLC, volume) into a list of dictionaries for clarity. This gives structured historical data up to the requested `limit`.
  - `get_exchange_info`: returns the full JSON of exchange info (which includes server time, rate limits, and a list of symbols with trading rules).
  - `get_trading_fees`: since the actual trading fee endpoint (`/sapi/v1/asset/tradeFee`) requires API keys and signing, we provide a default fee structure as a placeholder. This returns a simple dictionary with typical maker/taker fees (0.1% each). In a real scenario, you would integrate an authenticated request here once API keys are configured.

All functions are stateless and purely fetch data (read-only). We avoid using any WebSocket endpoints – everything is done via REST GET calls to satisfy the requirement of REST-based access only.

## 3. Defining MCP Commands for Binance Data (`commands/` package)

With the data-fetching functions in place, we can define MCP commands that LLM agents can invoke. Each command will correspond to a Binance data function we wrote. We will use the MCP SDK’s decorators to register these commands as **tools** (for actions) or **resources** (for data retrieval) on the server. 

*MCP Tools vs Resources:* In MCP, a **tool** is an operation (like an RPC or function call) that the LLM can execute, often with parameters (similar to a POST action). A **resource** provides context/data (similar to a GET request) and is usually referenced by a URI scheme ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=,reusable%20templates%20for%20LLM)). In this server, we’ll expose Binance data primarily as tools (functions returning data on demand), since these suit query-style interactions. (You could also expose static data as resources with custom URI schemes, but we’ll keep things simple with tools.)

Create the `commands/market_data.py` for price and market data commands, and `commands/market_info.py` for meta-information commands:

**`commands/market_data.py`:** (Live prices, historical data, order book)

```python
# commands/market_data.py
from mcp.server.fastmcp import FastMCP
import binance_api

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
```

**`commands/market_info.py`:** (Exchange info, trading fees, other metadata)

```python
# commands/market_info.py
from mcp.server.fastmcp import FastMCP
import binance_api

def register_market_info_commands(mcp: FastMCP):
    """Register MCP commands for exchange information and metadata."""
    
    @mcp.tool()
    def get_exchange_info() -> dict:
        """Get Binance exchange information, including supported symbols and trading rules."""
        return binance_api.get_exchange_info()
    
    @mcp.tool()
    def get_trading_fees() -> dict:
        """Get the current trading fee rates (maker/taker) on Binance.
        
        Note: This uses default public fee rates. Actual user-specific fees would require API keys.
        """
        return binance_api.get_trading_fees()
```

**About the command definitions:**

- We define functions and decorate them with `@mcp.tool()` to register as MCP tools on the server. The function name (e.g., `get_price`) will become the tool name that an agent can call, and the docstring serves as its description for the LLM.
- The `register_*_commands` functions take the `mcp: FastMCP` instance and attach multiple commands. We call the corresponding `binance_api` functions inside each command to retrieve data.
- **`get_price(symbol)`** – returns the latest price as a float. The agent can call this with a symbol like `"BTCUSDT"` to get the current price.  
- **`get_order_book(symbol, depth)`** – returns a dictionary of the order book. We use a default `depth=10` (top 10 bids and asks). The Binance API requires specific depth values; we note this in the docstring. The result includes lists of bids and asks with price and quantity.  
- **`get_historical_prices(symbol, interval, limit)`** – returns a list of historical price data points for the given interval. By default, it fetches 1-day candles (`"1d"`) for the last 100 days. Agents can specify shorter intervals like `"1h"` for hourly data or `"1m"` for minute data. We limited the default `limit` to 100 for performance, but this can be adjusted (Binance allows up to 1000 candles per request).  
- **`get_exchange_info()`** – returns a dictionary of comprehensive exchange info: trading rules, symbol list, rate limits, etc. An agent might use this to discover available trading pairs or rule constraints. This data can be large, so in practice an LLM might not request it frequently, but it’s available if needed.  
- **`get_trading_fees()`** – returns a dictionary of maker and taker fee rates. Here we simply return the default 0.1% fees. The docstring clarifies that a real implementation would require authentication. This shows how the server can be designed to include **write**-related or account-specific data in the future. For now, it’s read-only static data.

All these commands are read-only operations aligning with public API data. In an MCP context, these would typically be considered *tools* because they perform an action (HTTP request) and return a result. If we had static context data to load, we might use `@mcp.resource` with a URI (for example, an alternative design could expose `exchangeInfo` via a URI like `binance://exchange-info` as a resource).

## 4. Setting Up the MCP Server (`server.py`)

Now, bring everything together in the main server script. In `server.py` we will:

- Instantiate the MCP server (using `FastMCP` from the MCP SDK).
- Register all commands by calling the registration functions from our commands modules.
- Run the server so it’s ready to accept connections from LLM agents.

Open `server.py` and write the following:

```python
# server.py
from mcp.server.fastmcp import FastMCP
# Import our command registration functions
from commands import market_data, market_info

# 1. Create the MCP server instance with a descriptive name.
# You can also specify dependencies that the server requires at runtime.
mcp = FastMCP("BinanceMarketData", dependencies=["requests"])

# 2. Register commands from the command modules.
market_data.register_market_data_commands(mcp)
market_info.register_market_info_commands(mcp)

# 3. (Optional) You could register additional commands or resources here in future, 
#    e.g., private trading actions when API keys are available.

# 4. Start the MCP server when this script is executed.
if __name__ == "__main__":
    # This launches the server (by default, it will listen for MCP client connections via STDIO or SSE).
    mcp.run()
```

**Explanation:**

- We create a `FastMCP` server named `"BinanceMarketData"`. The name is arbitrary but should describe the server’s purpose (it may be shown to users or in agent tool listings). We include `requests` in the `dependencies` list – this is a hint for MCP clients (like agent orchestrators) that our server uses `requests` internally. The MCP framework can use this to ensure the environment has that library. We could also list other packages (e.g., if we used `pandas` for data processing, we’d list it here).
- We call our registration functions to attach all commands to the `mcp` instance. Under the hood, the `@mcp.tool()` decorator in those functions uses the `mcp` instance to register each tool along with its signature and docstring. After these calls, the MCP server “knows” about `get_price`, `get_order_book`, etc.
- Finally, we use `mcp.run()` inside a `__main__` guard. This will start the server event loop. By default, `FastMCP.run()` will handle incoming MCP connections. If you run `python server.py`, it will start a **STDIO-based MCP server** (useful for running as a subprocess tool). If you wanted to serve it as a remote server, the MCP SDK also supports an SSE (Server-Sent Events over HTTP) mode (e.g., `mcp.sse_app()` for integration with an ASGI server), but for simplicity we stick with the default.

At this point, our MCP server is fully implemented. We have a clear separation between Binance API logic and MCP command definitions, which makes the code easier to maintain:

- If Binance changes an endpoint or if we want to switch to a different data source, we update `binance_api.py` without touching the MCP definitions.
- If we want to add new commands (for example, a `get_recent_trades` or even future trading actions like `place_order` once authenticated), we can add them in the appropriate module and call its registration function in `server.py`.

## 5. Running and Using the MCP Server

With all code in place, run the server to ensure it starts correctly:

```bash
python server.py
```

This will launch the MCP server. By default, it will wait for an agent to connect. There are a couple of ways to integrate this with an LLM agent:

- **Using an MCP-compatible agent framework (Agno or OpenAI Agents SDK):** In your agent setup, you would start or connect to this MCP server. For example, with OpenAI’s Agents SDK, you could use `MCPServerStdio` or `MCPServerSse` to connect the agent to the running server ([Model context protocol (MCP) - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/mcp/#:~:text=Using%20MCP%20servers)) ([GitHub - modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients](https://github.com/modelcontextprotocol/python-sdk#:~:text=mcp%20%3D%20FastMCP%28)). In Agno, you can configure the agent to use this server as a tool source (Agno supports MCP integration to let the agent call external tools).
- **Testing with the MCP CLI (Inspector):** The MCP SDK provides a CLI for development. You can run `mcp dev server.py` to interactively test the server. This will list the available tools and allow you to call them manually. For example, you can list tools with something akin to `list_tools()` and you should see `get_price`, `get_order_book`, etc., each with their parameters and docstrings. You can then invoke a tool (the exact CLI commands may vary with MCP versions, but the dev inspector typically shows how to call a tool and see its output).

When an LLM agent is connected to this MCP server, it will receive the list of these tools (commands). The agent might ask for data like:

- *“What’s the current price of BTCUSDT?”* – The agent can call the `get_price("BTCUSDT")` tool, and the server will return the latest price from Binance.  
- *“Show me the last 30 days of prices for ETHUSDT.”* – The agent can call `get_historical_prices("ETHUSDT", interval="1d", limit=30)` to get the daily OHLC data for the past 30 days, then reason or respond based on that.  
- *“How deep is the order book on BNBBTC right now?”* – The agent could call `get_order_book("BNBBTC", depth=5)` to get the top 5 bids/asks on the BNBBTC order book.  
- *“What trading fees does Binance charge?”* – The agent calls `get_trading_fees()` and the server returns the default fee rates.

Because this server is using only public endpoints, it doesn’t require API keys to run. It’s a safe starting point. **Design note:** if you later need to support private endpoints (like placing orders or querying account info), you can extend `binance_api.py` with authenticated requests (Binance uses API key/secret and HMAC signatures for those). You would then add MCP tools for those actions (mark them as sensitive or restricted as needed). The current architecture makes it straightforward to add such features without altering the existing public data commands.

## 6. Architectural Considerations

- **Statelessness:** Our MCP server functions are stateless (each call fetches fresh data from Binance). This is simple and ensures the LLM always gets up-to-date information. However, calling the Binance API on each request can be rate-limited. In a high-frequency scenario, consider caching responses (like caching `exchangeInfo` or recent prices) to reduce redundant calls. For instance, the Alphavantage MCP server example used an in-memory cache for recent data to avoid hitting API limits too often.
- **Error Handling:** We included basic error handling (raising exceptions on HTTP errors or unexpected responses). In an MCP server, if a tool raises an exception, it will usually propagate back to the agent as an error message. You might want to catch exceptions and return a clean error result or message, depending on how you want the agent to handle failures. For example, if an invalid symbol is requested, Binance returns an error JSON; we could intercept that and return a message like “Symbol not found.” 
- **Tools vs Resources:** We chose to implement everything as tools (functions). Tools in MCP can be thought of like POST actions (even though our use-case is data retrieval). Alternatively, some of these could be **resources** – for example, one could define `@mcp.resource("binance://orderbook/{symbol}")` to fetch an order book as read-only context. Resources are useful if you want the agent to *load* data into its context (prompt) directly. In practice, whether to use a tool or resource depends on how the agent is going to use the data. Our use of tools is adequate for most query/response usage. 
- **Security:** Since we are only accessing public data, security concerns are minimal. If extending to private endpoints, be cautious with API keys. Do not expose keys via the MCP interface. Instead, load them from environment or secure storage (as we hinted with `os.getenv`). The MCP server runs on your machine or infrastructure, and the agent’s LLM only receives the data you return, so secrets should remain safe on the server side.
