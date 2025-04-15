# Binance MCP Server

A Model Context Protocol (MCP) server that exposes Binance cryptocurrency exchange data to Large Language Model (LLM) agents. This server allows LLMs to access real-time and historical market data from Binance through a standardized interface.

## Features

- **Live Price Data**: Get current prices for any trading pair on Binance
- **Order Book Access**: Retrieve order book snapshots showing buy/sell interest at different price levels
- **Historical Price Data**: Fetch OHLCV (Open, High, Low, Close, Volume) candlestick data for any timeframe
- **Real-time WebSocket Streams**: Subscribe to real-time trade, ticker, and order book updates via WebSockets
- **Comprehensive Market Data**: Access trades, 24hr statistics, aggregate trades, rolling window data, and more
- **Exchange Information**: Access trading rules, symbol information, and fee structures
- **Read-only Operation**: All data is fetched via Binance's public REST API (no API keys required)
- **MCP Standard Compliant**: Works with any MCP-compatible LLM client

## Requirements

- Python 3.8+
- `mcp` package with CLI tools (`mcp[cli]`)
- `requests` library for REST API
- `websockets` library for WebSocket streams
- `uvicorn` for serving (optional)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/binance_mcp_server.git
cd binance_mcp_server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server Directly

To run the server in standalone mode:

```bash
python run_server.py
```

This will start the MCP server, which will listen for connections via STDIO.

### Development Mode with MCP Inspector

For development and testing, use the MCP Inspector:

```bash
mcp dev run_server.py
```

This opens the MCP Inspector interface where you can test the server's tools interactively.

### Installing in Claude Desktop

To use this server with Claude Desktop:

1. Install the MCP CLI tools if you haven't already:
```bash
pip install "mcp[cli]"
```

2. Install the server in Claude Desktop:
```bash
mcp install run_server.py
```

3. You can now access Binance data directly within your Claude Desktop conversations.

### Example Client

An example client script is provided to demonstrate programmatic usage:

```bash
python example_client.py
```

This script connects to the server and retrieves various types of market data.

## Available Tools

### Connectivity and Basic Info

- **ping_binance()**: Test connectivity to the Binance API server
  - Example: `ping_binance()`

- **get_server_time()**: Get the current server time from Binance
  - Example: `get_server_time()`

### Market Data

- **get_price(symbol)**: Get the current price for a trading pair
  - Example: `get_price(symbol="BTCUSDT")`

- **get_order_book(symbol, depth=10)**: Get the current order book
  - Example: `get_order_book(symbol="ETHUSDT", depth=5)`
  
- **get_historical_prices(symbol, interval="1d", limit=100)**: Get historical OHLCV data
  - Example: `get_historical_prices(symbol="BTCUSDT", interval="1h", limit=24)`
  - Valid intervals: "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"

- **get_ui_klines(symbol, interval="1d", limit=100)**: Get UI-optimized candlestick data
  - Example: `get_ui_klines(symbol="BTCUSDT", interval="1h", limit=24)`

- **get_recent_trades(symbol, limit=20)**: Get the most recent trades for a symbol
  - Example: `get_recent_trades(symbol="BTCUSDT", limit=50)`

- **get_historical_trades(symbol, limit=20, from_id=None)**: Get older trades for a symbol
  - Example: `get_historical_trades(symbol="BTCUSDT", limit=100, from_id=12345)`

- **get_aggregate_trades(symbol, limit=20)**: Get compressed/aggregate trades
  - Example: `get_aggregate_trades(symbol="ETHUSDT", limit=30)`

- **get_24hr_ticker(symbol)**: Get 24-hour price change statistics
  - Example: `get_24hr_ticker(symbol="BNBUSDT")`

- **get_all_24hr_tickers()**: Get 24-hour statistics for all symbols
  - Example: `get_all_24hr_tickers()`

- **get_trading_day_ticker(symbol, type="FULL")**: Get trading day price change statistics
  - Example: `get_trading_day_ticker(symbol="BTCUSDT", type="FULL")`

- **get_all_trading_day_tickers(type="FULL")**: Get trading day statistics for all symbols
  - Example: `get_all_trading_day_tickers(type="MINI")`

- **get_rolling_window_ticker(symbol, window_size="1d", type="FULL")**: Get rolling window price statistics
  - Example: `get_rolling_window_ticker(symbol="BTCUSDT", window_size="4h")`

- **get_all_rolling_window_tickers(window_size="1d", type="FULL")**: Get rolling window stats for all symbols
  - Example: `get_all_rolling_window_tickers(window_size="4h", type="MINI")`

- **get_average_price(symbol)**: Get current average price (5-minute weighted average)
  - Example: `get_average_price(symbol="BTCUSDT")`

- **get_book_ticker(symbol)**: Get best bid/ask prices and quantities
  - Example: `get_book_ticker(symbol="ETHBTC")`

- **get_all_book_tickers()**: Get best bid/ask for all symbols
  - Example: `get_all_book_tickers()`

### Market Info

- **get_exchange_info()**: Get comprehensive exchange information including trading rules and symbol list

- **get_trading_fees()**: Get the default trading fee rates (note: for demonstration purposes, returns default public fees)

### WebSocket Streams

- **subscribe_to_trade_stream(symbol)**: Subscribe to real-time trade events
  - Example: `subscribe_to_trade_stream(symbol="BTCUSDT")`

- **subscribe_to_kline_stream(symbol, interval="1m")**: Subscribe to candlestick/kline updates
  - Example: `subscribe_to_kline_stream(symbol="BTCUSDT", interval="5m")`

- **subscribe_to_ticker_stream(symbol)**: Subscribe to 24hr ticker updates
  - Example: `subscribe_to_ticker_stream(symbol="ETHUSDT")`

- **subscribe_to_book_ticker_stream(symbol)**: Subscribe to best bid/ask updates
  - Example: `subscribe_to_book_ticker_stream(symbol="BNBUSDT")`

- **subscribe_to_depth_stream(symbol, levels=10)**: Subscribe to order book updates
  - Example: `subscribe_to_depth_stream(symbol="BTCUSDT", levels=5)`

- **list_active_subscriptions()**: List all active WebSocket subscriptions
  - Example: `list_active_subscriptions()`

- **get_latest_stream_data(stream_name)**: Get the latest data from a stream
  - Example: `get_latest_stream_data(stream_name="btcusdt@trade")`

- **unsubscribe_from_stream(stream_name)**: Unsubscribe from a stream
  - Example: `unsubscribe_from_stream(stream_name="btcusdt@kline_1m")`

- **cleanup_all_streams()**: Close all WebSocket connections and clean up resources
  - Example: `cleanup_all_streams()`

## Project Structure

```
binance_mcp_server/  
├── binance_api.py       # Core REST API interaction module
├── binance_ws_api.py    # WebSocket connection management
├── commands/            # MCP command definitions  
│   ├── __init__.py  
│   ├── market_data.py   # Price/order book/historical data commands  
│   ├── market_info.py   # Exchange info and metadata commands
│   └── websocket_streams.py  # WebSocket stream commands
└── server.py            # Main MCP server setup and initialization
```

## Examples

### Basic Connectivity

```python
# Check if Binance API is reachable
is_connected = ping_binance()

# Get the current server time (milliseconds since epoch)
server_time = get_server_time()
```

### Getting Current Market Data

```python
# Get the current price of Bitcoin
btc_price = get_price(symbol="BTCUSDT")

# Get detailed 24-hour statistics
btc_stats = get_24hr_ticker(symbol="BTCUSDT")
print(f"BTC price change: {btc_stats['priceChangePercent']}%")
print(f"BTC 24h volume: {btc_stats['volume']} BTC")

# Get rolling window statistics (4-hour window)
btc_4h_stats = get_rolling_window_ticker(symbol="BTCUSDT", window_size="4h")
print(f"BTC 4h price change: {btc_4h_stats['priceChangePercent']}%")
```

### Working with WebSocket Streams

```python
# Subscribe to real-time trade updates
trade_sub = subscribe_to_trade_stream(symbol="BTCUSDT")

# After some time, get the latest trade data
latest_trade = get_latest_stream_data(stream_name="btcusdt@trade")
print(f"Latest trade price: {latest_trade['data']['p']}")

# Subscribe to candlestick updates for chart data
kline_sub = subscribe_to_kline_stream(symbol="ETHUSDT", interval="5m")

# Clean up when done
unsubscribe_from_stream(stream_name="btcusdt@trade")
unsubscribe_from_stream(stream_name="ethusdt@kline_5m")
```

## Implementation Status

For a detailed overview of the implemented and planned API endpoints, refer to the [API Implementation Status](instructions/api-implementation-status.md) document.

## Extending the Server

### Adding New Tools

To add new tools, create appropriate functions in the Binance API module and then register them as MCP tools in one of the command modules.

### Supporting Private API Endpoints

To support authenticated API calls:
1. Modify `binance_api.py` to include authentication
2. Create additional command modules for trading operations
3. Register the new commands in `server.py`

## Troubleshooting

- **Connection Issues**: Ensure the server is running before attempting to connect with a client
- **Rate Limiting**: Binance may rate-limit excessive API calls; consider implementing caching for high-traffic deployments
- **WebSocket Stability**: WebSocket connections may disconnect after 24 hours (Binance limit); the server will attempt to reconnect automatically
- **Data Format**: Different symbols or intervals may return data in slightly different formats

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Binance for providing a comprehensive public API
- The MCP project for standardizing LLM tool interactions 