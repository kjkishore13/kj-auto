# ============================================================
# KJs TRD Trading Terminal - Logger Utility
# ============================================================

from datetime import datetime
import os
import json

class Logger:
    """Central logging utility for the platform."""

    def __init__(self, log_file=None, log_level='INFO'):
        self.log_level = log_level
        self.log_file = log_file or 'logs/kjs_trd.log'
        self.levels = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3,
            'CRITICAL': 4
        }

        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self._log("INFO", "Logger initialized")

    def debug(self, message):
        """Log a debug message."""
        self._log("DEBUG", message)

    def info(self, message):
        """Log an info message."""
        self._log("INFO", message)

    def warning(self, message):
        """Log a warning message."""
        self._log("WARNING", message)

    def error(self, message):
        """Log an error message."""
        self._log("ERROR", message)

    def critical(self, message):
        """Log a critical message."""
        self._log("CRITICAL", message)

    def _log(self, level, message):
        """Internal log method."""
        if self.levels.get(level, 0) < self.levels.get(self.log_level, 0):
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"

        print(log_entry)

        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"[ERROR] Failed to write log: {str(e)}")

    def set_level(self, level):
        """Set the log level."""
        if level in self.levels:
            self.log_level = level
            self.info(f"Log level set to: {level}")

    def get_logs(self, lines=100):
        """Get recent logs."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:]
        except Exception as e:
            return [f"Error reading logs: {str(e)}"]

        return []

    def clear_logs(self):
        """Clear all logs."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'w') as f:
                    f.write('')
                self.info("Logs cleared")
                return True
        except Exception as e:
            self.error(f"Failed to clear logs: {str(e)}")

        return False

logger = Logger()

def get_logger():
    """Get the global logger instance."""
    return logger
