# ============================================================
# KJs TRD Trading Terminal - VWAP Alert
# ============================================================

class VWAPAlert:
    """VWAP Alert Module"""

    name = "VWAP Alert"
    type = "alert"
    version = "1.0.0"
    author = "KJ"
    description = "Alerts when price crosses VWAP"

    def __init__(self):
        self.vwap = 0
        self.previous_vwap = 0
        self.cross_detected = False
        self.last_alert_time = None

    def initialize(self, context):
        """Initialize the alert"""
        print(f"✅ {self.name} initialized")
        return True

    def calculate_vwap(self, candles):
        """Calculate VWAP (Volume Weighted Average Price)"""
        if len(candles) < 1:
            return 0

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
        """Called when a new candle is received."""
        candles = context.get('candles', [])

        if len(candles) < 20:
            return None

        self.previous_vwap = self.vwap
        self.vwap = self.calculate_vwap(candles)

        current_price = candle['close']
        alert = None

        if self.previous_vwap > 0:
            if current_price > self.vwap and self.previous_vwap <= self.previous_vwap:
                alert = {
                    'type': 'BULLISH',
                    'message': f'Price crossed ABOVE VWAP at {current_price}',
                    'price': current_price,
                    'vwap': self.vwap,
                    'cross': 'above'
                }

            elif current_price < self.vwap and self.previous_vwap >= self.previous_vwap:
                alert = {
                    'type': 'BEARISH',
                    'message': f'Price crossed BELOW VWAP at {current_price}',
                    'price': current_price,
                    'vwap': self.vwap,
                    'cross': 'below'
                }

        if self.vwap > 0:
            deviation = ((current_price - self.vwap) / self.vwap) * 100

            if deviation > 3:
                alert = {
                    'type': 'EXTENDED',
                    'message': f'Price is {round(deviation, 2)}% ABOVE VWAP at {current_price}',
                    'price': current_price,
                    'vwap': self.vwap,
                    'deviation': round(deviation, 2)
                }
            elif deviation < -3:
                alert = {
                    'type': 'EXTENDED',
                    'message': f'Price is {abs(round(deviation, 2))}% BELOW VWAP at {current_price}',
                    'price': current_price,
                    'vwap': self.vwap,
                    'deviation': round(deviation, 2)
                }

        if alert:
            self.last_alert_time = candle.get('time')
            return alert

        return None

    def get_vwap(self):
        """Get current VWAP value"""
        return self.vwap

    def get_status(self):
        """Get alert status"""
        return {
            'vwap': self.vwap,
            'last_alert_time': self.last_alert_time,
            'is_active': True
        }

    def on_stop(self):
        """Called when alert stops"""
        print(f"🛑 {self.name} stopped")
        return True

    def get_settings(self):
        """Return alert settings"""
        return {
            'name': self.name,
            'version': self.version
        }

    def update_settings(self, settings):
        """Update alert settings"""
        return True
