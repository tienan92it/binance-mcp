# Binance Spot API Reference Guide

This document serves as a comprehensive reference for the Binance Spot API, categorizing the various endpoints and explaining how they can be integrated into the MCP server.

## Table of Contents
- [API Base URLs](#api-base-urls)
- [API Categories](#api-categories)
- [Authentication Methods](#authentication-methods)
- [Market Data Endpoints](#market-data-endpoints)
- [Trading Endpoints](#trading-endpoints)
- [Account Endpoints](#account-endpoints)
- [User Data Stream Endpoints](#user-data-stream-endpoints)
- [WebSocket Streams](#websocket-streams)
- [Integration Strategy](#integration-strategy)
- [Implementation Roadmap](#implementation-roadmap)

## API Base URLs

- **REST API**: `https://api.binance.com`
- **WebSocket API**: `wss://ws-api.binance.com:443/ws-api/v3`
- **WebSocket Market Streams**: `wss://stream.binance.com:9443`

## API Categories

The Binance Spot API is organized into several categories:

1. **Market Data API**: Public endpoints that provide market data like prices, order books, and historical trades.
2. **Trading API**: Endpoints for managing orders (requires authentication).
3. **Account API**: Endpoints for managing account information (requires authentication).
4. **User Data Stream**: WebSocket streams for receiving real-time account updates.
5. **Market Data Streams**: WebSocket streams for real-time market data.

## Authentication Methods

Binance offers three authentication methods for API keys:

1. **HMAC SHA256 Signature**: The default method that signs requests with a secret key.
2. **RSA Signature**: Uses PKCS#8 RSA keys for added security.
3. **Ed25519 Signature**: Provides better performance and security than other methods.

When implementing private endpoints, we'll need to support at least HMAC SHA256 signing.

## Market Data Endpoints

| Endpoint | Description | Current Implementation Status |
|----------|-------------|------------------------------|
| `GET /api/v3/ping` | Test connectivity | Implemented in `ping_binance()` |
| `GET /api/v3/time` | Check server time | Implemented in `get_server_time()` |
| `GET /api/v3/exchangeInfo` | Exchange information | Implemented in `get_exchange_info()` |
| `GET /api/v3/depth` | Order book | Implemented in `get_order_book()` |
| `GET /api/v3/trades` | Recent trades | Implemented in `get_recent_trades()` |
| `GET /api/v3/historicalTrades` | Historical trades | Implemented in `get_historical_trades()` |
| `GET /api/v3/aggTrades` | Compressed/Aggregate trades | Implemented in `get_aggregate_trades()` |
| `GET /api/v3/klines` | Kline/Candlestick data | Implemented in `get_historical_prices()` |
| `GET /api/v3/uiKlines` | UIKlines | Implemented in `get_ui_klines()` |
| `GET /api/v3/avgPrice` | Current average price | Implemented in `get_average_price()` |
| `GET /api/v3/ticker/24hr` | 24hr ticker price change statistics | Implemented in `get_24hr_ticker()` |
| `GET /api/v3/ticker/tradingDay` | Trading Day Ticker | Implemented in `get_trading_day_ticker()` |
| `GET /api/v3/ticker/price` | Symbol price ticker | Implemented in `get_price()` |
| `GET /api/v3/ticker/bookTicker` | Symbol order book ticker | Implemented in `get_book_ticker()` |
| `GET /api/v3/ticker` | Rolling window price change statistics | Implemented in `get_rolling_window_ticker()` |

## Trading Endpoints

| Endpoint | Description | Authentication Required | Current Implementation Status |
|----------|-------------|-------------------------|------------------------------|
| `POST /api/v3/order` | New order (TRADE) | Yes | Not implemented |
| `POST /api/v3/order/test` | Test new order (TRADE) | Yes | Not implemented |
| `GET /api/v3/order` | Query order (USER_DATA) | Yes | Not implemented |
| `DELETE /api/v3/order` | Cancel order (TRADE) | Yes | Not implemented |
| `DELETE /api/v3/openOrders` | Cancel All Open Orders on a Symbol (TRADE) | Yes | Not implemented |
| `POST /api/v3/order/cancelReplace` | Cancel an Existing Order and Send a New Order (TRADE) | Yes | Not implemented |
| `PUT /api/v3/order/keepPriority` | Order Amend Keep Priority (TRADE) | Yes | Not implemented |
| `GET /api/v3/openOrders` | Current open orders (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/allOrders` | All orders (USER_DATA) | Yes | Not implemented |
| `POST /api/v3/sor/order` | New order using SOR (TRADE) | Yes | Not implemented |
| `POST /api/v3/sor/order/test` | Test new order using SOR (TRADE) | Yes | Not implemented |

## Order List Endpoints

| Endpoint | Description | Authentication Required | Current Implementation Status |
|----------|-------------|-------------------------|------------------------------|
| `POST /api/v3/order/oco` | New OCO (TRADE) | Yes | Not implemented |
| `POST /api/v3/orderList` | New Order list (TRADE) | Yes | Not implemented |
| `DELETE /api/v3/orderList` | Cancel Order list (TRADE) | Yes | Not implemented |
| `GET /api/v3/orderList` | Query Order list (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/allOrderList` | Query all Order lists (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/openOrderList` | Query Open Order lists (USER_DATA) | Yes | Not implemented |

## Account Endpoints

| Endpoint | Description | Authentication Required | Current Implementation Status |
|----------|-------------|-------------------------|------------------------------|
| `GET /api/v3/account` | Account information (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/myTrades` | Account trade list (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/rateLimit/order` | Query current order count (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/preventedMatches` | Query Prevented Matches (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/allocations` | Query Allocations (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/commissionRates` | Query Commission Rates (USER_DATA) | Yes | Not implemented |
| `GET /api/v3/orderAmendment` | Query Order Amendments (USER_DATA) | Yes | Not implemented |

## User Data Stream Endpoints

| Endpoint | Description | Authentication Required | Current Implementation Status |
|----------|-------------|-------------------------|------------------------------|
| `POST /api/v3/userDataStream` | Create a listenKey (USER_STREAM) | Yes | Not implemented |
| `PUT /api/v3/userDataStream` | Keep-alive a listenKey (USER_STREAM) | Yes | Not implemented |
| `DELETE /api/v3/userDataStream` | Close a listenKey (USER_STREAM) | Yes | Not implemented |

## WebSocket Streams

### WebSocket API

The WebSocket API provides functionality similar to the REST API but over a persistent connection. It includes:

- Market data requests
- Trading operations
- Account information
- User data stream subscriptions

### Market Data Streams

| Stream | Description | Current Implementation Status |
|--------|-------------|------------------------------|
| `<symbol>@aggTrade` | Aggregate trade streams | Implemented in `subscribe_to_trade_stream()` |
| `<symbol>@trade` | Trade streams | Implemented in `subscribe_to_trade_stream()` |
| `<symbol>@kline_<interval>` | Kline/Candlestick streams | Implemented in `subscribe_to_kline_stream()` |
| `<symbol>@miniTicker` | Individual symbol mini ticker | Not implemented |
| `!miniTicker@arr` | All market mini tickers | Not implemented |
| `<symbol>@ticker` | Individual symbol ticker | Implemented in `subscribe_to_ticker_stream()` |
| `!ticker@arr` | All market tickers | Not implemented |
| `<symbol>@windowTicker_<window_size>` | Individual symbol rolling window statistics | Not implemented |
| `!windowTicker_<window_size>@arr` | All market rolling window statistics | Not implemented |
| `<symbol>@bookTicker` | Individual symbol book ticker | Implemented in `subscribe_to_book_ticker_stream()` |
| `<symbol>@avgPrice` | Average price | Not implemented |
| `<symbol>@depth<levels>[@100ms]` | Partial book depth streams | Implemented in `subscribe_to_depth_stream()` |
| `<symbol>@depth[@100ms]` | Diff. depth stream | Not implemented |

## Integration Strategy

Based on the available Binance Spot API endpoints and our current implementation, we'll follow these integration strategies:

### For REST API Endpoints:

1. **Extend `binance_api.py`** with new functions that call additional endpoints
2. **Create new command modules** for different API categories
3. **Register new MCP tools** in the appropriate command registration functions

### For WebSocket Endpoints:

1. **Create a new `binance_ws_api.py`** module for WebSocket connections
2. **Implement connection management** for persistent WebSocket connections
3. **Add subscription management** for different market data streams
4. **Create WebSocket event handlers** to process incoming data

## Implementation Roadmap

### Completed Implementations

**Market Data REST Endpoints:**
- Basic connectivity (ping, server time)
- Symbol price data
- Order book data
- Historical klines/candlesticks
- Recent and historical trades
- Aggregate trades
- Average price
- 24hr ticker price change statistics
- Book ticker data
- UI-optimized klines
- Trading day ticker
- Rolling window statistics

**WebSocket Market Data Streams:**
- Trade streams
- Kline/candlestick streams
- Ticker streams
- Book ticker streams
- Depth (order book) streams

### Future Implementation Priorities

1. **Authenticated Endpoints**
   - Account information
   - Current open orders
   - Order placement/cancellation

2. **Additional WebSocket Streams**
   - All market tickers
   - Mini-ticker streams
   - Diff. depth stream

3. **User Data Streams**
   - Listen key management
   - Account update streams
   - Order update streams

4. **Advanced Trading Features**
   - OCO orders
   - Order lists
   - SOR orders 