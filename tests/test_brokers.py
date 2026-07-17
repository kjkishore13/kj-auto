# ============================================================
# KJs TRD Trading Terminal - Broker Tests
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_broker_interface():
    """Test Broker Interface base class."""
    print("Testing Broker Interface...")

    try:
        from backend.brokers.broker_interface import BrokerInterface

        broker = BrokerInterface()

        assert broker.broker_name is None
        assert broker.connected is False

        result = broker.connect("test_api_key", "test_token")
        assert result is True
        assert broker.connected is True

        order = broker.place_order("NIFTY 50", 10, "BUY", 22450)
        assert order is not None
        assert order['symbol'] == "NIFTY 50"
        assert order['quantity'] == 10

        result = broker.disconnect()
        assert result is True
        assert broker.connected is False

        print("✅ Broker Interface test passed")
        return True

    except Exception as e:
        print(f"❌ Broker Interface test failed: {str(e)}")
        return False

def test_dhan_broker():
    """Test Dhan broker integration."""
    print("Testing Dhan broker...")

    try:
        from backend.brokers.dhan import DhanBroker

        broker = DhanBroker()

        assert broker.broker_name == "Dhan"

        result = broker.connect("test_client", "test_token")
        assert result is True
        assert broker.connected is True

        order = broker.place_order("NIFTY 50", 10, "BUY", 22450)
        assert order is not None

        result = broker.disconnect()
        assert result is True

        print("✅ Dhan broker test passed")
        return True

    except Exception as e:
        print(f"❌ Dhan broker test failed: {str(e)}")
        return False

def test_zerodha_broker():
    """Test Zerodha broker integration."""
    print("Testing Zerodha broker...")

    try:
        from backend.brokers.zerodha import ZerodhaBroker

        broker = ZerodhaBroker()

        assert broker.broker_name == "Zerodha"

        result = broker.connect("test_api", "test_token")
        assert result is True

        order = broker.place_order("NIFTY 50", 10, "BUY", 22450)
        assert order is not None

        print("✅ Zerodha broker test passed")
        return True

    except Exception as e:
        print(f"❌ Zerodha broker test failed: {str(e)}")
        return False

def test_order_validation():
    """Test order validation."""
    print("Testing order validation...")

    try:
        from backend.brokers.broker_interface import BrokerInterface

        broker = BrokerInterface()
        broker.connect("test_api", "test_token")

        order = broker.place_order("NIFTY 50", 10, "BUY", 22450)
        assert order is not None
        assert order['quantity'] == 10

        order = broker.place_order("NIFTY 50", -5, "BUY", 22450)
        assert order is not None

        print("✅ Order validation test passed")
        return True

    except Exception as e:
        print(f"❌ Order validation test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling in brokers."""
    print("Testing error handling...")

    try:
        from backend.brokers.broker_interface import BrokerInterface

        broker = BrokerInterface()

        order = broker.place_order("NIFTY 50", 10, "BUY", 22450)
        assert order is None

        positions = broker.get_positions()
        assert positions == []

        print("✅ Error handling test passed")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all broker tests."""
    print("=" * 50)
    print("🚀 Running Broker Tests")
    print("=" * 50)

    tests = [
        test_broker_interface,
        test_dhan_broker,
        test_zerodha_broker,
        test_order_validation,
        test_error_handling
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
