#!/usr/bin/env python3
"""
Data Collection Scheduler
Provides scheduling capabilities for automated data collection.
"""

import yaml
import logging
import time
import schedule
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Import our modules
from . import orchestrator, data_quality

def setup_logging():
    """Setup logging for scheduler"""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'scheduler_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_schedule_config():
    """Load scheduling configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'cron_schedule.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_data_collection():
    """Run the full data collection process"""
    logger = logging.getLogger(__name__)
    logger.info("🔄 Starting scheduled data collection...")
    
    try:
        orchestrator.main()
        logger.info("✅ Scheduled data collection completed successfully")
    except Exception as e:
        logger.error(f"❌ Scheduled data collection failed: {e}")

def run_quality_check():
    """Run data quality monitoring"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Starting scheduled quality check...")
    
    try:
        data_quality.main()
        logger.info("✅ Scheduled quality check completed successfully")
    except Exception as e:
        logger.error(f"❌ Scheduled quality check failed: {e}")

def setup_schedules(schedule_config: Dict[str, Any], logger: logging.Logger):
    """Setup scheduled jobs based on configuration"""
    
    # Data collection schedules
    collection_schedule = schedule_config.get('data_collection', {})
    
    # Daily collection (default: 6:00 AM)
    daily_time = collection_schedule.get('daily', '06:00')
    schedule.every().day.at(daily_time).do(run_data_collection)
    logger.info(f"📅 Scheduled daily data collection at {daily_time}")
    
    # Hourly collection (if enabled)
    if collection_schedule.get('hourly', False):
        schedule.every().hour.do(run_data_collection)
        logger.info("📅 Scheduled hourly data collection")
    
    # Market hours collection (if enabled)
    market_hours = collection_schedule.get('market_hours', False)
    if market_hours:
        # Schedule for ASX market hours (10:00 AM - 4:00 PM AEST)
        schedule.every().day.at("10:00").do(run_data_collection)
        schedule.every().day.at("12:00").do(run_data_collection)
        schedule.every().day.at("14:00").do(run_data_collection)
        schedule.every().day.at("16:00").do(run_data_collection)
        logger.info("📅 Scheduled market hours data collection")
    
    # Quality check schedules
    quality_schedule = schedule_config.get('quality_check', {})
    
    # Daily quality check (default: 7:00 AM)
    quality_time = quality_schedule.get('daily', '07:00')
    schedule.every().day.at(quality_time).do(run_quality_check)
    logger.info(f"📅 Scheduled daily quality check at {quality_time}")

def run_scheduler():
    """Main scheduler loop"""
    logger = setup_logging()
    schedule_config = load_schedule_config()
    
    logger.info("⏰ Starting Data Collection Scheduler")
    logger.info("Press Ctrl+C to stop the scheduler")
    
    # Setup scheduled jobs
    setup_schedules(schedule_config, logger)
    
    # Run initial collection if requested
    if schedule_config.get('run_on_startup', False):
        logger.info("🚀 Running initial data collection on startup...")
        run_data_collection()
    
    # Main scheduler loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("⏹️  Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")

def run_once():
    """Run data collection once (for testing or manual execution)"""
    logger = setup_logging()
    logger.info("🔄 Running one-time data collection...")
    run_data_collection()

def run_quality_once():
    """Run quality check once (for testing or manual execution)"""
    logger = setup_logging()
    logger.info("🔍 Running one-time quality check...")
    run_quality_check()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'once':
            run_once()
        elif command == 'quality':
            run_quality_once()
        elif command == 'scheduler':
            run_scheduler()
        else:
            print("Usage: python scheduler.py [once|quality|scheduler]")
            print("  once: Run data collection once")
            print("  quality: Run quality check once")
            print("  scheduler: Start the scheduler (default)")
    else:
        run_scheduler() 