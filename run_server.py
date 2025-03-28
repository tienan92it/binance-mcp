# run_server.py
"""
Run script for the Binance MCP Server.
This script makes it easier to run the server from the command line.
"""

from binance_mcp_server.server import mcp

if __name__ == "__main__":
    print("Starting Binance MCP Server...")
    mcp.run()
    print("Binance MCP Server stopped.") 