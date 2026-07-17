# ============================================================
# KJs TRD Trading Terminal - Paper Trading Engine
# ============================================================

from datetime import datetime
import json
import uuid

class PaperTradingEngine:
    """Simulates trading with virtual money."""

    def __init__(self):
        self.portfolio = {
            'balance': 1000000,
            'equity': 1000000,
            'pnl': 0,
            'positions': {},
            'orders': [],
            'trades': [],
            'history': []
        }
        self.running = False
        self.event_engine = None
        self._log("INFO", "Paper Trading Engine initialized")

    def initialize(self, event_engine=None):
        """Initialize the paper trading engine."""
        self.event_engine = event_engine
        self._log("INFO", "Paper Trading Engine initialized with dependencies")
        return True

    def start(self):
        """Start paper trading."""
        self.running = True
        self._log("INFO", "Paper Trading Engine started")

    def stop(self):
        """Stop paper trading."""
        self.running = False
        self._log("INFO", "Paper Trading Engine stopped")

    def reset(self):
        """Reset the portfolio."""
        self.portfolio = {
            'balance': 1000000,
            'equity': 1000000,
            'pnl': 0,
            'positions': {},
            'orders': [],
            'trades': [],
            'history': []
        }
        self._log("INFO", "Paper Trading portfolio reset")

    def place_order(self, order_data):
        """Place a paper trade order."""
        if not self.running:
            self._log("WARNING", "Paper trading is not running")
            return None

        symbol = order_data.get('symbol', 'NIFTY 50')
        order_type = order_data.get('type', 'BUY')
        quantity = order_data.get('quantity', 0)
        price = order_data.get('price', 0)
        module = order_data.get('module', 'manual')

        if quantity <= 0 or price <= 0:
            self._log("ERROR", "Invalid order parameters")
            return None

        if order_type == 'BUY':
            cost = price * quantity
            if cost > self.portfolio['balance']:
                self._log("WARNING", f"Insufficient balance: {cost} > {self.portfolio['balance']}")
                return None

        order_id = self._generate_order_id()
        order = {
            'id': order_id,
            'symbol': symbol,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'module': module,
            'status': 'executed',
            'timestamp': datetime.now().isoformat()
        }

        self.portfolio['orders'].append(order)

        if order_type == 'BUY':
            result = self._execute_buy(order)
        else:
            result = self._execute_sell(order)

        self.portfolio['history'].append({
            'order_id': order_id,
            'type': order_type,
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'timestamp': datetime.now().isoformat()
        })

        if self.event_engine:
            self.event_engine.publish('PAPER_TRADE_EXECUTED', {
                'order': order,
                'portfolio': self.get_portfolio_summary(),
                'timestamp': datetime.now().isoformat()
            })

        self._log("INFO", f"Paper order executed: {order_type} {quantity} {symbol} @ {price}")
        return order

    def _execute_buy(self, order):
        """Execute a BUY order."""
        symbol = order['symbol']
        price = order['price']
        quantity = order['quantity']

        cost = price * quantity
        self.portfolio['balance'] -= cost

        if symbol not in self.portfolio['positions']:
            self.portfolio['positions'][symbol] = {
                'symbol': symbol,
                'quantity': 0,
                'average_price': 0,
                'total_cost': 0,
                'entry_time': datetime.now().isoformat(),
                'trades': []
            }

        pos = self.portfolio['positions'][symbol]
        total_quantity = pos['quantity'] + quantity
        total_cost = pos['total_cost'] + cost
        pos['quantity'] = total_quantity
        pos['average_price'] = total_cost / total_quantity if total_quantity > 0 else 0
        pos['total_cost'] = total_cost

        trade = {
            'id': self._generate_trade_id(),
            'type': 'BUY',
            'price': price,
            'quantity': quantity,
            'timestamp': datetime.now().isoformat()
        }
        pos['trades'].append(trade)

        self.portfolio['equity'] = self.portfolio['balance'] + total_cost

        return order

    def _execute_sell(self, order):
        """Execute a SELL order."""
        symbol = order['symbol']
        price = order['price']
        quantity = order['quantity']

        if symbol not in self.portfolio['positions']:
            self._log("WARNING", f"No position found for {symbol}")
            return None

        pos = self.portfolio['positions'][symbol]
        if pos['quantity'] < quantity:
            self._log("WARNING", f"Insufficient quantity: {pos['quantity']} < {quantity}")
            return None

        avg_price = pos['average_price']
        pnl = (price - avg_price) * quantity

        pos['quantity'] -= quantity
        pos['total_cost'] -= avg_price * quantity

        self.portfolio['balance'] += price * quantity

        if pos['quantity'] <= 0:
            del self.portfolio['positions'][symbol]

        trade = {
            'id': self._generate_trade_id(),
            'type': 'SELL',
            'price': price,
            'quantity': quantity,
            'pnl': pnl,
            'timestamp': datetime.now().isoformat()
        }
        self.portfolio['trades'].append(trade)

        self.portfolio['pnl'] += pnl
        self.portfolio['equity'] = self.portfolio['balance'] + sum(
            pos['total_cost'] for pos in self.portfolio['positions'].values()
        )

        return order

    def get_portfolio_summary(self):
        """Get portfolio summary."""
        return {
            'balance': round(self.portfolio['balance'], 2),
            'equity': round(self.portfolio['equity'], 2),
            'pnl': round(self.portfolio['pnl'], 2),
            'positions': len(self.portfolio['positions']),
            'total_trades': len(self.portfolio['trades']),
            'total_orders': len(self.portfolio['orders'])
        }

    def get_positions(self):
        """Get all open positions."""
        return self.portfolio['positions']

    def get_trades(self):
        """Get all trades."""
        return self.portfolio['trades']

    def get_orders(self):
        """Get all orders."""
        return self.portfolio['orders']

    def _generate_order_id(self):
        """Generate a unique order ID."""
        return f"PAPER_ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

    def _generate_trade_id(self):
        """Generate a unique trade ID."""
        return f"PAPER_TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [PaperTrading] [{level}] {message}")
