# ============================================================
# KJs TRD Trading Terminal - RSI Indicator
# ============================================================

class RSI:
    """RSI Indicator Module"""

    name = "RSI"
    type = "indicator"
    version = "1.0.0"
    author = "KJ"
    description = "Relative Strength Index for overbought/oversold conditions"

    def __init__(self):
        self.period = 14
        self.overbought = 70
        self.oversold = 30
        self.values = []

    def initialize(self, context):
        """Initialize the indicator"""
        print(f"✅ {self.name} initialized")
        print(f"📊 Period: {self.period}")
        print(f"📊 Overbought: {self.overbought}")
        print(f"📊 Oversold: {self.oversold}")
        return True

    def calculate(self, candles):
        """Calculate RSI for all candles."""
        if len(candles) < self.period + 1:
            return []

        rsi_values = []

        for i in range(self.period, len(candles)):
            gains = 0
            losses = 0

            for j in range(i - self.period + 1, i + 1):
                change = candles[j]['close'] - candles[j - 1]['close']
                if change >= 0:
                    gains += change
                else:
                    losses += abs(change)

            avg_gain = gains / self.period
            avg_loss = losses / self.period

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(round(rsi, 2))

        return rsi_values

    def on_candle(self, candle, context):
        """Called when a new candle is received."""
        candles = context.get('candles', [])

        if len(candles) < self.period + 1:
            return None

        rsi_values = self.calculate(candles)

        if rsi_values:
            current_rsi = rsi_values[-1]
            self.values.append(current_rsi)

            if len(self.values) > 100:
                self.values = self.values[-100:]

            result = {
                'rsi': current_rsi,
                'signal': self._get_signal(current_rsi)
            }

            return result

        return None

    def _get_signal(self, rsi):
        """Generate trading signal based on RSI"""
        if rsi >= self.overbought:
            return {'type': 'overbought', 'action': 'SELL'}
        elif rsi <= self.oversold:
            return {'type': 'oversold', 'action': 'BUY'}
        else:
            return {'type': 'neutral', 'action': 'HOLD'}

    def get_latest(self):
        """Get the latest RSI value"""
        return self.values[-1] if self.values else None

    def get_settings(self):
        """Return indicator settings"""
        return {
            'period': self.period,
            'overbought': self.overbought,
            'oversold': self.oversold
        }

    def update_settings(self, settings):
        """Update indicator settings"""
        if 'period' in settings:
            self.period = settings['period']
        if 'overbought' in settings:
            self.overbought = settings['overbought']
        if 'oversold' in settings:
            self.oversold = settings['oversold']
        return True
