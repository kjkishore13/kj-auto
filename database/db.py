# ============================================================
# KJs TRD Trading Terminal - Database Connection
# ============================================================

from .models import Database
import os

_db_instance = None

def get_db():
    """Get the database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.connect()
    return _db_instance

def init_db(db_path=None):
    """Initialize the database."""
    global _db_instance

    if db_path:
        _db_instance = Database(db_path)
    else:
        _db_instance = Database()

    _db_instance.connect()
    print("✅ Database initialized successfully")
    return _db_instance

def close_db():
    """Close the database connection."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
        print("✅ Database closed")

def reset_db():
    """Reset the database (drop and recreate all tables)."""
    global _db_instance

    if _db_instance:
        _db_instance.close()

    db_path = 'database/kjs_trd.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Removed existing database: {db_path}")

    _db_instance = Database(db_path)
    _db_instance.connect()
    print("✅ Database reset successfully")
    return _db_instance

def backup_db():
    """Create a backup of the database."""
    import shutil
    from datetime import datetime

    db_path = 'database/kjs_trd.db'
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False

    backup_dir = 'database/backups'
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'kjs_trd_{timestamp}.db')

    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return True

db = get_db()
