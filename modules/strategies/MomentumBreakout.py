# ============================================================
# KJs TRD Trading Terminal - Momentum Breakout Strategy
# ============================================================

class MomentumBreakout:
    """Momentum Breakout Strategy Module"""

    name = "Momentum Breakout"
    type = "strategy"
    version = "1.0.0"
    author = "KJ"
    description = "Buys when price breaks above 20-period high with volume confirmation"

    def __init__(self):
        self.period = 20
        self.volume_threshold = 1.5
        self.position = None
        self.entry_price = None
        self.stop_loss = None
        self.target = None

    def initialize(self, context):
        """Initialize the strategy"""
        print(f"✅ {self.name} initialized")
        print(f"📊 Period: {self.period}")
        print(f"📊 Volume Threshold: {self.volume_threshold}x")
        return True

    def on_candle(self, candle, context):
        """Called when a new candle is received."""
        candles = context.get('candles', [])
        if len(candles) < self.period:
            return None, None

        high_20 = max(c['high'] for c in candles[-self.period:])
        avg_volume = sum(c['volume'] for c in candles[-self.period:]) / self.period

        if candle['close'] > high_20:
            if candle['volume'] > avg_volume * self.volume_threshold:
                return 'BUY', {
                    'reason': f'Breakout above {self.period}H with volume',
                    'price': candle['close'],
                    'high': high_20,
                    'volume': candle['volume'],
                    'avg_volume': avg_volume
                }

        if self.position == 'long':
            if candle['low'] <= self.stop_loss:
                return 'EXIT', {
                    'reason': 'Stop loss hit',
                    'price': self.stop_loss,
                    'exit_type': 'stop_loss'
                }

            if candle['high'] >= self.target:
                return 'EXIT', {
                    'reason': 'Target hit',
                    'price': self.target,
                    'exit_type': 'target'
                }

        return None, None

    def on_tick(self, tick, context):
        """Called when a new tick is received."""
        pass

    def on_stop(self):
        """Called when strategy stops"""
        print(f"🛑 {self.name} stopped")
        return True

    def get_settings(self):
        """Return strategy settings"""
        return {
            'period': self.period,
            'volume_threshold': self.volume_threshold
        }

    def update_settings(self, settings):
        """Update strategy settings"""
        if 'period' in settings:
            self.period = settings['period']
        if 'volume_threshold' in settings:
            self.volume_threshold = settings['volume_threshold']
        return True
