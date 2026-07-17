# KJs TRD Trading Terminal - Architecture Documentation

## Overview

KJs TRD Trading Terminal is a **Personal Trading Operating System** built as a modular platform. The platform itself remains stable while users extend it through Python Modules.

## Core Philosophy

- **Build Once, Extend Forever** - Platform code never changes; users add Python Modules
- **Everything is a Module** - Strategies, Indicators, Screeners, Alerts, Automation
- **Python-First** - Users write only Python; platform handles infrastructure
- **Event-Driven** - Loose coupling through Event Engine
- **One Source of Truth** - One module works for all modes (Live, Backtest, Paper, Auto)

## Architecture Layers

## Core Components

### 1. Runtime Engine (`backend/core/runtime_engine.py`)
- **Purpose**: Executes Python Modules
- **Responsibilities**:
  - Load and initialize modules
  - Start/Stop/Pause/Resume modules
  - Process candles through modules
  - Handle module exceptions
  - Publish events to Event Engine

### 2. Module Manager (`backend/core/module_manager.py`)
- **Purpose**: Manages all Python Modules
- **Responsibilities**:
  - Discover modules in `modules/` directory
  - Load/Unload modules
  - Track module metadata
  - Create/Delete modules
  - Manage module versions

### 3. Event Engine (`backend/core/event_engine.py`)
- **Purpose**: Communication hub
- **Responsibilities**:
  - Publish/subscribe system
  - Distribute events to subscribers
  - Decouple components
  - Async event processing

### 4. Market Data Engine (`backend/core/market_data_engine.py`)
- **Purpose**: Fetches and distributes market data
- **Responsibilities**:
  - Connect to data providers (Yahoo, Alpha Vantage, Dhan)
  - Fetch historical and live data
  - Cache data
  - Publish market data events

### 5. Execution Engine (`backend/engines/execution_engine.py`)
- **Purpose**: Executes trading signals
- **Modes**: Backtest, Paper Trading, Automation, Replay, Simulation
- **Responsibilities**:
  - Process BUY/SELL/EXIT signals
  - Manage positions
  - Track portfolio
  - Calculate PnL

### 6. Backtest Engine (`backend/engines/backtest_engine.py`)
- **Purpose**: Runs strategies on historical data
- **Responsibilities**:
  - Simulate trading on historical data
  - Calculate metrics (Win Rate, Profit Factor, Drawdown)
  - Generate equity curve
  - Export results

### 7. Paper Trading Engine (`backend/engines/paper_trading_engine.py`)
- **Purpose**: Simulates trading with virtual money
- **Responsibilities**:
  - Execute virtual orders
  - Track virtual positions
  - Track PnL
  - Manage virtual portfolio

### 8. Auto Trading Engine (`backend/engines/auto_trading_engine.py`)
- **Purpose**: Executes real trades through brokers
- **Responsibilities**:
  - Connect to broker APIs
  - Place real orders
  - Risk management
  - Track positions and trades

### 9. Notification Engine (`backend/engines/notification_engine.py`)
- **Purpose**: Sends alerts through multiple channels
- **Channels**: Telegram, WhatsApp, Email, Push
- **Responsibilities**:
  - Send signal alerts
  - Send system status updates
  - Manage notification preferences

### 10. Broker Integration (`backend/brokers/`)
- **Purpose**: Standard interface to multiple brokers
- **Supported**: Dhan, Zerodha, Angel One
- **Responsibilities**:
  - Authentication
  - Order placement
  - Portfolio management
  - Position tracking

## Module System

### Module Lifecycle

### Standard Module Interface

```python
class Module:
    name = "Module Name"
    type = "strategy"  # or "indicator", "screener", "alert", "automation"
    version = "1.0.0"
    author = "Author"
    description = "Description"

    def initialize(self, context):
        """Initialize the module."""
        pass

    def on_candle(self, candle, context):
        """Called when a new candle is received."""
        return signal, data  # signal: 'BUY', 'SELL', 'EXIT', None

    def on_tick(self, tick, context):
        """Called when a new tick is received."""
        pass

    def on_stop(self):
        """Called when the module stops."""
        pass1. Market Data Engine → New Candle
2. Runtime Engine → on_candle() on all running modules
3. Module → Returns signal (BUY/SELL/EXIT)
4. Runtime Engine → Publishes SIGNAL_GENERATED event
5. Event Engine → Distributes event to subscribers
6. Chart Engine → Draws signal on chart
7. Execution Engine → Executes trade based on mode
8. Notification Engine → Sends alert
9. Database → Stores trade record
