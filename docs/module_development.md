# KJs TRD Trading Terminal - Module Development Guide

## Overview

This guide explains how to create Python modules for the KJs TRD Trading Terminal platform.

## Module Types

| Type | Purpose | Output |
|------|---------|--------|
| Strategy | Trading logic | BUY/SELL/EXIT signals |
| Indicator | Technical analysis | Plots, values, signals |
| Screener | Stock scanning | List of matching symbols |
| Alert | Notifications | Alert messages |
| Automation | Automated actions | Orders, actions |

---

## Module Lifecycle

Create -> Save -> Validate -> Register -> Load -> Initialize -> Run -> Pause -> Resume -> Stop -> Unload -> Delete

---

## Standard Module Interface

### Required Attributes

class MyModule:
    name = "Module Name"          # Display name
    type = "strategy"             # Module type
    version = "1.0.0"             # Version number
    author = "Your Name"          # Author name
    description = "Description"   # What the module does

### Required Methods

#### initialize(self, context)

Called when the module is loaded.

def initialize(self, context):
    """
    Initialize the module.
    
    Args:
        context: dict containing platform data
    
    Returns:
        bool: True if successful
    """
    self.period = 20
    self.threshold = 1.5
    return True

#### on_candle(self, candle, context)

Called when a new candle is received.

def on_candle(self, candle, context):
    """
    Process a new candle.
    
    Args:
        candle: dict with 'open', 'high', 'low', 'close', 'volume'
        context: dict with 'candles', 'symbol', 'timeframe', 'position'
    
    Returns:
        tuple: (signal, data) or (None, None)
        signal: 'BUY', 'SELL', 'EXIT', or None
        data: dict with additional info
    """
    # Your logic here
    return None, None

#### on_tick(self, tick, context)

Called when a new tick is received (optional).

def on_tick(self, tick, context):
    """
    Process a new tick.
    
    Args:
        tick: dict with price and volume data
        context: dict with platform data
    """
    pass

#### on_stop(self)

Called when the module stops (optional).

def on_stop(self):
    """Cleanup when module stops."""
    return True

---

## Example: Strategy Module

### Momentum Breakout Strategy

class MomentumBreakout:
    """Buys when price breaks above 20-period high with volume."""

    name = "Momentum Breakout"
    type = "strategy"
    version = "1.0.0"
    author = "KJ"
    description = "Buys on breakout above 20H with volume"

    def __init__(self):
        self.period = 20
        self.volume_threshold = 1.5

    def initialize(self, context):
        return True

    def on_candle(self, candle, context):
        candles = context.get('candles', [])
        if len(candles) < self.period:
            return None, None

        # Calculate 20-period high
        high_20 = max(c['high'] for c in candles[-self.period:])

        # Calculate average volume
        avg_volume = sum(c['volume'] for c in candles[-self.period:]) / self.period

        # Check breakout
        if candle['close'] > high_20:
            if candle['volume'] > avg_volume * self.volume_threshold:
                return 'BUY', {
                    'reason': f'Breakout above {self.period}H with volume',
                    'price': candle['close'],
                    'high': high_20
                }

        return None, None

    def on_stop(self):
        return True

---

## Example: Indicator Module

### EMA Indicator

class EMA:
    """Exponential Moving Average indicator."""

    name = "EMA"
    type = "indicator"
    version = "1.0.0"
    author = "KJ"
    description = "Exponential Moving Average"

    def __init__(self):
        self.period = 20
        self.values = []

    def initialize(self, context):
        return True

    def calculate(self, candles):
        """Calculate EMA values."""
        if len(candles) < self.period:
            return []

        ema = []
        multiplier = 2 / (self.period + 1)

        for i in range(len(candles)):
            if i < self.period - 1:
                ema.append(None)
                continue

            if i == self.period - 1:
                sum_close = sum(c['close'] for c in candles[:self.period])
                ema.append(sum_close / self.period)
            else:
                prev_ema = ema[i - 1]
                close = candles[i]['close']
                ema.append((close - prev_ema) * multiplier + prev_ema)

        return ema

    def on_candle(self, candle, context):
        candles = context.get('candles', [])
        if len(candles) < self.period:
            return None

        values = self.calculate(candles)
        if values:
            self.values = values
            return {'ema': values[-1]}

        return None

---

## Example: Screener Module

### Momentum Scanner

class MomentumScanner:
    """Scans for momentum stocks."""

    name = "Momentum Scanner"
    type = "screener"
    version = "1.0.0"
    author = "KJ"
    description = "Scans for momentum stocks"

    def __init__(self):
        self.period = 20
        self.min_change = 5

    def initialize(self, context):
        return True

    def scan(self, watchlist, market_data):
        """Scan watchlist for momentum stocks."""
        results = []

        for symbol in watchlist:
            candles = market_data.get_candles(symbol, count=self.period)
            if not candles:
                continue

            # Calculate price change
            start_price = candles[0]['close']
            current_price = candles[-1]['close']
            change = ((current_price - start_price) / start_price) * 100

            if change > self.min_change:
                results.append({
                    'symbol': symbol,
                    'price': current_price,
                    'change': round(change, 2)
                })

        # Sort by change (highest first)
        results.sort(key=lambda x: x['change'], reverse=True)
        return results

    def on_candle(self, candle, context):
        """Scanner doesn't process individual candles."""
        return None

---

## Example: Alert Module

### VWAP Alert

class VWAPAlert:
    """Alerts when price crosses VWAP."""

    name = "VWAP Alert"
    type = "alert"
    version = "1.0.0"
    author = "KJ"
    description = "Alerts when price crosses VWAP"

    def __init__(self):
        self.vwap = 0

    def initialize(self, context):
        return True

    def calculate_vwap(self, candles):
        """Calculate Volume Weighted Average Price."""
        total_volume = 0
        total_value = 0

        for candle in candles:
            typical_price = (candle['high'] + candle['low'] + candle['close']) / 3
            total_value += typical_price * candle['volume']
            total_volume += candle['volume']

        if total_volume == 0:
            return 0

        return round(total_value / total_volume, 2)

    def on_candle(self, candle, context):
        candles = context.get('candles', [])
        if len(candles) < 20:
            return None

        self.vwap = self.calculate_vwap(candles)
        current_price = candle['close']

        # Check if price crosses VWAP
        if current_price > self.vwap:
            return {
                'type': 'BULLISH',
                'message': f'Price crossed above VWAP at {current_price}',
                'price': current_price,
                'vwap': self.vwap
            }
        elif current_price < self.vwap:
            return {
                'type': 'BEARISH',
                'message': f'Price crossed below VWAP at {current_price}',
                'price': current_price,
                'vwap': self.vwap
            }

        return None

---

## Best Practices

### 1. Keep It Simple
- Focus on trading logic
- Let the platform handle infrastructure

### 2. Use Context
- Access market data through context
- Don't fetch data directly

### 3. Handle Errors
- Use try/except blocks
- Return meaningful error messages

### 4. Document Your Code
- Add docstrings
- Explain your logic

### 5. Test Your Module
- Test with sample data
- Verify signals are correct

### 6. Use Settings
- Make parameters configurable
- Use get_settings() and update_settings()

### 7. Clean Up
- Use on_stop() for cleanup
- Close connections if opened

---

## Module Settings

### Define Settings

def get_settings(self):
    """Return module settings."""
    return {
        'period': self.period,
        'threshold': self.threshold
    }

def update_settings(self, settings):
    """Update module settings."""
    if 'period' in settings:
        self.period = settings['period']
    if 'threshold' in settings:
        self.threshold = settings['threshold']
    return True

---

## Testing Your Module

### Test Template

def test_my_module():
    """Test the module."""
    module = MyModule()
    module.initialize({})

    # Create test candles
    candles = []
    for i in range(30):
        candles.append({
            'close': 100 + i,
            'high': 101 + i,
            'low': 99 + i,
            'volume': 1000000
        })

    context = {'candles': candles}

    # Test on_candle
    signal, data = module.on_candle(candles[-1], context)

    if signal:
        print(f"Signal: {signal}")
        print(f"Data: {data}")
    else:
        print("No signal")

    return True

---

## File Location

Modules must be placed in the correct directory:

modules/
├── strategies/       # Strategy modules
├── indicators/       # Indicator modules
├── screeners/        # Screener modules
└── alerts/           # Alert modules

---

## Module Discovery

The platform automatically discovers modules in these directories:

1. Scans all .py files
2. Looks for classes with name and type attributes
3. Loads valid modules
4. Registers them in Module Library

---

## Common Errors

| Error | Solution |
|-------|----------|
| Module not found | Check file location and name |
| No valid class | Add name and type attributes |
| Method missing | Implement required methods |
| Syntax error | Check Python syntax |

---

## Next Steps

1. Write your module
2. Save it in the correct directory
3. Open the platform
4. Find your module in Module Library
5. Click Run to start
6. Test and iterate

---

## Support

For questions or issues:
- Check the architecture documentation
- Review the API reference
- Test with sample data
