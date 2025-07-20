#!/usr/bin/env python3
"""
Financial Data Collector Orchestrator
Runs all data collection modules with unified logging and error handling.
"""

import yaml
import logging
import sys
from pathlib import Path
from datetime import datetime
import traceback
from typing import Dict, List, Any

# Import our ingest modules
from . import ohlcv, macro, fundamentals, events

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'data_collection_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """Load configuration files"""
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_collection_module(module_name: str, module_func, logger: logging.Logger) -> Dict[str, Any]:
    """Run a single collection module with error handling"""
    start_time = datetime.now()
    logger.info(f"Starting {module_name} collection...")
    
    try:
        module_func()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"✅ {module_name} completed successfully in {duration:.2f}s")
        return {
            'status': 'success',
            'duration': duration,
            'error': None
        }
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        error_msg = f"❌ {module_name} failed after {duration:.2f}s: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            'status': 'error',
            'duration': duration,
            'error': str(e)
        }

def generate_collection_report(results: Dict[str, Dict], logger: logging.Logger):
    """Generate a summary report of the collection run"""
    logger.info("\n" + "="*50)
    logger.info("📊 DATA COLLECTION SUMMARY REPORT")
    logger.info("="*50)
    
    total_modules = len(results)
    successful_modules = sum(1 for r in results.values() if r['status'] == 'success')
    failed_modules = total_modules - successful_modules
    total_duration = sum(r['duration'] for r in results.values())
    
    logger.info(f"Total modules: {total_modules}")
    logger.info(f"Successful: {successful_modules}")
    logger.info(f"Failed: {failed_modules}")
    logger.info(f"Total duration: {total_duration:.2f}s")
    
    if failed_modules > 0:
        logger.warning("Failed modules:")
        for module, result in results.items():
            if result['status'] == 'error':
                logger.warning(f"  - {module}: {result['error']}")
    
    logger.info("="*50)

def main():
    """Main orchestrator function"""
    logger = setup_logging()
    config = load_config()
    
    logger.info("🚀 Starting Financial Data Collection Orchestrator")
    logger.info(f"Configuration loaded: {len(config)} data types configured")
    
    # Define collection modules
    collection_modules = {
        'OHLCV Data': ohlcv.main,
        'Macro Data': macro.main,
        'Fundamentals': fundamentals.main,
        'Events': events.main
    }
    
    results = {}
    
    # Run each collection module
    for module_name, module_func in collection_modules.items():
        result = run_collection_module(module_name, module_func, logger)
        results[module_name] = result
    
    # Generate summary report
    generate_collection_report(results, logger)
    
    # Exit with error code if any modules failed
    failed_count = sum(1 for r in results.values() if r['status'] == 'error')
    if failed_count > 0:
        logger.error(f"Collection completed with {failed_count} failures")
        sys.exit(1)
    else:
        logger.info("🎉 All data collection modules completed successfully!")

if __name__ == '__main__':
    main() 