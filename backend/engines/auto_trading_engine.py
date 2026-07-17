# ============================================================
# KJs TRD Trading Terminal - Auto Trading Engine
# ============================================================

from datetime import datetime
import json
import uuid

class AutoTradingEngine:
    """Executes real trades through broker integration."""

    def __init__(self):
        self.running = False
        self.orders = []
        self.trades = []
        self.positions = {}
        self.risk_limits = {
            'max_position_size': 100000,
            'max_daily_loss': 50000,
            'max_positions': 5,
            'max_risk_per_trade': 0.02
        }
        self.daily_pnl = 0
        self.event_engine = None
        self.broker_interface = None
        self._log("INFO", "Auto Trading Engine initialized")

    def initialize(self, event_engine=None, broker_interface=None):
        """Initialize the auto trading engine."""
        self.event_engine = event_engine
        self.broker_interface = broker_interface
        self._log("INFO", "Auto Trading Engine initialized with dependencies")
        return True

    def start(self):
        """Start auto trading."""
        if not self.broker_interface:
            self._log("ERROR", "Broker interface not initialized")
            return False

        self.running = True
        self._log("INFO", "Auto Trading Engine started")
        return True

    def stop(self):
        """Stop auto trading."""
        self.running = False
        self._log("INFO", "Auto Trading Engine stopped")

    def execute_signal(self, signal_data):
        """Execute a trading signal with real broker."""
        if not self.running:
            self._log("WARNING", "Auto trading is not running")
            return None

        if not self.broker_interface or not self.broker_interface.is_connected():
            self._log("ERROR", "Broker not connected")
            return None

        signal = signal_data.get('signal')
        symbol = signal_data.get('symbol', 'NIFTY 50')
        price = signal_data.get('price', 0)
        quantity = signal_data.get('quantity', 0)

        if not signal or price <= 0 or quantity <= 0:
            self._log("ERROR", "Invalid signal parameters")
            return None

        if not self._check_risk_limits(signal_data):
            self._log("WARNING", "Risk limit exceeded")
            return None

        try:
            if signal == 'BUY':
                order = self._place_buy_order(signal_data)
            elif signal == 'SELL':
                order = self._place_sell_order(signal_data)
            elif signal == 'EXIT':
                order = self._place_exit_order(signal_data)
            else:
                self._log("ERROR", f"Unknown signal type: {signal}")
                return None

            if order:
                self.orders.append(order)

                if self.event_engine:
                    self.event_engine.publish('AUTO_ORDER_EXECUTED', {
                        'order': order,
                        'signal': signal_data,
                        'timestamp': datetime.now().isoformat()
                    })

                self._log("INFO", f"Auto order executed: {signal} {quantity} {symbol} @ {price}")
                return order

        except Exception as e:
            self._log("ERROR", f"Error executing auto trade: {str(e)}")
            return None

        return None

    def _place_buy_order(self, signal_data):
        """Place a BUY order through broker."""
        symbol = signal_data.get('symbol', 'NIFTY 50')
        quantity = signal_data.get('quantity', 0)
        price = signal_data.get('price', 0)

        order = self.broker_interface.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type='BUY',
            price=price
        )

        if order and order.get('status') == 'executed':
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'symbol': symbol,
                    'quantity': 0,
                    'average_price': 0,
                    'total_cost': 0,
                    'entry_time': datetime.now().isoformat()
                }

            pos = self.positions[symbol]
            total_quantity = pos['quantity'] + quantity
            total_cost = pos['total_cost'] + (price * quantity)
            pos['quantity'] = total_quantity
            pos['average_price'] = total_cost / total_quantity if total_quantity > 0 else 0
            pos['total_cost'] = total_cost

        return order

    def _place_sell_order(self, signal_data):
        """Place a SELL order through broker."""
        symbol = signal_data.get('symbol', 'NIFTY 50')
        quantity = signal_data.get('quantity', 0)
        price = signal_data.get('price', 0)

        order = self.broker_interface.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type='SELL',
            price=price
        )

        if order and order.get('status') == 'executed':
            if symbol in self.positions:
                pos = self.positions[symbol]
                avg_price = pos['average_price']
                pnl = (price - avg_price) * quantity
                self.daily_pnl += pnl

                pos['quantity'] -= quantity
                pos['total_cost'] -= avg_price * quantity

                if pos['quantity'] <= 0:
                    del self.positions[symbol]

                trade = {
                    'id': self._generate_trade_id(),
                    'symbol': symbol,
                    'type': 'SELL',
                    'price': price,
                    'quantity': quantity,
                    'pnl': pnl,
                    'timestamp': datetime.now().isoformat()
                }
                self.trades.append(trade)

        return order

    def _place_exit_order(self, signal_data):
        """Place an EXIT order (close all positions for symbol)."""
        symbol = signal_data.get('symbol', 'NIFTY 50')

        if symbol not in self.positions:
            self._log("WARNING", f"No position found for {symbol}")
            return None

        pos = self.positions[symbol]
        exit_data = signal_data.copy()
        exit_data['quantity'] = pos['quantity']
        exit_data['signal'] = 'SELL'

        return self._place_sell_order(exit_data)

    def _check_risk_limits(self, signal_data):
        """Check if signal exceeds risk limits."""
        symbol = signal_data.get('symbol', 'NIFTY 50')
        price = signal_data.get('price', 0)
        quantity = signal_data.get('quantity', 0)

        position_value = price * quantity
        if position_value > self.risk_limits['max_position_size']:
            self._log("WARNING", f"Position value {position_value} exceeds max")
            return False

        if len(self.positions) >= self.risk_limits['max_positions']:
            self._log("WARNING", "Max positions reached")
            return False

        if self.daily_pnl < -self.risk_limits['max_daily_loss']:
            self._log("WARNING", "Max daily loss exceeded")
            return False

        return True

    def get_positions(self):
        """Get all open positions."""
        return self.positions

    def get_trades(self):
        """Get all trades."""
        return self.trades

    def get_orders(self):
        """Get all orders."""
        return self.orders

    def get_daily_pnl(self):
        """Get today's PnL."""
        return self.daily_pnl

    def _generate_trade_id(self):
        """Generate a unique trade ID."""
        return f"AUTO_TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [AutoTrading] [{level}] {message}")
