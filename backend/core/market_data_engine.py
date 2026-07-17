# ============================================================
# KJs TRD Trading Terminal - Market Data Engine
# ============================================================

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import threading
import random

class MarketDataEngine:
    """Fetches and distributes market data to the platform."""

    def __init__(self):
        self.subscribers = []
        self.cache = {}
        self.running = False
        self.thread = None
        self.symbols = ['NIFTY 50', 'BANKNIFTY']
        self.current_data = {}
        self.event_engine = None
        self._log("INFO", "Market Data Engine initialized")

    def initialize(self, event_engine=None):
        """Initialize the market data engine."""
        self.event_engine = event_engine
        self._log("INFO", "Market Data Engine initialized with dependencies")
        return True

    def start(self):
        """Start the market data engine."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._fetch_loop, daemon=True)
        self.thread.start()
        self._log("INFO", "Market Data Engine started")

    def stop(self):
        """Stop the market data engine."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self._log("INFO", "Market Data Engine stopped")

    def subscribe(self, symbol, callback):
        """Subscribe to market data for a symbol."""
        if symbol not in self.current_data:
            self.current_data[symbol] = {
                'price': 0,
                'change': 0,
                'change_percent': 0,
                'volume': 0,
                'high': 0,
                'low': 0,
                'open': 0,
                'close': 0,
                'candles': []
            }
        self.subscribers.append((symbol, callback))
        self._log("INFO", f"Subscribed to {symbol}")

    def get_price(self, symbol):
        """Get current price for a symbol."""
        if symbol in self.current_data:
            return self.current_data[symbol].get('price', 0)
        return 0

    def get_historical(self, symbol, period='5d', interval='15m'):
        """Get historical data for a symbol."""
        cache_key = f"{symbol}_{period}_{interval}"

        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < 60:
                return data

        try:
            # Try Yahoo Finance first
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)

            if not data.empty:
                self.cache[cache_key] = (datetime.now(), data)
                return data
        except Exception as e:
            self._log("WARNING", f"Yahoo Finance failed for {symbol}: {str(e)}")

        # Fallback: Generate mock data
        return self._generate_mock_historical(count=100)

    def get_candles(self, symbol, count=200, interval='15m'):
        """Get recent candles for a symbol."""
        data = self.get_historical(symbol, period='5d', interval=interval)

        if data is not None and not data.empty:
            candles = []
            for idx, row in data.tail(count).iterrows():
                candles.append({
                    'time': int(idx.timestamp()),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume'])
                })
            return candles

        return self._generate_mock_candles(count)

    def _generate_mock_candles(self, count=200):
        """Generate mock candle data for testing."""
        candles = []
        price = 22400
        now = datetime.now()
        one_hour = 60 * 60

        for i in range(count - 1, -1, -1):
            change = (random.random() - 0.48) * 60
            open_price = price
            close_price = price + change
            high = max(open_price, close_price) + random.random() * 20
            low = min(open_price, close_price) - random.random() * 20
            volume = int(100000 + random.random() * 900000)

            candles.append({
                'time': int((now - timedelta(seconds=i * one_hour)).timestamp()),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': volume
            })

            price = close_price

        return candles

    def _generate_mock_historical(self, count=100):
        """Generate mock historical data."""
        data = []
        price = 22400
        now = datetime.now()

        for i in range(count - 1, -1, -1):
            change = (random.random() - 0.48) * 60
            open_price = price
            close_price = price + change
            high = max(open_price, close_price) + random.random() * 20
            low = min(open_price, close_price) - random.random() * 20

            data.append({
                'Open': round(open_price, 2),
                'High': round(high, 2),
                'Low': round(low, 2),
                'Close': round(close_price, 2),
                'Volume': int(100000 + random.random() * 900000)
            })

            price = close_price

        df = pd.DataFrame(data)
        df.index = pd.date_range(end=now, periods=count, freq='15min')
        return df

    def _fetch_loop(self):
        """Main fetch loop for market data."""
        while self.running:
            try:
                for symbol, callback in self.subscribers:
                    self._update_symbol_data(symbol)
                    if callback:
                        callback(symbol, self.current_data.get(symbol, {}))

                if self.event_engine:
                    self.event_engine.publish('MARKET_DATA_UPDATED', {
                        'symbols': list(self.current_data.keys()),
                        'data': self.current_data,
                        'timestamp': datetime.now().isoformat()
                    })

                time.sleep(5)

            except Exception as e:
                self._log("ERROR", f"Error in fetch loop: {str(e)}")
                time.sleep(5)

    def _update_symbol_data(self, symbol):
        """Update data for a specific symbol."""
        try:
            data = self.get_historical(symbol, period='1d', interval='1m')

            if data is not None and not data.empty:
                latest = data.iloc[-1]
                first = data.iloc[0]

                current = self.current_data.get(symbol, {})
                current['price'] = round(latest['Close'], 2)
                current['open'] = round(first['Open'], 2)
                current['high'] = round(data['High'].max(), 2)
                current['low'] = round(data['Low'].min(), 2)
                current['close'] = round(latest['Close'], 2)
                current['volume'] = int(latest['Volume'])
                current['change'] = round(latest['Close'] - first['Open'], 2)
                current['change_percent'] = round(
                    ((latest['Close'] - first['Open']) / first['Open']) * 100, 2
                )

                self.current_data[symbol] = current
            else:
                self._update_mock_data(symbol)

        except Exception as e:
            self._log("ERROR", f"Failed to update data for {symbol}: {str(e)}")
            self._update_mock_data(symbol)

    def _update_mock_data(self, symbol):
        """Update with mock data."""
        current = self.current_data.get(symbol, {})
        change = (random.random() - 0.48) * 20
        base_price = 22400 if 'NIFTY' in symbol else 48200

        current['price'] = round(base_price + change, 2)
        current['change'] = round(change, 2)
        current['change_percent'] = round((change / base_price) * 100, 2)
        current['volume'] = int(100000 + random.random() * 900000)
        current['high'] = round(current['price'] + random.random() * 15, 2)
        current['low'] = round(current['price'] - random.random() * 15, 2)
        current['open'] = round(current['price'] - random.random() * 10, 2)
        current['close'] = current['price']

        self.current_data[symbol] = current

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [MarketData] [{level}] {message}")
