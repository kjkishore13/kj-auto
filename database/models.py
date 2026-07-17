# ============================================================
# KJs TRD Trading Terminal - Database Models
# ============================================================

from datetime import datetime
import sqlite3
import json

class Database:
    """Database connection and operations"""

    def __init__(self, db_path='database/kjs_trd.db'):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._create_tables()
        return self

    def _create_tables(self):
        """Create all tables if they don't exist"""
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Modules table
        self.cursor.execute('''
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
            )
        ''')

        # Trades table
        self.cursor.execute('''
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
            )
        ''')

        # Orders table
        self.cursor.execute('''
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
            )
        ''')

        # Notifications table
        self.cursor.execute('''
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
            )
        ''')

        # Logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                source TEXT,
                message TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Watchlists table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                symbols TEXT NOT NULL,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Backtest results table
        self.cursor.execute('''
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
            )
        ''')

        self.connection.commit()

    def insert(self, table, data):
        """Insert data into table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, list(data.values()))
        self.connection.commit()
        return self.cursor.lastrowid

    def get(self, table, id_value, id_column='id'):
        """Get a record by ID"""
        query = f"SELECT * FROM {table} WHERE {id_column} = ?"
        self.cursor.execute(query, (id_value,))
        return self.cursor.fetchone()

    def get_all(self, table, conditions=None, order_by=None, limit=None):
        """Get all records from table"""
        query = f"SELECT * FROM {table}"
        params = []

        if conditions:
            where_clause = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            query += f" WHERE {where_clause}"
            params = list(conditions.values())

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update(self, table, id_value, data, id_column='id'):
        """Update a record"""
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = ?"
        self.cursor.execute(query, list(data.values()) + [id_value])
        self.connection.commit()
        return self.cursor.rowcount

    def delete(self, table, id_value, id_column='id'):
        """Delete a record"""
        query = f"DELETE FROM {table} WHERE {id_column} = ?"
        self.cursor.execute(query, (id_value,))
        self.connection.commit()
        return self.cursor.rowcount

    def execute_query(self, query, params=None):
        """Execute a raw query"""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.connection.commit()
        return self.cursor

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    # ============================================================
    # Helper methods for common operations
    # ============================================================

    def save_module(self, name, module_type, code, author=None, description=None, user_id=None):
        """Save a module to the database"""
        data = {
            'name': name,
            'type': module_type,
            'code': code,
            'status': 'stopped',
            'author': author,
            'description': description,
            'user_id': user_id,
            'version': '1.0.0'
        }
        return self.insert('modules', data)

    def update_module_status(self, module_id, status):
        """Update module status"""
        return self.update('modules', module_id, {'status': status})

    def save_trade(self, symbol, trade_type, entry_price, quantity, module_id=None, user_id=None):
        """Save a trade"""
        data = {
            'symbol': symbol,
            'type': trade_type,
            'entry_price': entry_price,
            'quantity': quantity,
            'status': 'open',
            'module_id': module_id,
            'user_id': user_id
        }
        return self.insert('trades', data)

    def close_trade(self, trade_id, exit_price, pnl):
        """Close a trade"""
        return self.update('trades', trade_id, {
            'exit_price': exit_price,
            'pnl': pnl,
            'status': 'closed',
            'closed_at': datetime.now().isoformat()
        })

    def save_log(self, level, message, source=None, details=None):
        """Save a log entry"""
        data = {
            'level': level,
            'message': message,
            'source': source,
            'details': json.dumps(details) if details else None
        }
        return self.insert('logs', data)

    def save_backtest(self, module_id, symbol, results, user_id=None):
        """Save backtest results"""
        data = {
            'module_id': module_id,
            'symbol': symbol,
            'start_date': results.get('start_date'),
            'end_date': results.get('end_date'),
            'initial_capital': results.get('initial_capital', 100000),
            'final_equity': results.get('final_equity', 0),
            'return_percent': results.get('return_percent', 0),
            'win_rate': results.get('win_rate', 0),
            'total_trades': results.get('total_trades', 0),
            'results_json': json.dumps(results),
            'user_id': user_id
        }
        return self.insert('backtests', data)

db = Database()

def get_db():
    """Get the global database instance"""
    if not db.connection:
        db.connect()
    return db

def init_db():
    """Initialize the database"""
    db.connect()
    print("✅ Database initialized")
    return db

def close_db():
    """Close the database connection"""
    db.close()
    print("✅ Database closed")
