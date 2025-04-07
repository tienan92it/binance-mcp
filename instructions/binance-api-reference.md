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
| `GET /api/v3/ping` | Test connectivity | Not implemented |
| `GET /api/v3/time` | Check server time | Not implemented |
| `GET /api/v3/exchangeInfo` | Exchange information | Implemented in `get_exchange_info()` |
| `GET /api/v3/depth` | Order book | Implemented in `get_order_book()` |
| `GET /api/v3/trades` | Recent trades | Not implemented |
| `GET /api/v3/historicalTrades` | Historical trades | Not implemented |
| `GET /api/v3/aggTrades` | Compressed/Aggregate trades | Not implemented |
| `GET /api/v3/klines` | Kline/Candlestick data | Implemented in `get_historical_klines()` |
| `GET /api/v3/uiKlines` | UIKlines | Not implemented |
| `GET /api/v3/avgPrice` | Current average price | Not implemented |
| `GET /api/v3/ticker/24hr` | 24hr ticker price change statistics | Not implemented |
| `GET /api/v3/ticker/tradingDay` | Trading Day Ticker | Not implemented |
| `GET /api/v3/ticker/price` | Symbol price ticker | Implemented in `get_live_price()` |
| `GET /api/v3/ticker/bookTicker` | Symbol order book ticker | Not implemented |
| `GET /api/v3/ticker` | Rolling window price change statistics | Not implemented |

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
| `<symbol>@aggTrade` | Aggregate trade streams | Not implemented |
| `<symbol>@trade` | Trade streams | Not implemented |
| `<symbol>@kline_<interval>` | Kline/Candlestick streams | Not implemented |
| `<symbol>@miniTicker` | Individual symbol mini ticker | Not implemented |
| `!miniTicker@arr` | All market mini tickers | Not implemented |
| `<symbol>@ticker` | Individual symbol ticker | Not implemented |
| `!ticker@arr` | All market tickers | Not implemented |
| `<symbol>@windowTicker_<window_size>` | Individual symbol rolling window statistics | Not implemented |
| `!windowTicker_<window_size>@arr` | All market rolling window statistics | Not implemented |
| `<symbol>@bookTicker` | Individual symbol book ticker | Not implemented |
| `<symbol>@avgPrice` | Average price | Not implemented |
| `<symbol>@depth<levels>[@100ms]` | Partial book depth streams | Not implemented |
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

Priority order for implementation:

1. **Additional Market Data REST Endpoints**
   - Recent trades
   - Compressed/Aggregate trades
   - Current average price
   - 24hr ticker price change statistics
   - Symbol order book ticker

2. **Basic Authenticated Endpoints**
   - Account information
   - Current open orders
   - Order placement/cancellation

3. **WebSocket Market Data Streams**
   - Aggregate trade streams
   - Kline/Candlestick streams
   - Ticker streams
   - Book ticker streams

4. **WebSocket User Data Streams**
   - Listen key management
   - Account update streams
   - Order update streams

5. **Advanced Trading Features**
   - OCO orders
   - Order lists
   - SOR orders 