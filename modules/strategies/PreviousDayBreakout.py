# ============================================================
# KJs TRD Trading Terminal - Previous Day Breakout Strategy
# ============================================================

class PreviousDayBreakout:
    """Previous Day Breakout Strategy Module"""

    name = "Previous Day Breakout"
    type = "strategy"
    version = "2.1.0"
    author = "KJ"
    description = "Trades breakouts above yesterday's high"

    def __init__(self):
        self.lookback_days = 1
        self.entry_multiplier = 1.0
        self.stop_loss_multiplier = 0.005
        self.target_multiplier = 0.02
        self.position = None
        self.entry_price = None
        self.stop_loss = None
        self.target = None
        self.daily_high = None
        self.daily_low = None

    def initialize(self, context):
        """Initialize the strategy"""
        print(f"✅ {self.name} initialized")
        print(f"📊 Lookback Days: {self.lookback_days}")
        return True

    def on_candle(self, candle, context):
        """Called when a new candle is received."""
        candles = context.get('candles', [])

        if len(candles) < 2:
            return None, None

        yesterday = candles[-2]
        yesterday_high = yesterday['high']
        yesterday_low = yesterday['low']
        yesterday_close = yesterday['close']

        self.daily_high = yesterday_high
        self.daily_low = yesterday_low

        current_price = candle['close']

        if current_price > yesterday_high * self.entry_multiplier:
            if self.position is None:
                entry_price = current_price
                stop_loss = entry_price * (1 - self.stop_loss_multiplier)
                target = entry_price * (1 + self.target_multiplier)

                self.position = 'long'
                self.entry_price = entry_price
                self.stop_loss = stop_loss
                self.target = target

                return 'BUY', {
                    'reason': f'Breakout above yesterday\'s high at {yesterday_high}',
                    'price': entry_price,
                    'stop_loss': stop_loss,
                    'target': target,
                    'yesterday_high': yesterday_high,
                    'yesterday_low': yesterday_low
                }

        if self.position == 'long':
            if candle['low'] <= self.stop_loss:
                exit_price = self.stop_loss
                self.position = None
                return 'EXIT', {
                    'reason': 'Stop loss hit',
                    'price': exit_price,
                    'exit_type': 'stop_loss'
                }

            if candle['high'] >= self.target:
                exit_price = self.target
                self.position = None
                return 'EXIT', {
                    'reason': 'Target hit',
                    'price': exit_price,
                    'exit_type': 'target'
                }

            if current_price > self.entry_price * 1.01:
                new_stop = current_price * (1 - self.stop_loss_multiplier)
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop

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
            'lookback_days': self.lookback_days,
            'entry_multiplier': self.entry_multiplier,
            'stop_loss_multiplier': self.stop_loss_multiplier,
            'target_multiplier': self.target_multiplier
        }

    def update_settings(self, settings):
        """Update strategy settings"""
        if 'lookback_days' in settings:
            self.lookback_days = settings['lookback_days']
        if 'entry_multiplier' in settings:
            self.entry_multiplier = settings['entry_multiplier']
        if 'stop_loss_multiplier' in settings:
            self.stop_loss_multiplier = settings['stop_loss_multiplier']
        if 'target_multiplier' in settings:
            self.target_multiplier = settings['target_multiplier']
        return True
