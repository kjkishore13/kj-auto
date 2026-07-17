# ============================================================
# KJs TRD Trading Terminal - Configuration
# ============================================================

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_URI = 'sqlite:///kjs_trd.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///kjs_trd.db'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# ============================================================
# App Settings
# ============================================================

APP_SETTINGS = {
    'APP_NAME': 'KJs TRD Trading Terminal',
    'APP_VERSION': '1.0.0',
    'AUTHOR': 'KJ',
    'DESCRIPTION': 'Personal Trading Operating System',
}

# ============================================================
# Broker Settings
# ============================================================

BROKER_SETTINGS = {
    'default_broker': 'dhan',
    'brokers': {
        'dhan': {
            'name': 'Dhan',
            'api_url': 'https://api.dhan.co',
            'enabled': True
        },
        'zerodha': {
            'name': 'Zerodha',
            'api_url': 'https://api.kite.trade',
            'enabled': False
        },
        'angel': {
            'name': 'Angel One',
            'api_url': 'https://apiconnect.angelbroking.com',
            'enabled': False
        }
    }
}

# ============================================================
# Notification Settings
# ============================================================

NOTIFICATION_SETTINGS = {
    'channels': {
        'telegram': {
            'enabled': True,
            'bot_token': os.environ.get('TELEGRAM_BOT_TOKEN') or 'YOUR_BOT_TOKEN',
            'chat_id': os.environ.get('TELEGRAM_CHAT_ID') or 'YOUR_CHAT_ID'
        },
        'email': {
            'enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': os.environ.get('EMAIL_USERNAME') or 'your-email@gmail.com',
            'password': os.environ.get('EMAIL_PASSWORD') or 'your-password'
        },
        'whatsapp': {
            'enabled': False
        }
    }
}

# ============================================================
# Market Data Settings
# ============================================================

MARKET_DATA_SETTINGS = {
    'providers': {
        'yahoo': {
            'enabled': True,
            'base_url': 'https://query1.finance.yahoo.com'
        },
        'alpha_vantage': {
            'enabled': False,
            'api_key': os.environ.get('ALPHA_VANTAGE_KEY') or 'YOUR_API_KEY',
            'base_url': 'https://www.alphavantage.co'
        },
        'dhan': {
            'enabled': True,
            'api_url': 'https://api.dhan.co'
        }
    },
    'default_symbol': 'NIFTY 50',
    'default_timeframe': '15m',
    'cache_duration': 60
}

# ============================================================
# Module Settings
# ============================================================

MODULE_SETTINGS = {
    'module_directory': 'modules/',
    'allowed_types': ['strategy', 'indicator', 'screener', 'alert', 'automation'],
    'max_running_modules': 10,
    'timeout_seconds': 30
}

# ============================================================
# Database Settings
# ============================================================

DATABASE_SETTINGS = {
    'type': 'sqlite',
    'path': 'database/kjs_trd.db',
    'backup_enabled': True,
    'backup_interval_hours': 24
}

# ============================================================
# Logging Settings
# ============================================================

LOGGING_SETTINGS = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/kjs_trd.log',
    'max_size_mb': 10,
    'backup_count': 5
}
