# Binance MCP Server

A Model Context Protocol (MCP) server that exposes Binance exchange data to LLM agents.

## Features

- Access live price data for any trading pair
- Retrieve order book snapshots
- Fetch historical price data (OHLCV candles)
- Get exchange information and trading fees
- All data is fetched via public Binance REST API (no API keys required)

## Setup

1. Install the required dependencies:

```bash
pip install mcp requests
```

2. Run the server:

```bash
python -m binance_mcp_server.server
```

## Available Commands

The server exposes the following MCP tools:

### Market Data

- `get_price(symbol)` - Get the latest price for a trading pair (e.g., "BTCUSDT")
- `get_order_book(symbol, depth=10)` - Get the current order book for a trading pair
- `get_historical_prices(symbol, interval="1d", limit=100)` - Get historical OHLCV data

### Market Info

- `get_exchange_info()` - Get exchange information, including supported symbols and trading rules
- `get_trading_fees()` - Get the current default trading fee rates

## Usage with Claude Desktop

To use this server with Claude Desktop:

1. Install the MCP CLI:

```bash
pip install "mcp[cli]"
```

2. Install the server in Claude Desktop:

```bash
mcp install binance_mcp_server/server.py
```

3. You can now use the Binance data tools in Claude Desktop conversations.

## Development

To test the server in development mode:

```bash
mcp dev binance_mcp_server/server.py
```

This will open the MCP Inspector, which allows you to test the server's commands. 