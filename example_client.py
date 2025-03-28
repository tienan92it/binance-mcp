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
            # Handle tools that may be returned as tuples or objects
            for tool in tools:
                if isinstance(tool, tuple):
                    # If tool is a tuple, it might be (name, description, schema)
                    tool_name = tool[0] if len(tool) > 0 else "Unknown"
                    tool_desc = tool[1] if len(tool) > 1 else "No description"
                    print(f"- {tool_name}: {tool_desc}")
                else:
                    # If tool is an object with attributes
                    print(f"- {tool.name}: {tool.description}")
            
            # Fetch BTC price
            print("\nFetching BTC price...")
            btc_price_result = await session.call_tool("get_price", arguments={"symbol": "BTCUSDT"})
            # Extract the actual result value
            btc_price = getattr(btc_price_result, "result", btc_price_result)
            print(f"Current BTC price: ${btc_price}")
            
            # Fetch ETH order book
            print("\nFetching ETH order book (top 5 levels)...")
            eth_orderbook_result = await session.call_tool(
                "get_order_book", 
                arguments={"symbol": "ETHUSDT", "depth": 5}
            )
            # Extract the actual result value
            eth_orderbook = getattr(eth_orderbook_result, "result", eth_orderbook_result)
            
            print("ETH Order Book:")
            print("Bids (buy orders):")
            if isinstance(eth_orderbook, dict) and "bids" in eth_orderbook:
                for bid in eth_orderbook["bids"][:5]:
                    print(f"  Price: ${bid[0]}, Quantity: {bid[1]}")
            else:
                print(f"  Unexpected result format: {eth_orderbook}")
                
            print("Asks (sell orders):")
            if isinstance(eth_orderbook, dict) and "asks" in eth_orderbook:
                for ask in eth_orderbook["asks"][:5]:
                    print(f"  Price: ${ask[0]}, Quantity: {ask[1]}")
            else:
                print(f"  Unexpected result format: {eth_orderbook}")
            
            # Fetch BTC historical prices
            print("\nFetching BTC historical prices (last 3 days)...")
            btc_history_result = await session.call_tool(
                "get_historical_prices", 
                arguments={"symbol": "BTCUSDT", "interval": "1d", "limit": 3}
            )
            # Extract the actual result value
            btc_history = getattr(btc_history_result, "result", btc_history_result)
            
            print("BTC Historical Prices (last 3 days):")
            if isinstance(btc_history, list):
                for candle in btc_history:
                    if isinstance(candle, dict):
                        print(f"  Open: ${candle.get('open')}, High: ${candle.get('high')}, Low: ${candle.get('low')}, Close: ${candle.get('close')}, Volume: {candle.get('volume')}")
                    else:
                        print(f"  Unexpected candle format: {candle}")
            else:
                print(f"  Unexpected result format: {btc_history}")
            
            # Get trading fees
            print("\nFetching trading fees...")
            fees_result = await session.call_tool("get_trading_fees")
            # Extract the actual result value
            fees = getattr(fees_result, "result", fees_result)
            
            if isinstance(fees, dict) and "maker_fee" in fees and "taker_fee" in fees:
                print(f"Maker fee: {fees['maker_fee']*100}%")
                print(f"Taker fee: {fees['taker_fee']*100}%")
            else:
                print(f"Unexpected fees format: {fees}")

if __name__ == "__main__":
    asyncio.run(main()) 