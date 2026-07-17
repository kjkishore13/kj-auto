# ============================================================
# KJs TRD Trading Terminal - Execution Engine
# ============================================================

from datetime import datetime
import json
import uuid

class ExecutionEngine:
    """Executes trades based on signals from modules."""

    def __init__(self):
        self.mode = 'paper'  # paper, backtest, auto, replay, simulation
        self.positions = {}
        self.orders = []
        self.trades = []
        self.portfolio = {
            'balance': 1000000,
            'equity': 1000000,
            'pnl': 0,
            'positions': {}
        }
        self.event_engine = None
        self.runtime_engine = None
        self._log("INFO", "Execution Engine initialized")

    def initialize(self, event_engine=None, runtime_engine=None):
        """Initialize the execution engine."""
        self.event_engine = event_engine
        self.runtime_engine = runtime_engine
        self._log("INFO", f"Execution Engine initialized (mode: {self.mode})")
        return True

    def set_mode(self, mode):
        """Set execution mode."""
        valid_modes = ['paper', 'backtest', 'auto', 'replay', 'simulation']
        if mode in valid_modes:
            self.mode = mode
            self._log("INFO", f"Execution mode set to: {mode}")
            return True
        return False

    def execute_signal(self, signal_data):
        """Execute a trading signal."""
        module_name = signal_data.get('module_name')
        signal = signal_data.get('signal')
        price = signal_data.get('price', 0)
        data = signal_data.get('data', {})

        self._log("INFO", f"Processing signal: {signal} from {module_name} at {price}")

        if signal == 'BUY':
            return self._execute_buy(module_name, price, data)
        elif signal == 'SELL':
            return self._execute_sell(module_name, price, data)
        elif signal == 'EXIT':
            return self._execute_exit(module_name, price, data)
        else:
            self._log("WARNING", f"Unknown signal type: {signal}")
            return None

    def _execute_buy(self, module_name, price, data):
        """Execute a BUY signal."""
        quantity = self._calculate_quantity(price)

        if quantity <= 0:
            self._log("WARNING", f"Invalid quantity for BUY: {quantity}")
            return None

        order = {
            'id': self._generate_order_id(),
            'module': module_name,
            'type': 'BUY',
            'price': price,
            'quantity': quantity,
            'status': 'executed' if self.mode != 'auto' else 'pending',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        self.orders.append(order)

        if self.mode == 'paper':
            return self._execute_paper_order(order)
        elif self.mode == 'auto':
            return self._execute_auto_order(order)
        elif self.mode == 'backtest':
            return self._execute_backtest_order(order)
        else:
            return order

    def _execute_sell(self, module_name, price, data):
        """Execute a SELL signal."""
        position = None
        for pos in self.positions.values():
            if pos.get('module') == module_name and pos.get('status') == 'open':
                position = pos
                break

        if not position:
            self._log("WARNING", f"No open position found for {module_name}")
            return None

        order = {
            'id': self._generate_order_id(),
            'module': module_name,
            'type': 'SELL',
            'price': price,
            'quantity': position.get('quantity', 0),
            'status': 'executed',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        self.orders.append(order)

        entry_price = position.get('entry_price', price)
        pnl = (price - entry_price) * position.get('quantity', 0)

        position['status'] = 'closed'
        position['exit_price'] = price
        position['pnl'] = pnl
        position['exit_time'] = datetime.now().isoformat()

        self.portfolio['balance'] += pnl
        self.portfolio['equity'] = self.portfolio['balance']
        self.portfolio['pnl'] += pnl

        trade = {
            'id': self._generate_trade_id(),
            'module': module_name,
            'type': 'SELL',
            'entry_price': entry_price,
            'exit_price': price,
            'quantity': position.get('quantity', 0),
            'pnl': pnl,
            'timestamp': datetime.now().isoformat()
        }
        self.trades.append(trade)

        self._log("INFO", f"Closed position: {module_name} PnL: {pnl:.2f}")

        if self.event_engine:
            self.event_engine.publish('TRADE_CLOSED', {
                'module_name': module_name,
                'pnl': pnl,
                'price': price,
                'quantity': position.get('quantity', 0),
                'timestamp': datetime.now().isoformat()
            })

        return order

    def _execute_exit(self, module_name, price, data):
        """Execute an EXIT signal (close all positions)."""
        results = []
        for pos in list(self.positions.values()):
            if pos.get('module') == module_name and pos.get('status') == 'open':
                result = self._execute_sell(module_name, price, data)
                if result:
                    results.append(result)
        return results

    def _execute_paper_order(self, order):
        """Execute a paper trading order."""
        if order['type'] == 'BUY':
            position = {
                'module': order['module'],
                'entry_price': order['price'],
                'quantity': order['quantity'],
                'status': 'open',
                'entry_time': order['timestamp'],
                'data': order.get('data', {})
            }
            self.positions[order['id']] = position

            self.portfolio['equity'] -= order['price'] * order['quantity']

            self._log("INFO", f"Paper BUY: {order['quantity']} @ {order['price']}")

            if self.event_engine:
                self.event_engine.publish('PAPER_TRADE_OPENED', {
                    'module': order['module'],
                    'price': order['price'],
                    'quantity': order['quantity'],
                    'timestamp': order['timestamp']
                })

        return order

    def _execute_auto_order(self, order):
        """Execute an auto trading order (real broker)."""
        self._log("INFO", f"Auto order placed: {order['type']} {order['quantity']} @ {order['price']}")

        if self.event_engine:
            self.event_engine.publish('AUTO_ORDER_PLACED', {
                'order': order,
                'timestamp': datetime.now().isoformat()
            })

        return order

    def _execute_backtest_order(self, order):
        """Execute a backtest order."""
        if order['type'] == 'BUY':
            position = {
                'module': order['module'],
                'entry_price': order['price'],
                'quantity': order['quantity'],
                'status': 'open',
                'entry_time': order['timestamp'],
                'data': order.get('data', {})
            }
            self.positions[order['id']] = position

        return order

    def _calculate_quantity(self, price):
        """Calculate position size based on risk."""
        risk_per_trade = 0.02
        risk_amount = self.portfolio['balance'] * risk_per_trade

        quantity = int(risk_amount / price / 10) * 10

        return max(10, min(quantity, 1000))

    def _generate_order_id(self):
        """Generate a unique order ID."""
        return f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.orders)}"

    def _generate_trade_id(self):
        """Generate a unique trade ID."""
        return f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.trades)}"

    def get_portfolio(self):
        """Get current portfolio status."""
        return self.portfolio

    def get_positions(self):
        """Get all open positions."""
        return {k: v for k, v in self.positions.items() if v.get('status') == 'open'}

    def get_trades(self):
        """Get all trades."""
        return self.trades

    def get_orders(self):
        """Get all orders."""
        return self.orders

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Execution] [{level}] {message}")
