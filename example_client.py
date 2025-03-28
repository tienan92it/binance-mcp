# example_client.py
"""
Example client script for the Binance MCP Server.
This demonstrates how to connect to the server and use its tools programmatically.
"""

import asyncio
import subprocess
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command=sys.executable,  # Current Python executable
        args=["run_server.py"],  # Run the server script
    )

    # Connect to the server
    print("Connecting to Binance MCP Server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            print("\nAvailable tools:")
            tools = await session.list_tools()
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
            
            # Fetch BTC price
            print("\nFetching BTC price...")
            btc_price = await session.call_tool("get_price", arguments={"symbol": "BTCUSDT"})
            print(f"Current BTC price: ${btc_price}")
            
            # Fetch ETH order book
            print("\nFetching ETH order book (top 5 levels)...")
            eth_orderbook = await session.call_tool(
                "get_order_book", 
                arguments={"symbol": "ETHUSDT", "depth": 5}
            )
            print("ETH Order Book:")
            print("Bids (buy orders):")
            for bid in eth_orderbook["bids"][:5]:
                print(f"  Price: ${bid[0]}, Quantity: {bid[1]}")
            print("Asks (sell orders):")
            for ask in eth_orderbook["asks"][:5]:
                print(f"  Price: ${ask[0]}, Quantity: {ask[1]}")
            
            # Fetch BTC historical prices
            print("\nFetching BTC historical prices (last 3 days)...")
            btc_history = await session.call_tool(
                "get_historical_prices", 
                arguments={"symbol": "BTCUSDT", "interval": "1d", "limit": 3}
            )
            print("BTC Historical Prices (last 3 days):")
            for candle in btc_history:
                print(f"  Open: ${candle['open']}, High: ${candle['high']}, Low: ${candle['low']}, Close: ${candle['close']}, Volume: {candle['volume']}")
            
            # Get trading fees
            print("\nFetching trading fees...")
            fees = await session.call_tool("get_trading_fees")
            print(f"Maker fee: {fees['maker_fee']*100}%")
            print(f"Taker fee: {fees['taker_fee']*100}%")

if __name__ == "__main__":
    asyncio.run(main()) 