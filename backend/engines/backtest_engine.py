# ============================================================
# KJs TRD Trading Terminal - Backtest Engine
# ============================================================

from datetime import datetime
import pandas as pd
import json

class BacktestEngine:
    """Executes backtests on historical data."""

    def __init__(self):
        self.results = {}
        self.execution_engine = None
        self.runtime_engine = None
        self.event_engine = None
        self._log("INFO", "Backtest Engine initialized")

    def initialize(self, execution_engine=None, runtime_engine=None, event_engine=None):
        """Initialize the backtest engine."""
        self.execution_engine = execution_engine
        self.runtime_engine = runtime_engine
        self.event_engine = event_engine
        self._log("INFO", "Backtest Engine initialized with dependencies")
        return True

    def run_backtest(self, module_name, symbol, start_date, end_date, initial_capital=100000):
        """Run a backtest for a specific module."""
        self._log("INFO", f"Starting backtest for {module_name} on {symbol}")

        from ..core.market_data_engine import MarketDataEngine
        market_data = MarketDataEngine()

        try:
            data = market_data.get_historical(symbol, period='6mo', interval='15m')
            if data is None or data.empty:
                self._log("ERROR", f"No historical data found for {symbol}")
                return None
        except Exception as e:
            self._log("ERROR", f"Error fetching data: {str(e)}")
            return None

        if not self.runtime_engine:
            self._log("ERROR", "Runtime engine not initialized")
            return None

        module = self.runtime_engine.modules.get(module_name)
        if not module:
            self._log("ERROR", f"Module {module_name} not found")
            return None

        if self.execution_engine:
            self.execution_engine.set_mode('backtest')
            self.execution_engine.portfolio['balance'] = initial_capital
            self.execution_engine.portfolio['equity'] = initial_capital
            self.execution_engine.positions = {}
            self.execution_engine.trades = []

        trades = []
        equity_curve = []
        context = {'candles': [], 'symbol': symbol, 'timeframe': '15m', 'position': None}

        for idx, row in data.iterrows():
            candle = {
                'time': int(idx.timestamp()),
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'close': round(row['Close'], 2),
                'volume': int(row['Volume'])
            }

            context['candles'].append(candle)
            if len(context['candles']) > 200:
                context['candles'] = context['candles'][-200:]

            try:
                result = module.on_candle(candle, context)
                if result:
                    signal, data_dict = result if isinstance(result, tuple) else (result, None)
                    if signal:
                        signal_data = {
                            'module_name': module_name,
                            'signal': signal,
                            'price': candle['close'],
                            'data': data_dict or {}
                        }
                        if self.execution_engine:
                            order = self.execution_engine.execute_signal(signal_data)
                            if order:
                                trades.append(order)
            except Exception as e:
                self._log("ERROR", f"Error in module execution: {str(e)}")

            if self.execution_engine:
                portfolio = self.execution_engine.get_portfolio()
                equity_curve.append({
                    'time': idx.isoformat(),
                    'equity': portfolio['equity'] + sum(
                        (candle['close'] - pos.get('entry_price', 0)) * pos.get('quantity', 0)
                        for pos in self.execution_engine.positions.values()
                        if pos.get('status') == 'open'
                    )
                })

        results = self._calculate_metrics(trades, equity_curve, initial_capital)
        results['module_name'] = module_name
        results['symbol'] = symbol
        results['start_date'] = start_date
        results['end_date'] = end_date
        results['trades'] = trades
        results['equity_curve'] = equity_curve

        self.results[module_name] = results
        self._log("INFO", f"Backtest completed for {module_name}")

        return results

    def _calculate_metrics(self, trades, equity_curve, initial_capital):
        """Calculate backtest metrics."""
        total_trades = len(trades)

        if total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_pnl': 0,
                'max_drawdown': 0,
                'final_equity': initial_capital,
                'return_percent': 0
            }

        total_pnl = sum(t.get('pnl', 0) for t in trades if 'pnl' in t)

        winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
        losing_trades = sum(1 for t in trades if t.get('pnl', 0) < 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')

        max_drawdown = 0
        peak = initial_capital
        if equity_curve:
            for point in equity_curve:
                equity = point.get('equity', initial_capital)
                if equity > peak:
                    peak = equity
                drawdown = (peak - equity) / peak * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

        final_equity = equity_curve[-1].get('equity', initial_capital) if equity_curve else initial_capital
        return_percent = ((final_equity - initial_capital) / initial_capital) * 100

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'total_pnl': round(total_pnl, 2),
            'max_drawdown': round(max_drawdown, 2),
            'final_equity': round(final_equity, 2),
            'return_percent': round(return_percent, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2)
        }

    def get_results(self, module_name=None):
        """Get backtest results."""
        if module_name:
            return self.results.get(module_name)
        return self.results

    def export_results(self, module_name, filepath=None):
        """Export backtest results to JSON."""
        results = self.get_results(module_name)
        if not results:
            return False

        if not filepath:
            filepath = f"backtest_{module_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        self._log("INFO", f"Exported backtest results to {filepath}")
        return True

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Backtest] [{level}] {message}")
