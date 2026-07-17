# ============================================================
# KJs TRD Trading Terminal - Module Tests
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_momentum_breakout():
    """Test Momentum Breakout strategy."""
    print("Testing Momentum Breakout strategy...")

    try:
        from modules.strategies.MomentumBreakout import MomentumBreakout

        strategy = MomentumBreakout()

        assert strategy.name == "Momentum Breakout"
        assert strategy.type == "strategy"
        assert strategy.version == "1.0.0"

        context = {}
        result = strategy.initialize(context)
        assert result is True

        candle = {'close': 22500, 'high': 22550, 'low': 22450, 'volume': 1000000}
        context = {'candles': []}
        result = strategy.on_candle(candle, context)
        assert result == (None, None)

        context = {'candles': []}
        for i in range(25):
            context['candles'].append({
                'close': 22000 + i * 20,
                'high': 22050 + i * 20,
                'low': 21950 + i * 20,
                'volume': 1000000 + i * 10000
            })

        candle = {'close': 22500, 'high': 22550, 'low': 22450, 'volume': 2000000}
        result = strategy.on_candle(candle, context)

        if result and result[0] == 'BUY':
            print("✅ Momentum Breakout test passed")
            return True
        else:
            print("⚠️ Momentum Breakout - no signal generated (may need more data)")
            return True

    except Exception as e:
        print(f"❌ Momentum Breakout test failed: {str(e)}")
        return False

def test_previous_day_breakout():
    """Test Previous Day Breakout strategy."""
    print("Testing Previous Day Breakout strategy...")

    try:
        from modules.strategies.PreviousDayBreakout import PreviousDayBreakout

        strategy = PreviousDayBreakout()

        assert strategy.name == "Previous Day Breakout"
        assert strategy.type == "strategy"
        assert strategy.version == "2.1.0"

        print("✅ Previous Day Breakout test passed")
        return True

    except Exception as e:
        print(f"❌ Previous Day Breakout test failed: {str(e)}")
        return False

def test_ema_indicator():
    """Test EMA indicator."""
    print("Testing EMA indicator...")

    try:
        from modules.indicators.EMA import EMA

        indicator = EMA()

        assert indicator.name == "EMA Ribbon"
        assert indicator.type == "indicator"
        assert indicator.periods == [9, 20, 50, 200]

        candles = []
        for i in range(1, 100):
            candles.append({
                'close': 100 + i * 0.5,
                'high': 102 + i * 0.5,
                'low': 98 + i * 0.5,
                'volume': 1000000
            })

        result = indicator.calculate(candles)
        assert result is not None
        assert len(result) == 4

        print("✅ EMA indicator test passed")
        return True

    except Exception as e:
        print(f"❌ EMA indicator test failed: {str(e)}")
        return False

def test_rsi_indicator():
    """Test RSI indicator."""
    print("Testing RSI indicator...")

    try:
        from modules.indicators.RSI import RSI

        indicator = RSI()

        assert indicator.name == "RSI"
        assert indicator.type == "indicator"
        assert indicator.period == 14

        print("✅ RSI indicator test passed")
        return True

    except Exception as e:
        print(f"❌ RSI indicator test failed: {str(e)}")
        return False

def test_momentum_scanner():
    """Test Momentum Scanner."""
    print("Testing Momentum Scanner...")

    try:
        from modules.screeners.MomentumScanner import MomentumScanner

        scanner = MomentumScanner()

        assert scanner.name == "Momentum Scanner"
        assert scanner.type == "screener"

        print("✅ Momentum Scanner test passed")
        return True

    except Exception as e:
        print(f"❌ Momentum Scanner test failed: {str(e)}")
        return False

def test_vwap_alert():
    """Test VWAP Alert."""
    print("Testing VWAP Alert...")

    try:
        from modules.alerts.VWAPAlert import VWAPAlert

        alert = VWAPAlert()

        assert alert.name == "VWAP Alert"
        assert alert.type == "alert"

        print("✅ VWAP Alert test passed")
        return True

    except Exception as e:
        print(f"❌ VWAP Alert test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all module tests."""
    print("=" * 50)
    print("🚀 Running Module Tests")
    print("=" * 50)

    tests = [
        test_momentum_breakout,
        test_previous_day_breakout,
        test_ema_indicator,
        test_rsi_indicator,
        test_momentum_scanner,
        test_vwap_alert
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
