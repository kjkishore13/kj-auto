# ============================================================
# KJs TRD Trading Terminal - Dhan Broker Integration
# ============================================================

from .broker_interface import BrokerInterface
from datetime import datetime
import json
import requests

class DhanBroker(BrokerInterface):
    """Dhan broker implementation."""

    def __init__(self):
        super().__init__()
        self.broker_name = 'Dhan'
        self.base_url = 'https://api.dhan.co'
        self.client_id = None
        self.auth_token = None
        self._log("INFO", "Dhan Broker initialized")

    def connect(self, client_id, auth_token, config=None):
        """Connect to Dhan broker."""
        self.client_id = client_id
        self.auth_token = auth_token
        self.api_key = client_id
        self.access_token = auth_token
        self.connected = True

        if config:
            self.base_url = config.get('api_url', self.base_url)

        self._log("INFO", f"Connected to Dhan broker (Client: {client_id})")
        return True

    def disconnect(self):
        """Disconnect from Dhan broker."""
        self.client_id = None
        self.auth_token = None
        self.connected = False
        self._log("INFO", "Disconnected from Dhan broker")
        return True

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make a request to Dhan API."""
        if not self.connected:
            self._log("ERROR", "Not connected to Dhan")
            return None

        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return None

            if response.status_code in [200, 201]:
                return response.json()
            else:
                self._log("ERROR", f"Dhan API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            self._log("ERROR", f"Dhan API request failed: {str(e)}")
            return None

    def place_order(self, symbol, quantity, order_type, price=None, order_type_detail='MARKET'):
        """Place an order through Dhan."""
        if not self.connected:
            self._log("ERROR", "Not connected to Dhan")
            return None

        order_type_map = {
            'BUY': 'BUY',
            'SELL': 'SELL'
        }

        dhan_order_type = {
            'MARKET': 'MARKET',
            'LIMIT': 'LIMIT',
            'SL-M': 'SL-M'
        }

        order_data = {
            'securityId': symbol,
            'exchangeSegment': 'NSE',
            'transactionType': order_type_map.get(order_type, 'BUY'),
            'quantity': quantity,
            'orderType': dhan_order_type.get(order_type_detail, 'MARKET')
        }

        if price and order_type_detail != 'MARKET':
            order_data['price'] = price

        result = self._make_request('POST', '/v2/orders', order_data)

        if result:
            order = {
                'id': result.get('orderId', self._generate_order_id()),
                'symbol': symbol,
                'quantity': quantity,
                'order_type': order_type,
                'price': price,
                'type': order_type_detail,
                'status': result.get('status', 'pending'),
                'timestamp': datetime.now().isoformat(),
                'broker': self.broker_name,
                'raw_response': result
            }
            self._log("INFO", f"Dhan order placed: {order_type} {quantity} {symbol}")
            return order

        return None

    def get_order_status(self, order_id):
        """Get order status from Dhan."""
        result = self._make_request('GET', f'/v2/orders/{order_id}')

        if result:
            return {
                'id': order_id,
                'status': result.get('status', 'unknown'),
                'filled_quantity': result.get('filledQuantity', 0),
                'price': result.get('averagePrice', 0),
                'timestamp': datetime.now().isoformat()
            }

        return {'id': order_id, 'status': 'unknown'}

    def get_positions(self):
        """Get positions from Dhan."""
        result = self._make_request('GET', '/v2/positions')

        if result:
            positions = []
            for pos in result.get('data', []):
                positions.append({
                    'symbol': pos.get('securityId'),
                    'quantity': pos.get('netQuantity', 0),
                    'average_price': pos.get('averagePrice', 0),
                    'current_price': pos.get('lastPrice', 0),
                    'pnl': pos.get('pnl', 0)
                })
            return positions

        return []

    def get_portfolio(self):
        """Get portfolio from Dhan."""
        result = self._make_request('GET', '/v2/portfolio')

        if result:
            return {
                'total_value': result.get('totalValue', 0),
                'available_cash': result.get('availableCash', 0),
                'holdings_value': result.get('holdingsValue', 0),
                'pnl_today': result.get('dayPnL', 0),
                'total_pnl': result.get('totalPnL', 0)
            }

        return {}

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Dhan] [{level}] {message}")
