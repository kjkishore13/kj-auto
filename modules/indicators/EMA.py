# ============================================================
# KJs TRD Trading Terminal - EMA Indicator
# ============================================================

class EMA:
    """EMA Indicator Module"""

    name = "EMA Ribbon"
    type = "indicator"
    version = "1.2.0"
    author = "KJ"
    description = "Multiple EMA lines for trend confirmation"

    def __init__(self):
        self.periods = [9, 20, 50, 200]
        self.colors = ['#eab308', '#3b82f6', '#8b5cf6', '#ef4444']
        self.values = {}

    def initialize(self, context):
        """Initialize the indicator"""
        print(f"✅ {self.name} initialized")
        print(f"📊 Periods: {self.periods}")
        return True

    def calculate(self, candles):
        """Calculate EMA for all periods"""
        result = {}

        for period in self.periods:
            ema_values = self._calculate_ema(candles, period)
            result[period] = ema_values

        return result

    def _calculate_ema(self, candles, period):
        """Calculate EMA for a single period"""
        if len(candles) < period:
            return []

        ema = []
        multiplier = 2 / (period + 1)

        for i in range(len(candles)):
            if i < period - 1:
                ema.append(None)
                continue

            if i == period - 1:
                sum_close = sum(c['close'] for c in candles[:period])
                ema.append(sum_close / period)
            else:
                prev_ema = ema[i - 1]
                close = candles[i]['close']
                ema.append((close - prev_ema) * multiplier + prev_ema)

        return ema

    def on_candle(self, candle, context):
        """Called when a new candle is received."""
        candles = context.get('candles', [])
        if len(candles) < max(self.periods):
            return None

        for period in self.periods:
            ema_values = self._calculate_ema(candles, period)
            if ema_values:
                self.values[period] = ema_values[-1]

        return self.values

    def get_latest(self):
        """Get latest EMA values"""
        return {period: values[-1] if values else None
                for period, values in self.values.items()}

    def get_settings(self):
        """Return indicator settings"""
        return {
            'periods': self.periods,
            'colors': self.colors
        }

    def update_settings(self, settings):
        """Update indicator settings"""
        if 'periods' in settings:
            self.periods = settings['periods']
        return True
