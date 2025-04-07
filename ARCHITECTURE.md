# Binance MCP Server Architecture

## System Components

```
+-----------------------+       +------------------+       +----------------+
|                       |       |                  |       |                |
|   Binance Exchange    | <---> |  Binance MCP     | <---> |  LLM Agent    |
|   API Endpoints       |       |  Server          |       |  (Claude/GPT)  |
|                       |       |                  |       |                |
+-----------------------+       +------------------+       +----------------+
      ^                               |
      |                               |
      v                               v
+------------------------+    +------------------+
|                        |    |                  |
|  WebSocket Data        |    |  MCP Client      |
|  Streams               |    |  Applications    |
|                        |    |                  |
+------------------------+    +------------------+
```

## Internal Structure

```
+----------------------------------------------------+
|                 Binance MCP Server                 |
|                                                    |
|  +----------------+      +---------------------+   |
|  |                |      |                     |   |
|  | REST API       |      | WebSocket API       |   |
|  | (binance_api)  |      | (binance_ws_api)    |   |
|  |                |      |                     |   |
|  +-------+--------+      +----------+----------+   |
|          ^                          ^              |
|          |                          |              |
|          v                          v              |
|  +-------+------------------------+-+----------+   |
|  |                                             |   |
|  |             Command Modules                 |   |
|  |                                             |   |
|  |  +-------------+  +-------------+  +-----+  |   |
|  |  | market_data |  | market_info |  | ws  |  |   |
|  |  +-------------+  +-------------+  +-----+  |   |
|  |                                             |   |
|  +---------------------+---------------------+--   |
|                        ^                          |
|                        |                          |
|                        v                          |
|  +------------------------------------------+     |
|  |                                          |     |
|  |           MCP Server Interface           |     |
|  |             (FastMCP)                    |     |
|  |                                          |     |
|  +------------------------------------------+     |
|                                                    |
+----------------------------------------------------+
```

## Data Flow

```
+----------------+    HTTP GET    +---------------------------+
| MCP Client     | -------------> | Binance Exchange REST API |
| (Tool Request) |                +---------------------------+
+----------------+                          |
        |                                   v
        |                      +---------------------------+
        |                      | Process & Format Response |
        |                      +---------------------------+
        v                                   |
+----------------+                          v
| MCP Server     | <----- JSON Response ----+
| (Tool Result)  |
+----------------+
```

WebSocket Data Flow:

```
+-------------------+      Subscribe      +-------------------------+
|                   |  ---------------->  |                         |
| WebSocket Command |                     | Binance WebSocket API   |
|                   |  <----------------  |                         |
+--------+----------+    Stream Open      +-------------------------+
         |                                            |
         |                                            v
         |                                 +-------------------------+
         v                                 | WebSocket Message       |
+--------+----------+                      | Processing & Queueing   |
|                   |                      +-------------------------+
| WebSocket Result  |                                 |
| Queue             |                                 |
|                   | <---- Real-time Updates --------+
+-------------------+
```

## Component Responsibilities

### binance_api.py
- Provides functions for accessing REST API endpoints
- Handles HTTP request/response cycle
- Encapsulates error handling and data formatting
- Converts data types (string to numeric)

### binance_ws_api.py
- Manages WebSocket connections
- Handles subscription management
- Processes incoming messages
- Maintains connection state and handles reconnects

### commands/market_data.py
- Defines MCP tools for market data
- Maps tool parameters to API function calls
- Formats responses for MCP protocol

### commands/market_info.py
- Defines MCP tools for exchange information
- Provides metadata about symbols, markets, and exchange rules

### commands/websocket_streams.py
- Defines MCP tools for WebSocket interactions
- Manages subscription lifecycles
- Provides access to real-time data queues

### server.py
- Initializes FastMCP server
- Registers all command modules
- Configures server parameters and dependencies

## Authentication Flow

Future implementation:

```
+-------------+     +------------+     +----------------+
|             |     |            |     |                |
| API Key     | --> | HMAC-SHA   | --> | Request with   |
| Secret Key  |     | Signature  |     | Authentication |
|             |     |            |     |                |
+-------------+     +------------+     +-------+--------+
                                              |
                                              v
                                    +------------------+
                                    |                  |
                                    | Authenticated    |
                                    | Binance API      |
                                    |                  |
                                    +------------------+
``` 