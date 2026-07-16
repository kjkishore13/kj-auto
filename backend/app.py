# ============================================================
# KJs TRD Trading Terminal - Backend Server
# ============================================================

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='../')
CORS(app)

# ============================================================
# MOCK DATA GENERATOR (Fallback when Dhan is not available)
# ============================================================

def generate_mock_candles(count=100):
    """Generate mock candle data for testing"""
    data = []
    price = 22400
    now = datetime.now()
    one_hour = 60 * 60

    for i in range(count - 1, -1, -1):
        change = (random.random() - 0.48) * 60
        open_price = price
        close_price = price + change
        high = max(open_price, close_price) + random.random() * 20
        low = min(open_price, close_price) - random.random() * 20
        volume = int(100000 + random.random() * 900000)

        data.append({
            'time': int((now - timedelta(seconds=i * one_hour)).timestamp()),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close_price, 2),
            'volume': volume
        })

        price = close_price

    return data

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def serve_index():
    return send_from_directory('../', 'index.html')

@app.route('/chart.html')
def serve_chart():
    return send_from_directory('../', 'chart.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        "status": "running",
        "runtime": "online",
        "market_data": "connected",
        "broker": "dhan",
        "notification": "telegram",
        "database": "connected",
        "uptime": "2h 14m",
        "memory": "342MB",
        "running_modules": 4
    })

@app.route('/api/market/historical/<symbol>')
def get_historical_data(symbol):
    """Get historical candle data"""
    period = request.args.get('period', '5d')
    interval = request.args.get('interval', '15m')

    print(f"📊 Fetching data for {symbol} ({period}, {interval})")

    # Generate mock data
    count = 100
    if interval == '1m':
        count = 60
    elif interval == '5m':
        count = 100
    elif interval == '15m':
        count = 200
    elif interval == '1h':
        count = 300
    elif interval == '1d':
        count = 400

    data = generate_mock_candles(count)
    return jsonify(data)

@app.route('/api/market/price/<symbol>')
def get_current_price(symbol):
    """Get current price"""
    price = 22450 + (random.random() - 0.5) * 100
    return jsonify({
        'symbol': symbol,
        'price': round(price, 2),
        'change': round((random.random() - 0.5) * 50, 2),
        'change_percent': round((random.random() - 0.5) * 0.5, 2),
        'volume': int(100000 + random.random() * 900000),
        'high': round(price + random.random() * 20, 2),
        'low': round(price - random.random() * 20, 2),
        'open': round(price - random.random() * 10, 2),
        'close': round(price, 2)
    })

@app.route('/api/modules')
def get_modules():
    """Get list of all modules"""
    modules = [
        {
            "name": "Momentum Breakout",
            "type": "strategy",
            "description": "Buys on breakout above 20H with volume",
            "status": "running",
            "version": "1.0.0"
        },
        {
            "name": "Previous Day Breakout",
            "type": "strategy",
            "description": "Trades breakouts above yesterday's high",
            "status": "running",
            "version": "2.1.0"
        },
        {
            "name": "EMA Ribbon",
            "type": "indicator",
            "description": "Multiple EMA lines for trend confirmation",
            "status": "running",
            "version": "1.2.0"
        },
        {
            "name": "Momentum Scanner",
            "type": "screener",
            "description": "Scans for momentum stocks across watchlist",
            "status": "stopped",
            "version": "1.0.0"
        }
    ]
    return jsonify(modules)

@app.route('/api/modules/create', methods=['POST'])
def create_module():
    """Create a new module"""
    try:
        data = request.get_json()
        module_name = data.get('name')
        module_type = data.get('type')
        module_code = data.get('code', '')

        if not module_name or not module_type:
            return jsonify({
                "status": "error",
                "message": "Module name and type are required"
            }), 400

        # Create directory if it doesn't exist
        module_dir = f"../modules/{module_type}s"
        os.makedirs(module_dir, exist_ok=True)

        filename = f"{module_name}.py"
        filepath = os.path.join(module_dir, filename)

        counter = 1
        while os.path.exists(filepath):
            filename = f"{module_name}_{counter}.py"
            filepath = os.path.join(module_dir, filename)
            counter += 1

        with open(filepath, 'w') as f:
            f.write(module_code)

        return jsonify({
            "status": "success",
            "message": f"Module '{module_name}' created successfully",
            "file": filename,
            "path": filepath
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/run_module/<module_name>', methods=['POST'])
def run_module(module_name):
    """Start a module"""
    return jsonify({
        "status": "success",
        "message": f"Module '{module_name}' started successfully",
        "module": module_name
    })

@app.route('/api/stop_module/<module_name>', methods=['POST'])
def stop_module(module_name):
    """Stop a module"""
    return jsonify({
        "status": "success",
        "message": f"Module '{module_name}' stopped",
        "module": module_name
    })

# ============================================================
# START THE SERVER
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 KJs TRD Trading Terminal - Backend Server")
    print("=" * 50)
    print("📊 Server running at: http://localhost:5000")
    print("📈 API available at: http://localhost:5000/api/status")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
