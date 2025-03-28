# Binance MCP Server

A Model Context Protocol (MCP) server that exposes Binance cryptocurrency exchange data to Large Language Model (LLM) agents. This server allows LLMs to access real-time and historical market data from Binance through a standardized interface.

## Features

- **Live Price Data**: Get current prices for any trading pair on Binance
- **Order Book Access**: Retrieve order book snapshots showing buy/sell interest at different price levels
- **Historical Price Data**: Fetch OHLCV (Open, High, Low, Close, Volume) candlestick data for any timeframe
- **Exchange Information**: Access trading rules, symbol information, and fee structures
- **Read-only Operation**: All data is fetched via Binance's public REST API (no API keys required)
- **MCP Standard Compliant**: Works with any MCP-compatible LLM client

## Requirements

- Python 3.8+
- `mcp` package with CLI tools (`mcp[cli]`)
- `requests` library

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

### Market Data

- **get_price(symbol)**: Get the current price for a trading pair
  - Example: `get_price(symbol="BTCUSDT")`

- **get_order_book(symbol, depth=10)**: Get the current order book
  - Example: `get_order_book(symbol="ETHUSDT", depth=5)`
  
- **get_historical_prices(symbol, interval="1d", limit=100)**: Get historical OHLCV data
  - Example: `get_historical_prices(symbol="BTCUSDT", interval="1h", limit=24)`
  - Valid intervals: "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"

### Market Info

- **get_exchange_info()**: Get comprehensive exchange information including trading rules and symbol list

- **get_trading_fees()**: Get the default trading fee rates (note: for demonstration purposes, returns default public fees)

## Project Structure

```
binance_mcp_server/  
├── binance_api.py     # Core API interaction module  
├── commands/          # MCP command definitions  
│   ├── __init__.py  
│   ├── market_data.py # Price/order book/historical data commands  
│   └── market_info.py # Exchange info and metadata commands  
└── server.py          # Main MCP server setup and initialization
```

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
- **Data Format**: Different symbols or intervals may return data in slightly different formats

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Binance for providing a comprehensive public API
- The MCP project for standardizing LLM tool interactions 