# ============================================================
# KJs TRD Trading Terminal - Runtime Engine Tests
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.runtime_engine import RuntimeEngine
from backend.core.event_engine import EventEngine
from backend.core.module_manager import ModuleManager

def test_runtime_initialization():
    """Test runtime engine initialization."""
    print("Testing Runtime Engine initialization...")

    runtime = RuntimeEngine()
    event_engine = EventEngine()

    result = runtime.initialize(event_engine=event_engine)

    assert result is True, "Runtime initialization failed"
    print("✅ Runtime initialization test passed")
    return True

def test_module_loading():
    """Test loading a module."""
    print("Testing module loading...")

    runtime = RuntimeEngine()
    event_engine = EventEngine()
    runtime.initialize(event_engine=event_engine)

    test_module_path = "modules/strategies/MomentumBreakout.py"

    if os.path.exists(test_module_path):
        result = runtime.load_module("MomentumBreakout", test_module_path)

        if result:
            print("✅ Module loading test passed")
            return True
        else:
            print("❌ Module loading failed")
            return False
    else:
        print("⚠️ Test module not found, skipping")
        return True

def test_module_start_stop():
    """Test starting and stopping a module."""
    print("Testing module start/stop...")

    runtime = RuntimeEngine()
    event_engine = EventEngine()
    runtime.initialize(event_engine=event_engine)

    class MockModule:
        def __init__(self):
            self.name = "Mock Strategy"
            self.type = "strategy"
            self.version = "1.0.0"
            self.author = "Test"
            self.description = "Test module"

        def initialize(self, context):
            return True

        def on_candle(self, candle, context):
            return None, None

        def on_stop(self):
            return True

    runtime.modules["MockModule"] = MockModule()

    start_result = runtime.start_module("MockModule")
    assert start_result is True, "Module start failed"

    status = runtime.get_module_status("MockModule")
    assert status == "running", f"Expected 'running', got '{status}'"

    stop_result = runtime.stop_module("MockModule")
    assert stop_result is True, "Module stop failed"

    status = runtime.get_module_status("MockModule")
    assert status == "stopped", f"Expected 'stopped', got '{status}'"

    print("✅ Module start/stop test passed")
    return True

def test_candle_processing():
    """Test candle processing."""
    print("Testing candle processing...")

    runtime = RuntimeEngine()
    event_engine = EventEngine()
    runtime.initialize(event_engine=event_engine)

    class MockModule:
        def __init__(self):
            self.name = "Mock Strategy"
            self.type = "strategy"

        def initialize(self, context):
            return True

        def on_candle(self, candle, context):
            if candle['close'] > 22500:
                return 'BUY', {'price': candle['close']}
            return None, None

    runtime.modules["MockModule"] = MockModule()
    runtime.start_module("MockModule")

    candle = {
        'time': 1234567890,
        'open': 22400,
        'high': 22600,
        'low': 22350,
        'close': 22550,
        'volume': 1000000
    }

    results = runtime.process_candle(candle)

    assert "MockModule" in results, "Module not in results"
    assert results["MockModule"]["signal"] == "BUY", "Signal not BUY"

    print("✅ Candle processing test passed")
    return True

def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("🚀 Running Runtime Engine Tests")
    print("=" * 50)

    tests = [
        test_runtime_initialization,
        test_module_loading,
        test_module_start_stop,
        test_candle_processing
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            failed += 1

    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0

if __name__ == "__main__":
    run_all_tests()
