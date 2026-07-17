# ============================================================
# KJs TRD Trading Terminal - Runtime Engine
# ============================================================

import importlib
import sys
import os
import traceback
from datetime import datetime

class RuntimeEngine:
    """Executes Python modules and manages their lifecycle."""

    def __init__(self):
        self.modules = {}
        self.running_modules = {}
        self.event_engine = None
        self.market_data_engine = None

    def initialize(self, event_engine=None, market_data_engine=None):
        """Initialize the runtime engine with dependencies."""
        self.event_engine = event_engine
        self.market_data_engine = market_data_engine
        self._log("INFO", "Runtime Engine initialized")
        return True

    def load_module(self, module_name, module_path):
        """Load a Python module from file path."""
        try:
            module_dir = os.path.dirname(module_path)
            if module_dir not in sys.path:
                sys.path.append(module_dir)

            module_name_only = os.path.splitext(os.path.basename(module_path))[0]
            module = importlib.import_module(module_name_only)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (callable(attr) and 
                    attr_name not in ['Module', 'Strategy', 'Indicator'] and
                    hasattr(attr, '__module__')):
                    if hasattr(attr, 'initialize') and hasattr(attr, 'on_candle'):
                        instance = attr()
                        instance.module_path = module_path
                        instance.module_name = module_name
                        self.modules[module_name] = instance
                        self._log("INFO", f"Loaded module: {module_name}")
                        return instance

            self._log("ERROR", f"No valid module class found in {module_path}")
            return None

        except Exception as e:
            self._log("ERROR", f"Failed to load module {module_name}: {str(e)}")
            return None

    def start_module(self, module_name):
        """Start a loaded module."""
        if module_name not in self.modules:
            self._log("ERROR", f"Module {module_name} not loaded")
            return False

        if module_name in self.running_modules and self.running_modules[module_name] == 'running':
            self._log("WARNING", f"Module {module_name} already running")
            return True

        try:
            module = self.modules[module_name]
            context = {'candles': [], 'symbol': 'NIFTY 50', 'timeframe': '15m', 'position': None}

            if hasattr(module, 'initialize'):
                module.initialize(context)

            self.running_modules[module_name] = 'running'
            self._log("INFO", f"Started module: {module_name}")

            if self.event_engine:
                self.event_engine.publish('MODULE_STARTED', {
                    'module_name': module_name,
                    'timestamp': datetime.now().isoformat()
                })

            return True

        except Exception as e:
            self._log("ERROR", f"Failed to start module {module_name}: {str(e)}")
            self.running_modules[module_name] = 'error'
            return False

    def stop_module(self, module_name):
        """Stop a running module."""
        if module_name not in self.modules:
            return False

        if module_name not in self.running_modules:
            return True

        try:
            module = self.modules[module_name]
            if hasattr(module, 'on_stop'):
                module.on_stop()

            self.running_modules[module_name] = 'stopped'
            self._log("INFO", f"Stopped module: {module_name}")

            if self.event_engine:
                self.event_engine.publish('MODULE_STOPPED', {
                    'module_name': module_name,
                    'timestamp': datetime.now().isoformat()
                })

            return True

        except Exception as e:
            self._log("ERROR", f"Failed to stop module {module_name}: {str(e)}")
            return False

    def pause_module(self, module_name):
        """Pause a running module."""
        if module_name in self.running_modules and self.running_modules[module_name] == 'running':
            self.running_modules[module_name] = 'paused'
            self._log("INFO", f"Paused module: {module_name}")
            return True
        return False

    def resume_module(self, module_name):
        """Resume a paused module."""
        if module_name in self.running_modules and self.running_modules[module_name] == 'paused':
            self.running_modules[module_name] = 'running'
            self._log("INFO", f"Resumed module: {module_name}")
            return True
        return False

    def process_candle(self, candle_data):
        """Process a new candle through all running modules."""
        results = {}

        for module_name, status in self.running_modules.items():
            if status != 'running':
                continue

            try:
                module = self.modules[module_name]
                if hasattr(module, 'on_candle'):
                    context = self._get_module_context(module_name)
                    if context:
                        context['candles'].append(candle_data)
                        if len(context['candles']) > 200:
                            context['candles'] = context['candles'][-200:]

                    result = module.on_candle(candle_data, context or {})

                    if result:
                        signal, data = result if isinstance(result, tuple) else (result, None)
                        if signal:
                            results[module_name] = {
                                'signal': signal,
                                'data': data,
                                'price': candle_data.get('close'),
                                'timestamp': datetime.now().isoformat()
                            }

                            if self.event_engine:
                                self.event_engine.publish('SIGNAL_GENERATED', {
                                    'module_name': module_name,
                                    'signal': signal,
                                    'data': data,
                                    'price': candle_data.get('close'),
                                    'timestamp': datetime.now().isoformat()
                                })

            except Exception as e:
                self._log("ERROR", f"Error in module {module_name}: {str(e)}")

        return results

    def _get_module_context(self, module_name):
        """Get or create context for a module."""
        if not hasattr(self, '_contexts'):
            self._contexts = {}

        if module_name not in self._contexts:
            self._contexts[module_name] = {
                'candles': [],
                'symbol': 'NIFTY 50',
                'timeframe': '15m',
                'position': None,
                'orders': []
            }

        return self._contexts[module_name]

    def get_module_status(self, module_name):
        """Get status of a module."""
        if module_name in self.running_modules:
            return self.running_modules[module_name]
        return 'unknown'

    def get_all_modules(self):
        """Get all loaded modules."""
        return list(self.modules.keys())

    def get_running_modules(self):
        """Get all running modules."""
        return [name for name, status in self.running_modules.items() if status == 'running']

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Runtime] [{level}] {message}")

    def shutdown(self):
        """Shutdown the runtime engine."""
        for module_name in list(self.running_modules.keys()):
            self.stop_module(module_name)
        self._log("INFO", "Runtime Engine shutdown")
