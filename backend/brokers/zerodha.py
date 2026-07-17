# ============================================================
# KJs TRD Trading Terminal - Zerodha Broker Integration
# ============================================================

from .broker_interface import BrokerInterface
from datetime import datetime
import json
import requests

class ZerodhaBroker(BrokerInterface):
    """Zerodha broker implementation."""

    def __init__(self):
        super().__init__()
        self.broker_name = 'Zerodha'
        self.base_url = 'https://api.kite.trade'
        self.api_key = None
        self.access_token = None
        self._log("INFO", "Zerodha Broker initialized")

    def connect(self, api_key, access_token, config=None):
        """Connect to Zerodha broker."""
        self.api_key = api_key
        self.access_token = access_token
        self.connected = True

        if config:
            self.base_url = config.get('api_url', self.base_url)

        self._log("INFO", "Connected to Zerodha broker")
        return True

    def disconnect(self):
        """Disconnect from Zerodha broker."""
        self.api_key = None
        self.access_token = None
        self.connected = False
        self._log("INFO", "Disconnected from Zerodha broker")
        return True

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make a request to Zerodha Kite API."""
        if not self.connected:
            self._log("ERROR", "Not connected to Zerodha")
            return None

        url = f"{self.base_url}{endpoint}"
        headers = {
            'X-Kite-Version': '3',
            'Authorization': f'token {self.api_key}:{self.access_token}',
            'Content-Type': 'application/json'
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
                return response.json().get('data', response.json())
            else:
                self._log("ERROR", f"Zerodha API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            self._log("ERROR", f"Zerodha API request failed: {str(e)}")
            return None

    def place_order(self, symbol, quantity, order_type, price=None, order_type_detail='MARKET'):
        """Place an order through Zerodha."""
        if not self.connected:
            self._log("ERROR", "Not connected to Zerodha")
            return None

        transaction_type = 'BUY' if order_type == 'BUY' else 'SELL'

        order_data = {
            'tradingsymbol': symbol,
            'exchange': 'NSE',
            'transaction_type': transaction_type,
            'quantity': quantity,
            'order_type': order_type_detail,
            'product': 'MIS'
        }

        if price and order_type_detail in ['LIMIT', 'SL', 'SL-M']:
            order_data['price'] = price

        result = self._make_request('POST', '/orders/regular', order_data)

        if result:
            order = {
                'id': result.get('order_id', self._generate_order_id()),
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
            self._log("INFO", f"Zerodha order placed: {order_type} {quantity} {symbol}")
            return order

        return None

    def get_order_status(self, order_id):
        """Get order status from Zerodha."""
        result = self._make_request('GET', f'/orders/{order_id}')

        if result:
            return {
                'id': order_id,
                'status': result.get('status', 'unknown'),
                'filled_quantity': result.get('filled_quantity', 0),
                'price': result.get('average_price', 0),
                'timestamp': datetime.now().isoformat()
            }

        return {'id': order_id, 'status': 'unknown'}

    def get_positions(self):
        """Get positions from Zerodha."""
        result = self._make_request('GET', '/positions')

        if result:
            positions = []
            for pos in result.get('net', []):
                positions.append({
                    'symbol': pos.get('tradingsymbol'),
                    'quantity': pos.get('quantity', 0),
                    'average_price': pos.get('average_price', 0),
                    'current_price': pos.get('last_price', 0),
                    'pnl': pos.get('unrealised', 0)
                })
            return positions

        return []

    def get_portfolio(self):
        """Get portfolio from Zerodha."""
        result = self._make_request('GET', '/portfolio/holdings')

        if result:
            total_value = sum(h.get('value', 0) for h in result)
            total_pnl = sum(h.get('pnl', 0) for h in result)

            return {
                'total_value': total_value,
                'holdings_value': total_value,
                'total_pnl': total_pnl,
                'holdings': result
            }

        return {}

    def get_margin(self):
        """Get margin from Zerodha."""
        result = self._make_request('GET', '/user/margins')

        if result:
            return {
                'available': result.get('available', {}).get('cash', 0),
                'used': result.get('utilised', {}).get('cash', 0),
                'total': result.get('available', {}).get('cash', 0) + result.get('utilised', {}).get('cash', 0)
            }

        return {}

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Zerodha] [{level}] {message}")
