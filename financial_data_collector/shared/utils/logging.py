#!/usr/bin/env python3
"""
Shared Logging Utilities
Standardized logging configuration for all financial data collectors.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import yaml
from typing import Optional, Dict, Any

def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    include_file_handler: bool = True,
    include_console_handler: bool = True
) -> logging.Logger:
    """
    Set up standardized logger for collectors
    
    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files (defaults to collector's logs/)
        include_file_handler: Whether to log to file
        include_console_handler: Whether to log to console
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to prevent duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if include_console_handler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if include_file_handler:
        if log_dir is None:
            # Default to logs directory relative to caller
            log_dir = Path.cwd() / 'logs'
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        log_file = log_dir / f"{name.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def load_logging_config(config_path: Path) -> Dict[str, Any]:
    """Load logging configuration from sources.yaml"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config.get('global', {})
    except Exception as e:
        # Fallback to defaults if config can't be loaded
        return {
            'log_level': 'INFO',
            'log_directory': '/tmp/financial_data_collector'
        }

def get_collector_logger(collector_name: str) -> logging.Logger:
    """
    Get a standardized logger for a specific collector
    
    Args:
        collector_name: Name of the collector (e.g., 'yahoo_finance', 'fred')
    
    Returns:
        Configured logger for the collector
    """
    
    # Try to load global config
    shared_config_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
    config = load_logging_config(shared_config_path)
    
    log_level = config.get('log_level', 'INFO')
    log_dir = Path(config.get('log_directory', '/tmp/financial_data_collector'))
    
    # Create collector-specific log directory
    collector_log_dir = log_dir / collector_name
    
    return setup_logger(
        name=f"financial_data_collector.{collector_name}",
        log_level=log_level,
        log_dir=collector_log_dir
    )

def log_collection_start(logger: logging.Logger, collector_name: str, data_type: str):
    """Standard logging for collection start"""
    logger.info("="*60)
    logger.info(f"🚀 Starting {collector_name} - {data_type} Collection")
    logger.info("="*60)

def log_collection_end(logger: logging.Logger, success_count: int, total_count: int, duration: float):
    """Standard logging for collection completion"""
    logger.info("="*60)
    logger.info(f"📊 Collection Summary:")
    logger.info(f"   ✅ Successful: {success_count}/{total_count}")
    logger.info(f"   📈 Success Rate: {success_count/total_count*100:.1f}%")
    logger.info(f"   ⏱️  Duration: {duration:.2f}s")
    logger.info("="*60)

def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any]):
    """Log error with additional context information"""
    logger.error(f"❌ Error: {str(error)}")
    for key, value in context.items():
        logger.error(f"   {key}: {value}")
    logger.error(f"   Exception Type: {type(error).__name__}") 