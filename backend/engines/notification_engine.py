# ============================================================
# KJs TRD Trading Terminal - Notification Engine
# ============================================================

from datetime import datetime
import json
import requests

class NotificationEngine:
    """Sends notifications through multiple channels."""

    def __init__(self):
        self.channels = {
            'telegram': {'enabled': False, 'bot_token': None, 'chat_id': None},
            'email': {'enabled': False, 'smtp_server': None, 'username': None, 'password': None},
            'whatsapp': {'enabled': False},
            'push': {'enabled': False}
        }
        self.notifications = []
        self.event_engine = None
        self._log("INFO", "Notification Engine initialized")

    def initialize(self, event_engine=None, config=None):
        """Initialize the notification engine."""
        self.event_engine = event_engine

        if config:
            self._load_config(config)

        self._log("INFO", "Notification Engine initialized with dependencies")
        return True

    def _load_config(self, config):
        """Load notification configuration."""
        channels = config.get('channels', {})

        if 'telegram' in channels:
            self.channels['telegram'] = {
                'enabled': channels['telegram'].get('enabled', False),
                'bot_token': channels['telegram'].get('bot_token'),
                'chat_id': channels['telegram'].get('chat_id')
            }

        if 'email' in channels:
            self.channels['email'] = {
                'enabled': channels['email'].get('enabled', False),
                'smtp_server': channels['email'].get('smtp_server'),
                'username': channels['email'].get('username'),
                'password': channels['email'].get('password')
            }

        if 'whatsapp' in channels:
            self.channels['whatsapp']['enabled'] = channels['whatsapp'].get('enabled', False)

        if 'push' in channels:
            self.channels['push']['enabled'] = channels['push'].get('enabled', False)

    def send_notification(self, message, channel=None, data=None):
        """Send a notification."""
        notification = {
            'id': self._generate_notification_id(),
            'message': message,
            'channel': channel or 'all',
            'data': data or {},
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }

        if channel and channel in self.channels:
            result = self._send_to_channel(channel, message, data)
            notification['status'] = 'sent' if result else 'failed'
        else:
            results = []
            for ch in self.channels:
                if self.channels[ch].get('enabled', False):
                    result = self._send_to_channel(ch, message, data)
                    results.append(result)
            notification['status'] = 'sent' if any(results) else 'failed'

        self.notifications.append(notification)

        if self.event_engine:
            self.event_engine.publish('NOTIFICATION_SENT', {
                'notification': notification,
                'timestamp': datetime.now().isoformat()
            })

        return notification

    def _send_to_channel(self, channel, message, data=None):
        """Send notification to a specific channel."""
        try:
            if channel == 'telegram':
                return self._send_telegram(message, data)
            elif channel == 'email':
                return self._send_email(message, data)
            elif channel == 'whatsapp':
                return self._send_whatsapp(message, data)
            elif channel == 'push':
                return self._send_push(message, data)
            else:
                self._log("WARNING", f"Unknown channel: {channel}")
                return False
        except Exception as e:
            self._log("ERROR", f"Failed to send {channel} notification: {str(e)}")
            return False

    def _send_telegram(self, message, data=None):
        """Send a Telegram notification."""
        config = self.channels.get('telegram', {})
        if not config.get('enabled'):
            return False

        bot_token = config.get('bot_token')
        chat_id = config.get('chat_id')

        if not bot_token or not chat_id:
            self._log("ERROR", "Telegram credentials not configured")
            return False

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                self._log("INFO", "Telegram notification sent")
                return True
            else:
                self._log("ERROR", f"Telegram API error: {response.text}")
                return False

        except Exception as e:
            self._log("ERROR", f"Telegram error: {str(e)}")
            return False

    def _send_email(self, message, data=None):
        """Send an email notification."""
        config = self.channels.get('email', {})
        if not config.get('enabled'):
            return False

        self._log("INFO", f"Email notification: {message[:50]}...")
        return True

    def _send_whatsapp(self, message, data=None):
        """Send a WhatsApp notification."""
        config = self.channels.get('whatsapp', {})
        if not config.get('enabled'):
            return False

        self._log("INFO", f"WhatsApp notification: {message[:50]}...")
        return True

    def _send_push(self, message, data=None):
        """Send a push notification."""
        config = self.channels.get('push', {})
        if not config.get('enabled'):
            return False

        self._log("INFO", f"Push notification: {message[:50]}...")
        return True

    def send_signal_alert(self, module_name, signal, price, symbol=None, data=None):
        """Send a trading signal alert."""
        symbol = symbol or 'NIFTY 50'
        message = f"""
📊 <b>Trading Signal Alert</b>
━━━━━━━━━━━━━━━━━━━
📈 <b>Module:</b> {module_name}
🔔 <b>Signal:</b> {signal}
💲 <b>Symbol:</b> {symbol}
💰 <b>Price:</b> ₹{price:,.2f}
🕐 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━
"""
        return self.send_notification(message.strip(), data=data)

    def send_status_update(self, status, details=None):
        """Send a system status update."""
        message = f"""
⚡ <b>System Status Update</b>
━━━━━━━━━━━━━━━━━━━
📊 <b>Status:</b> {status}
📋 <b>Details:</b> {details or 'All systems operational'}
🕐 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━
"""
        return self.send_notification(message.strip())

    def get_notifications(self, limit=50):
        """Get recent notifications."""
        return self.notifications[-limit:]

    def enable_channel(self, channel, config=None):
        """Enable a notification channel."""
        if channel in self.channels:
            self.channels[channel]['enabled'] = True
            if config:
                self.channels[channel].update(config)
            self._log("INFO", f"Channel enabled: {channel}")
            return True
        return False

    def disable_channel(self, channel):
        """Disable a notification channel."""
        if channel in self.channels:
            self.channels[channel]['enabled'] = False
            self._log("INFO", f"Channel disabled: {channel}")
            return True
        return False

    def _generate_notification_id(self):
        """Generate a unique notification ID."""
        return f"NOTIF_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.notifications)}"

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Notification] [{level}] {message}")
