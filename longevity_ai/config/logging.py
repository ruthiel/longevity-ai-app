"""
Logging configuration for the Longevity AI application.
Supports JSON and console logging with proper formatting.
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

import structlog

from longevity_ai.config.settings import get_settings


def setup_logging(level: str = None, format_type: str = None) -> None:
    """
    Setup application logging configuration.
    
    Args:
        level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Override format type (json, text, console)
    """
    settings = get_settings()
    
    # Use overrides or settings
    log_level = level or settings.log_level
    log_format = format_type or settings.log_format
    
    # Create logs directory if using file logging
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure based on format type
    if log_format == "json":
        _setup_json_logging(log_level, settings.log_file)
    elif log_format == "console":
        _setup_console_logging(log_level, settings.log_file)
    else:  # text
        _setup_text_logging(log_level, settings.log_file)
    
    # Set specific loggers to appropriate levels
    _configure_third_party_loggers()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "level": log_level,
            "format": log_format,
            "environment": settings.environment,
            "app_version": settings.app_version,
        }
    )


def _setup_json_logging(level: str, log_file: str = None) -> None:
    """Setup structured JSON logging."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handlers = ["console"]
    if log_file:
        handlers.append("file")
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "json",
                "stream": sys.stdout,
            }
        },
        "root": {
            "level": level,
            "handlers": handlers,
        }
    }
    
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "json",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    
    logging.config.dictConfig(config)


def _setup_console_logging(level: str, log_file: str = None) -> None:
    """Setup pretty console logging for development."""
    
    handlers = ["console"]
    if log_file:
        handlers.append("file")
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "file": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)-30s | %(filename)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "console",
                "stream": sys.stdout,
            }
        },
        "root": {
            "level": level,
            "handlers": handlers,
        }
    }
    
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "file", 
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    
    logging.config.dictConfig(config)


def _setup_text_logging(level: str, log_file: str = None) -> None:
    """Setup simple text logging."""
    
    handlers = ["console"]
    if log_file:
        handlers.append("file")
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "simple",
                "stream": sys.stdout,
            }
        },
        "root": {
            "level": level,
            "handlers": handlers,
        }
    }
    
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "simple",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    
    logging.config.dictConfig(config)


def _configure_third_party_loggers() -> None:
    """Configure third-party library loggers."""
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("supabase").setLevel(logging.INFO)
    logging.getLogger("langchain").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


# Context manager for temporary log level changes
class LogLevel:
    """Context manager to temporarily change log level."""
    
    def __init__(self, logger_name: str, level: str):
        self.logger = logging.getLogger(logger_name)
        self.original_level = self.logger.level
        self.new_level = getattr(logging, level.upper())
    
    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)