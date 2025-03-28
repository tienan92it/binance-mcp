# commands/market_info.py
from mcp.server.fastmcp import FastMCP
from binance_mcp_server import binance_api

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