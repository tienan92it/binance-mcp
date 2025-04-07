# server.py
from mcp.server.fastmcp import FastMCP
# Import our command registration functions
from binance_mcp_server.commands import market_data, market_info, websocket_streams

# 1. Create the MCP server instance with a descriptive name.
# You can also specify dependencies that the server requires at runtime.
mcp = FastMCP("BinanceMarketData", dependencies=["requests", "websockets"])

# 2. Register commands from the command modules.
market_data.register_market_data_commands(mcp)
market_info.register_market_info_commands(mcp)
websocket_streams.register_websocket_commands(mcp)

# 3. (Optional) You could register additional commands or resources here in future, 
#    e.g., private trading actions when API keys are available.

# 4. Start the MCP server when this script is executed.
if __name__ == "__main__":
    # This launches the server (by default, it will listen for MCP client connections via STDIO or SSE).
    mcp.run() 