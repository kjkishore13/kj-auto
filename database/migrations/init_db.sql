-- ============================================================
-- KJs TRD Trading Terminal - Initial Database Schema
-- ============================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modules table
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    version TEXT,
    author TEXT,
    description TEXT,
    code TEXT,
    status TEXT DEFAULT 'stopped',
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL,
    quantity INTEGER,
    pnl REAL,
    status TEXT DEFAULT 'open',
    module_id INTEGER,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL,
    status TEXT DEFAULT 'pending',
    order_type TEXT DEFAULT 'market',
    trade_id INTEGER,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    FOREIGN KEY (trade_id) REFERENCES trades(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'sent',
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Logs table
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    source TEXT,
    message TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    symbols TEXT NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Backtest results table
CREATE TABLE IF NOT EXISTS backtests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER,
    symbol TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    initial_capital REAL,
    final_equity REAL,
    return_percent REAL,
    win_rate REAL,
    total_trades INTEGER,
    results_json TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_at ON trades(created_at);
CREATE INDEX idx_orders_symbol ON orders(symbol);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_modules_name ON modules(name);
CREATE INDEX idx_modules_type ON modules(type);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_created_at ON logs(created_at);

-- Insert default admin user (password: admin123)
INSERT OR IGNORE INTO users (username, email, password_hash) 
VALUES ('admin', 'admin@kjs-trd.com', 'admin123');

-- Insert sample modules
INSERT OR IGNORE INTO modules (name, type, version, author, description, status) 
VALUES 
    ('Momentum Breakout', 'strategy', '1.0.0', 'KJ', 'Buys on breakout above 20H with volume', 'running'),
    ('Previous Day Breakout', 'strategy', '2.1.0', 'KJ', 'Trades breakouts above yesterday''s high', 'running'),
    ('EMA Ribbon', 'indicator', '1.2.0', 'KJ', 'Multiple EMA lines for trend confirmation', 'running'),
    ('Momentum Scanner', 'screener', '1.0.0', 'KJ', 'Scans for momentum stocks', 'stopped');

-- Insert sample watchlist
INSERT OR IGNORE INTO watchlists (name, symbols, user_id) 
VALUES ('Nifty 50', '["NIFTY 50", "BANKNIFTY", "RELIANCE", "TCS", "HDFC"]', 1);

-- Insert sample log entry
INSERT OR IGNORE INTO logs (level, source, message) 
VALUES ('INFO', 'init_db', 'Database initialized successfully');

-- ============================================================
-- Migration tracking table
-- ============================================================
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO migrations (version) VALUES ('1.0.0');
