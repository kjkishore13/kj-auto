# ============================================================
# KJs TRD Trading Terminal - Event Engine
# ============================================================

from datetime import datetime
import threading
import queue
import time

class EventEngine:
    """Central event bus for platform communication."""

    def __init__(self):
        self.subscribers = {}
        self.event_queue = queue.Queue()
        self.running = False
        self.thread = None
        self._log("INFO", "Event Engine initialized")

    def start(self):
        """Start the event engine."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._process_events, daemon=True)
        self.thread.start()
        self._log("INFO", "Event Engine started")

    def stop(self):
        """Stop the event engine."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self._log("INFO", "Event Engine stopped")

    def subscribe(self, event_type, callback):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        self._log("DEBUG", f"Subscribed to {event_type}")

    def unsubscribe(self, event_type, callback):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            if callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
                self._log("DEBUG", f"Unsubscribed from {event_type}")

    def publish(self, event_type, data=None):
        """Publish an event."""
        event = {
            'type': event_type,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        self.event_queue.put(event)
        self._log("DEBUG", f"Published event: {event_type}")

    def _process_events(self):
        """Process events from the queue."""
        while self.running:
            try:
                event = self.event_queue.get(timeout=0.1)
                self._dispatch_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                self._log("ERROR", f"Error processing event: {str(e)}")

    def _dispatch_event(self, event):
        """Dispatch an event to all subscribers."""
        event_type = event.get('type')
        data = event.get('data')

        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event_type, data, event.get('timestamp'))
                except Exception as e:
                    self._log("ERROR", f"Error in subscriber callback: {str(e)}")

    def publish_signal(self, module_name, signal, price, data=None):
        """Helper method to publish a trading signal."""
        self.publish('SIGNAL_GENERATED', {
            'module_name': module_name,
            'signal': signal,
            'price': price,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        })

    def publish_trade(self, trade_type, symbol, price, quantity, data=None):
        """Helper method to publish a trade event."""
        self.publish('TRADE_EXECUTED', {
            'type': trade_type,
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        })

    def publish_notification(self, channel, message, data=None):
        """Helper method to publish a notification event."""
        self.publish('NOTIFICATION_SENT', {
            'channel': channel,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        })

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [EventEngine] [{level}] {message}")
