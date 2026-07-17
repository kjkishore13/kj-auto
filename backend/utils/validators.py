# ============================================================
# KJs TRD Trading Terminal - Validators Utility
# ============================================================

import re
from datetime import datetime

class Validators:
    """Collection of validation functions."""

    @staticmethod
    def validate_symbol(symbol):
        """Validate a trading symbol."""
        if not symbol or not isinstance(symbol, str):
            return False, "Symbol must be a non-empty string"

        symbol = symbol.strip().upper()

        if not re.match(r'^[A-Z0-9&\-. ]+$', symbol):
            return False, "Symbol contains invalid characters"

        return True, symbol

    @staticmethod
    def validate_quantity(quantity):
        """Validate order quantity."""
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return False, "Quantity must be a number"

        if quantity <= 0:
            return False, "Quantity must be greater than 0"

        if quantity > 10000:
            return False, "Quantity exceeds maximum limit (10000)"

        return True, quantity

    @staticmethod
    def validate_price(price):
        """Validate price."""
        try:
            price = float(price)
        except (ValueError, TypeError):
            return False, "Price must be a number"

        if price <= 0:
            return False, "Price must be greater than 0"

        if price > 10000000:
            return False, "Price exceeds maximum limit"

        return True, round(price, 2)

    @staticmethod
    def validate_date(date_str):
        """Validate a date string."""
        if not date_str:
            return False, "Date is required"

        try:
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y%m%d']:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return True, parsed.strftime('%Y-%m-%d')
                except ValueError:
                    continue

            return False, "Invalid date format. Use YYYY-MM-DD"
        except Exception:
            return False, "Invalid date format"

    @staticmethod
    def validate_timeframe(timeframe):
        """Validate timeframe."""
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d', '1w', '1M']

        if not timeframe:
            return False, "Timeframe is required"

        timeframe = timeframe.lower()
        if timeframe not in valid_timeframes:
            return False, f"Invalid timeframe. Valid: {', '.join(valid_timeframes)}"

        return True, timeframe

    @staticmethod
    def validate_order_type(order_type):
        """Validate order type."""
        valid_types = ['BUY', 'SELL', 'EXIT']

        if not order_type:
            return False, "Order type is required"

        order_type = order_type.upper()
        if order_type not in valid_types:
            return False, f"Invalid order type. Valid: {', '.join(valid_types)}"

        return True, order_type

    @staticmethod
    def validate_signal(signal):
        """Validate a trading signal."""
        valid_signals = ['BUY', 'SELL', 'EXIT', 'HOLD']

        if not signal:
            return False, "Signal is required"

        signal = signal.upper()
        if signal not in valid_signals:
            return False, f"Invalid signal. Valid: {', '.join(valid_signals)}"

        return True, signal

    @staticmethod
    def validate_module_name(module_name):
        """Validate a module name."""
        if not module_name or not isinstance(module_name, str):
            return False, "Module name must be a non-empty string"

        if not re.match(r'^[a-zA-Z0-9_]+$', module_name):
            return False, "Module name can only contain letters, numbers, and underscores"

        if len(module_name) > 50:
            return False, "Module name exceeds maximum length (50 characters)"

        return True, module_name

    @staticmethod
    def validate_module_type(module_type):
        """Validate a module type."""
        valid_types = ['strategy', 'indicator', 'screener', 'alert', 'automation']

        if not module_type:
            return False, "Module type is required"

        module_type = module_type.lower()
        if module_type not in valid_types:
            return False, f"Invalid module type. Valid: {', '.join(valid_types)}"

        return True, module_type

    @staticmethod
    def validate_api_key(api_key):
        """Validate an API key."""
        if not api_key or not isinstance(api_key, str):
            return False, "API key must be a non-empty string"

        if len(api_key) < 10:
            return False, "API key is too short"

        return True, api_key

    @staticmethod
    def validate_percentage(value):
        """Validate a percentage value."""
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, "Value must be a number"

        if value < 0 or value > 100:
            return False, "Value must be between 0 and 100"

        return True, round(value, 2)

    @staticmethod
    def validate_risk_per_trade(value):
        """Validate risk per trade."""
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, "Value must be a number"

        if value <= 0 or value > 10:
            return False, "Risk per trade must be between 0 and 10%"

        return True, round(value, 2)

    @staticmethod
    def validate_all(data, rules):
        """Validate multiple fields at once."""
        errors = {}
        validated = {}
        is_valid = True

        for field, value in data.items():
            if field in rules:
                valid, result = rules[field](value)
                if valid:
                    validated[field] = result
                else:
                    errors[field] = result
                    is_valid = False
            else:
                validated[field] = value

        return is_valid, errors, validated
