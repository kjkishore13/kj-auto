# KJs TRD Trading Terminal - API Reference

## Base URL

http://localhost:5000/api

## Authentication

Authorization: Bearer YOUR_API_KEY

---

## Endpoints

### 1. System Status

GET /api/status

Returns the current system status.

Response:
{
    "status": "running",
    "runtime": "online",
    "market_data": "connected",
    "broker": "dhan",
    "notification": "telegram",
    "database": "connected",
    "uptime": "2h 14m",
    "memory": "342MB",
    "running_modules": 4
}

---

### 2. Modules

#### Get All Modules

GET /api/modules

Returns all loaded modules.

Response:
[
    {
        "name": "Momentum Breakout",
        "type": "strategy",
        "description": "Buys on breakout above 20H with volume",
        "status": "running",
        "version": "1.0.0"
    },
    {
        "name": "Previous Day Breakout",
        "type": "strategy",
        "description": "Trades breakouts above yesterday's high",
        "status": "running",
        "version": "2.1.0"
    }
]

#### Get Module Details

GET /api/modules/{module_name}

Returns details for a specific module.

Response:
{
    "name": "Momentum Breakout",
    "type": "strategy",
    "version": "1.0.0",
    "author": "KJ",
    "description": "Buys when price breaks above 20-period high",
    "status": "running",
    "settings": {
        "period": 20,
        "volume_threshold": 1.5
    }
}

#### Run Module

POST /api/modules/{module_name}/run

Starts a module.

Response:
{
    "status": "success",
    "message": "Module 'Momentum Breakout' started successfully",
    "module": "Momentum Breakout"
}

#### Stop Module

POST /api/modules/{module_name}/stop

Stops a running module.

Response:
{
    "status": "success",
    "message": "Module 'Momentum Breakout' stopped",
    "module": "Momentum Breakout"
}

#### Pause Module

POST /api/modules/{module_name}/pause

Pauses a running module.

Response:
{
    "status": "success",
    "message": "Module 'Momentum Breakout' paused",
    "module": "Momentum Breakout"
}

#### Resume Module

POST /api/modules/{module_name}/resume

Resumes a paused module.

Response:
{
    "status": "success",
    "message": "Module 'Momentum Breakout' resumed",
    "module": "Momentum Breakout"
}

---

### 3. Orders

#### Place Order

POST /api/orders

Places a new order.

Request:
{
    "symbol": "NIFTY 50",
    "quantity": 10,
    "order_type": "BUY",
    "price": 22450,
    "type": "MARKET"
}

Response:
{
    "id": "ORD_20260115_123456",
    "symbol": "NIFTY 50",
    "quantity": 10,
    "order_type": "BUY",
    "price": 22450,
    "status": "executed",
    "timestamp": "2026-01-15T12:34:56"
}

#### Get Orders

GET /api/orders

Returns all orders.

Response:
[
    {
        "id": "ORD_20260115_123456",
        "symbol": "NIFTY 50",
        "quantity": 10,
        "order_type": "BUY",
        "price": 22450,
        "status": "executed",
        "timestamp": "2026-01-15T12:34:56"
    }
]

#### Get Order Status

GET /api/orders/{order_id}

Returns status of a specific order.

Response:
{
    "id": "ORD_20260115_123456",
    "status": "executed",
    "filled_quantity": 10,
    "price": 22450,
    "timestamp": "2026-01-15T12:34:56"
}

#### Cancel Order

DELETE /api/orders/{order_id}

Cancels a pending order.

Response:
{
    "status": "success",
    "message": "Order cancelled",
    "order_id": "ORD_20260115_123456"
}

---

### 4. Portfolio

#### Get Portfolio

GET /api/portfolio

Returns current portfolio status.

Response:
{
    "balance": 1000000,
    "equity": 1024500,
    "pnl": 24500,
    "positions": [
        {
            "symbol": "NIFTY 50",
            "quantity": 10,
            "average_price": 22450,
            "current_price": 22550,
            "pnl": 1000
        }
    ],
    "total_trades": 15,
    "win_rate": 65.5
}

#### Get Positions

GET /api/portfolio/positions

Returns all open positions.

Response:
[
    {
        "symbol": "NIFTY 50",
        "quantity": 10,
        "average_price": 22450,
        "current_price": 22550,
        "pnl": 1000,
        "entry_time": "2026-01-15T10:30:00"
    }
]

---

### 5. Backtest

#### Run Backtest

POST /api/backtest

Runs a backtest on a module.

Request:
{
    "module_name": "Momentum Breakout",
    "symbol": "NIFTY 50",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "initial_capital": 100000
}

Response:
{
    "module_name": "Momentum Breakout",
    "symbol": "NIFTY 50",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "total_trades": 45,
    "win_rate": 62.5,
    "profit_factor": 1.8,
    "total_pnl": 24500,
    "max_drawdown": 12.5,
    "return_percent": 24.5,
    "final_equity": 124500
}

#### Get Backtest Results

GET /api/backtest/{module_name}

Returns backtest results for a module.

Response:
{
    "module_name": "Momentum Breakout",
    "symbol": "NIFTY 50",
    "total_trades": 45,
    "win_rate": 62.5,
    "profit_factor": 1.8,
    "total_pnl": 24500,
    "max_drawdown": 12.5,
    "return_percent": 24.5
}

---

### 6. Market Data

#### Get Current Price

GET /api/market/price/{symbol}

Returns current price for a symbol.

Response:
{
    "symbol": "NIFTY 50",
    "price": 22450.75,
    "change": 142.30,
    "change_percent": 0.64,
    "volume": 1250000,
    "high": 22500.00,
    "low": 22350.00,
    "open": 22308.45,
    "close": 22450.75
}

#### Get Historical Data

GET /api/market/historical/{symbol}

Returns historical data.

Query Parameters:
- period: 1d, 5d, 1mo, 3mo, 6mo, 1y
- interval: 1m, 5m, 15m, 30m, 1h, 1d

Response:
[
    {
        "time": 1705305600,
        "open": 22300,
        "high": 22450,
        "low": 22250,
        "close": 22450,
        "volume": 1000000
    }
]

---

### 7. Notifications

#### Send Notification

POST /api/notifications

Sends a notification.

Request:
{
    "channel": "telegram",
    "message": "BUY Signal for NIFTY 50 at 22450",
    "data": {
        "symbol": "NIFTY 50",
        "price": 22450,
        "signal": "BUY"
    }
}

Response:
{
    "status": "success",
    "message": "Notification sent",
    "notification_id": "NOTIF_20260115_123456"
}

#### Get Notifications

GET /api/notifications

Returns recent notifications.

Response:
[
    {
        "id": "NOTIF_20260115_123456",
        "channel": "telegram",
        "message": "BUY Signal for NIFTY 50 at 22450",
        "status": "sent",
        "timestamp": "2026-01-15T12:34:56"
    }
]

---

### 8. Watchlist

#### Get Watchlists

GET /api/watchlists

Returns all watchlists.

Response:
[
    {
        "id": 1,
        "name": "Nifty 50",
        "symbols": ["NIFTY 50", "BANKNIFTY", "RELIANCE", "TCS", "HDFC"]
    }
]

#### Create Watchlist

POST /api/watchlists

Creates a new watchlist.

Request:
{
    "name": "My Favorites",
    "symbols": ["NIFTY 50", "BANKNIFTY"]
}

Response:
{
    "status": "success",
    "id": 2,
    "name": "My Favorites",
    "symbols": ["NIFTY 50", "BANKNIFTY"]
}

---

## Error Responses

All errors return a standard format:

{
    "error": true,
    "message": "Error description",
    "code": "ERROR_CODE"
}

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |
