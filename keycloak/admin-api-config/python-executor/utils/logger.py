"""
Logging Configuration
Centralized logging setup for all components
"""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Setup logger with consistent formatting."""
    
    if format_string is None:
        format_string = (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


class PadminiLogger:
    """Enhanced logger with emojis for better readability."""
    
    def __init__(self, name: str):
        self.logger = setup_logger(name)
    
    def info(self, message: str):
        """Info message with ✅ emoji."""
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        """Warning message with ⚠️ emoji."""
        self.logger.warning(f"⚠️  {message}")
    
    def error(self, message: str):
        """Error message with ❌ emoji."""
        self.logger.error(f"❌ {message}")
    
    def debug(self, message: str):
        """Debug message with 🔍 emoji."""
        self.logger.debug(f"🔍 {message}")
    
    def success(self, message: str):
        """Success message with 🎉 emoji."""
        self.logger.info(f"🎉 {message}")
    
    def start_operation(self, operation: str):
        """Start operation message with 🚀 emoji."""
        self.logger.info(f"🚀 Starting {operation}...")
    
    def skip_operation(self, operation: str, reason: str):
        """Skip operation message with ⏭️ emoji."""
        self.logger.info(f"⏭️  {operation} skipped: {reason}")
    
    def rollback_operation(self, operation: str):
        """Rollback operation message with 🔄 emoji."""
        self.logger.info(f"🔄 Rolling back {operation}...")
