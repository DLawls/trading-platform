#!/usr/bin/env python3
"""
Alpaca Data Collector Orchestrator
Runs all Alpaca data collection modules with unified logging and error handling.
"""

import yaml
import logging
import sys
from pathlib import Path
from datetime import datetime
import traceback
from typing import Dict, List, Any

# Import our ingest modules
from . import ohlcv, events

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'alpaca_data_collection_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """Load configuration files"""
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_sources_config():
    """Load sources configuration"""
    sources_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
    with open(sources_path, 'r') as f:
        return yaml.safe_load(f)

def check_api_keys():
    """Check if Alpaca API keys are configured"""
    try:
        sources_config = load_sources_config()
        alpaca_config = sources_config['alpaca']
        
        api_key = alpaca_config['api_key']
        secret_key = alpaca_config['secret_key']
        
        if api_key == 'YOUR_ALPACA_API_KEY' or secret_key == 'YOUR_ALPACA_SECRET':
            return False, "Alpaca API keys not configured. Please update config/sources.yaml"
        
        return True, "API keys configured"
        
    except Exception as e:
        return False, f"Error checking API keys: {str(e)}"

def run_collection_module(module_name: str, module_func, logger: logging.Logger) -> Dict[str, Any]:
    """Run a single collection module with error handling"""
    start_time = datetime.now()
    logger.info(f"🚀 Starting {module_name} collection...")
    
    try:
        success = module_func()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if success:
            logger.info(f"✅ {module_name} completed successfully in {duration:.2f}s")
            return {
                'status': 'success',
                'duration': duration,
                'error': None
            }
        else:
            logger.error(f"❌ {module_name} completed with errors in {duration:.2f}s")
            return {
                'status': 'partial_failure',
                'duration': duration,
                'error': 'Module reported failure'
            }
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        error_msg = f"Exception in {module_name}: {str(e)}"
        logger.error(f"💥 {error_msg} (duration: {duration:.2f}s)")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            'status': 'error',
            'duration': duration,
            'error': error_msg
        }

def main():
    """Main orchestrator function"""
    logger = setup_logging()
    logger.info("🤖 Starting Alpaca Data Collection Orchestrator")
    logger.info(f"📅 Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API keys first
    keys_ok, keys_msg = check_api_keys()
    if not keys_ok:
        logger.error(f"❌ {keys_msg}")
        logger.error("Please configure your Alpaca API keys in config/sources.yaml")
        logger.error("Get your API keys from: https://app.alpaca.markets/")
        return False
    
    logger.info(f"🔑 {keys_msg}")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("📋 Configuration loaded successfully")
        
        # Collection results
        results = {}
        
        # Define collection modules to run
        collection_modules = [
            ('OHLCV', ohlcv.collect_ohlcv),
            ('Events', events.collect_events),
        ]
        
        logger.info(f"📊 Running {len(collection_modules)} collection modules...")
        
        # Run each collection module
        for module_name, module_func in collection_modules:
            results[module_name] = run_collection_module(module_name, module_func, logger)
        
        # Calculate overall success
        successful_modules = sum(1 for result in results.values() if result['status'] == 'success')
        total_modules = len(results)
        success_rate = (successful_modules / total_modules) * 100
        
        # Summary report
        total_duration = sum(result['duration'] for result in results.values())
        logger.info(f"\n{'='*60}")
        logger.info(f"📈 ALPACA DATA COLLECTION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"📊 Success Rate: {successful_modules}/{total_modules} ({success_rate:.1f}%)")
        logger.info(f"⏱️  Total Duration: {total_duration:.2f}s")
        logger.info(f"📅 Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Detailed results
        for module_name, result in results.items():
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            logger.info(f"{status_emoji} {module_name}: {result['status']} ({result['duration']:.2f}s)")
            if result['error']:
                logger.info(f"   Error: {result['error']}")
        
        logger.info(f"{'='*60}")
        
        # Determine overall success
        overall_success = success_rate >= 80  # 80% success rate threshold
        
        if overall_success:
            logger.info("🎉 Alpaca data collection completed successfully!")
        else:
            logger.warning("⚠️  Alpaca data collection completed with some failures")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"💥 Critical error in orchestrator: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 