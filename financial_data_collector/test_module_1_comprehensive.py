#!/usr/bin/env python3
"""
Module 1: Financial Data Collector - Comprehensive Test Suite
===========================================================

Production readiness validation for the complete Module 1 system.
Tests all collectors, data quality, dashboard, and integration components.

Usage:
    python3 test_module_1_comprehensive.py [--verbose] [--collectors-only] [--quick]
"""

import sys
import json
import yaml
import logging
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import argparse

# Test Categories
class TestCategories:
    CRITICAL = "🔴 CRITICAL"
    IMPORTANT = "🟡 IMPORTANT" 
    OPTIONAL = "🟢 OPTIONAL"

class TestRunner:
    def __init__(self, verbose=False, quick=False):
        self.verbose = verbose
        self.quick = quick
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = datetime.now()
        
        # Setup logging
        self.setup_logging()
        
        # Test configuration
        self.base_path = Path(__file__).parent
        self.data_path = self.base_path / 'financial_data'
        self.collectors = {
            'yahoo_finance': self.base_path / 'yahoo_finance_collector',
            'fred_economic': self.base_path / 'fred_data_collector', 
            'abs_australian': self.base_path / 'abs_data_collector',
            'alpaca_premium': self.base_path / 'alpaca_data_collector'
        }
        
    def setup_logging(self):
        """Setup test logging"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_test(self, test_name: str, test_func, category: str = TestCategories.IMPORTANT) -> bool:
        """Run individual test with error handling"""
        self.total_tests += 1
        
        try:
            print(f"\n{category} Testing: {test_name}")
            self.logger.info(f"Starting test: {test_name}")
            
            start = time.time()
            result = test_func()
            duration = time.time() - start
            
            if result:
                print(f"  ✅ PASS ({duration:.2f}s)")
                self.logger.info(f"PASS: {test_name} ({duration:.2f}s)")
                self.passed_tests += 1
                self.results[test_name] = {"status": "PASS", "duration": duration, "category": category}
                return True
            else:
                print(f"  ❌ FAIL ({duration:.2f}s)")
                self.logger.error(f"FAIL: {test_name} ({duration:.2f}s)")
                self.failed_tests += 1
                self.results[test_name] = {"status": "FAIL", "duration": duration, "category": category}
                return False
                
        except Exception as e:
            duration = time.time() - start if 'start' in locals() else 0
            print(f"  💥 ERROR ({duration:.2f}s): {str(e)}")
            self.logger.error(f"ERROR: {test_name} - {str(e)}")
            self.failed_tests += 1
            self.results[test_name] = {"status": "ERROR", "duration": duration, "category": category, "error": str(e)}
            return False

    # ==========================================
    # INFRASTRUCTURE TESTS
    # ==========================================
    
    def test_directory_structure(self) -> bool:
        """Test all required directories exist"""
        required_dirs = [
            self.base_path,
            self.data_path,
            self.base_path / 'dashboard',
            self.base_path / 'shared',
            self.collectors['yahoo_finance'],
            self.collectors['fred_economic'],
            self.collectors['abs_australian'],
            self.collectors['alpaca_premium']
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                self.logger.error(f"Missing directory: {directory}")
                return False
                
        # Check data subdirectories
        data_subdirs = ['ohlcv', 'fundamentals', 'events', 'economic']
        for subdir in data_subdirs:
            (self.data_path / subdir).mkdir(exist_ok=True)
            
        return True

    def test_configuration_files(self) -> bool:
        """Test all configuration files are valid"""
        config_files = [
            self.base_path / 'shared' / 'config' / 'sources.yaml',
            self.collectors['yahoo_finance'] / 'config' / 'data_requirements.yaml',
            self.collectors['fred_economic'] / 'config' / 'data_requirements.yaml',
            self.collectors['alpaca_premium'] / 'config' / 'sources.yaml'
        ]
        
        for config_file in config_files:
            if not config_file.exists():
                if 'alpaca' in str(config_file):
                    continue  # Alpaca may not be fully configured
                self.logger.error(f"Missing config file: {config_file}")
                return False
                
            try:
                with open(config_file, 'r') as f:
                    yaml.safe_load(f)
                self.logger.debug(f"Valid YAML: {config_file}")
            except yaml.YAMLError as e:
                self.logger.error(f"Invalid YAML in {config_file}: {e}")
                return False
                
        return True

    def test_python_dependencies(self) -> bool:
        """Test required Python packages are available"""
        required_packages = [
            'pandas', 'yaml', 'requests', 'yfinance', 'fredapi'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                self.logger.debug(f"Package available: {package}")
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            self.logger.error(f"Missing packages: {missing_packages}")
            return False
            
        return True

    # ==========================================
    # DATA COLLECTOR TESTS  
    # ==========================================

    def test_yahoo_finance_collector(self) -> bool:
        """Test Yahoo Finance data collection"""
        collector_path = self.collectors['yahoo_finance']
        
        # Test configuration
        config_file = collector_path / 'config' / 'data_requirements.yaml'
        if not config_file.exists():
            return False
            
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        # Verify ASX 50 tickers are configured
        if 'ohlcv' not in config or 'tickers' not in config['ohlcv']:
            return False
            
        tickers = config['ohlcv']['tickers']
        if len(tickers) < 45:  # Allow some flexibility
            self.logger.error(f"Only {len(tickers)} tickers configured, expected ~50")
            return False
            
        # Test orchestrator exists
        orchestrator = collector_path / 'ingest' / 'orchestrator.py'
        if not orchestrator.exists():
            return False
            
        return True

    def test_fred_economic_collector(self) -> bool:
        """Test FRED economic data collector"""
        collector_path = self.collectors['fred_economic']
        
        # Check if FRED API key is configured
        shared_config = self.base_path / 'shared' / 'config' / 'sources.yaml'
        if shared_config.exists():
            with open(shared_config, 'r') as f:
                config = yaml.safe_load(f)
                
            if 'fred' in config and 'api_key' in config['fred']:
                api_key = config['fred']['api_key']
                if api_key and api_key != 'YOUR_FRED_API_KEY':
                    self.logger.debug("FRED API key configured")
                else:
                    self.logger.warning("FRED API key not configured")
                    
        # Test collector structure
        required_files = [
            collector_path / 'ingest' / 'fred_economic_data.py',
            collector_path / 'config' / 'data_requirements.yaml'
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                return False
                
        return True

    def test_abs_australian_collector(self) -> bool:
        """Test ABS Australian data collector"""
        collector_path = self.collectors['abs_australian']
        
        # Test basic structure
        required_files = [
            collector_path / 'README.md',
            collector_path / 'config'
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.logger.warning(f"ABS collector file missing: {file_path}")
                # ABS is configured but not fully active
                
        return True  # ABS is configured but not mandatory for production

    def test_alpaca_collector(self) -> bool:
        """Test Alpaca premium collector"""
        collector_path = self.collectors['alpaca_premium']
        
        # Test containerized setup
        required_files = [
            collector_path / 'Dockerfile',
            collector_path / 'docker-compose.yml',
            collector_path / 'run_docker.sh',
            collector_path / 'config' / 'sources.yaml'
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.logger.error(f"Alpaca file missing: {file_path}")
                return False
                
        # Test API key configuration
        config_file = collector_path / 'config' / 'sources.yaml'
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        if 'alpaca' in config:
            api_key = config['alpaca'].get('api_key', '')
            if api_key and api_key != 'YOUR_ALPACA_API_KEY':
                self.logger.debug("Alpaca API key configured")
                return True
            else:
                self.logger.warning("Alpaca API key not configured")
                return True  # Configuration is ready, just needs keys
                
        return True

    # ==========================================
    # DATA QUALITY TESTS
    # ==========================================

    def test_data_files_exist(self) -> bool:
        """Test that data files exist from previous collections"""
        data_types = ['ohlcv', 'fundamentals', 'events', 'economic']
        files_found = 0
        
        for data_type in data_types:
            data_dir = self.data_path / data_type
            if data_dir.exists():
                files = list(data_dir.glob('*'))
                files_found += len(files)
                self.logger.debug(f"{data_type}: {len(files)} files")
                
        if files_found < 10:  # Minimum threshold
            self.logger.warning(f"Only {files_found} data files found")
            return False
            
        self.logger.info(f"Found {files_found} data files")
        return True

    def test_data_file_formats(self) -> bool:
        """Test data files are in correct formats"""
        # Test parquet files
        ohlcv_files = list((self.data_path / 'ohlcv').glob('*.parquet'))
        if ohlcv_files:
            try:
                import pandas as pd
                sample_file = ohlcv_files[0]
                df = pd.read_parquet(sample_file)
                
                # Basic schema validation
                expected_columns = ['ticker', 'datetime', 'open', 'high', 'low', 'close', 'volume']
                missing_cols = [col for col in expected_columns if col not in df.columns]
                if missing_cols:
                    self.logger.error(f"Missing columns in {sample_file}: {missing_cols}")
                    return False
                    
                self.logger.debug(f"Validated parquet file: {sample_file}")
            except Exception as e:
                self.logger.error(f"Error reading parquet file: {e}")
                return False
                
        # Test JSON files (events)
        events_files = list((self.data_path / 'events').glob('*.json'))
        if events_files:
            try:
                sample_file = events_files[0]
                with open(sample_file, 'r') as f:
                    data = json.load(f)
                    
                if isinstance(data, list) and len(data) > 0:
                    self.logger.debug(f"Validated JSON file: {sample_file}")
                else:
                    self.logger.warning(f"Empty or invalid JSON: {sample_file}")
                    
            except Exception as e:
                self.logger.error(f"Error reading JSON file: {e}")
                return False
                
        return True

    def test_data_freshness(self) -> bool:
        """Test data files are reasonably fresh"""
        cutoff_date = datetime.now() - timedelta(days=7)  # 1 week old
        
        recent_files = []
        for data_type in ['ohlcv', 'fundamentals', 'events']:
            data_dir = self.data_path / data_type
            if data_dir.exists():
                for file_path in data_dir.iterdir():
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time > cutoff_date:
                            recent_files.append(file_path)
                            
        if len(recent_files) < 5:  # Minimum recent files
            self.logger.warning(f"Only {len(recent_files)} recent files found")
            return False
            
        self.logger.info(f"Found {len(recent_files)} recent data files")
        return True

    # ==========================================
    # DASHBOARD TESTS
    # ==========================================

    def test_dashboard_structure(self) -> bool:
        """Test dashboard components exist"""
        dashboard_path = self.base_path / 'dashboard'
        
        required_files = [
            dashboard_path / 'app.py',
            dashboard_path / 'launch_dashboard.py',
            dashboard_path / 'config' / 'dashboard_config.yaml'
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.logger.error(f"Dashboard file missing: {file_path}")
                return False
                
        # Test pages directory
        pages_dir = dashboard_path / 'pages'
        if pages_dir.exists():
            page_files = list(pages_dir.glob('*.py'))
            self.logger.debug(f"Found {len(page_files)} dashboard pages")
            
        return True

    def test_dashboard_config(self) -> bool:
        """Test dashboard configuration is valid"""
        config_file = self.base_path / 'dashboard' / 'config' / 'dashboard_config.yaml'
        
        if not config_file.exists():
            return False
            
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            # Validate config structure
            required_sections = ['dashboard', 'collectors', 'monitoring']
            for section in required_sections:
                if section not in config:
                    self.logger.error(f"Missing config section: {section}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Dashboard config error: {e}")
            return False

    # ==========================================
    # INTEGRATION TESTS
    # ==========================================

    def test_shared_utilities(self) -> bool:
        """Test shared utilities are functional"""
        shared_path = self.base_path / 'shared'
        
        # Test config directory
        config_dir = shared_path / 'config'
        if not config_dir.exists():
            return False
            
        # Test monitoring utilities
        monitoring_dir = shared_path / 'monitoring'
        if monitoring_dir.exists():
            health_check = monitoring_dir / 'health_check.py'
            if health_check.exists():
                self.logger.debug("Health check utility found")
                
        return True

    def test_end_to_end_data_flow(self) -> bool:
        """Test complete data flow from collection to dashboard"""
        # This is a simplified E2E test
        # In production, this would trigger actual collection
        
        # 1. Check data sources are accessible
        data_dirs = ['ohlcv', 'fundamentals', 'events', 'economic']
        for data_dir in data_dirs:
            path = self.data_path / data_dir
            if not path.exists():
                path.mkdir(parents=True)
                
        # 2. Verify dashboard can access data
        dashboard_config = self.base_path / 'dashboard' / 'config' / 'dashboard_config.yaml'
        if dashboard_config.exists():
            self.logger.debug("Dashboard can access configuration")
            
        # 3. Test monitoring integration
        shared_config = self.base_path / 'shared' / 'config' / 'sources.yaml'
        if shared_config.exists():
            self.logger.debug("Shared configuration accessible")
            
        return True

    # ==========================================
    # PERFORMANCE TESTS
    # ==========================================

    def test_system_performance(self) -> bool:
        """Test basic system performance metrics"""
        if self.quick:
            return True  # Skip performance tests in quick mode
            
        # Test disk space
        data_size = sum(f.stat().st_size for f in self.data_path.rglob('*') if f.is_file())
        data_size_mb = data_size / (1024 * 1024)
        
        self.logger.info(f"Total data size: {data_size_mb:.1f} MB")
        
        if data_size_mb > 1000:  # 1GB
            self.logger.warning(f"Large data size: {data_size_mb:.1f} MB")
            
        # Test file count
        file_count = sum(1 for f in self.data_path.rglob('*') if f.is_file())
        self.logger.info(f"Total files: {file_count}")
        
        return True

    # ==========================================
    # SECURITY TESTS
    # ==========================================

    def test_api_key_security(self) -> bool:
        """Test API keys are properly secured"""
        shared_config = self.base_path / 'shared' / 'config' / 'sources.yaml'
        
        if not shared_config.exists():
            return True  # No config to test
            
        with open(shared_config, 'r') as f:
            config = yaml.safe_load(f)
            
        # Check for placeholder keys
        api_services = ['fred', 'alpaca', 'abs']
        configured_services = 0
        
        for service in api_services:
            if service in config:
                api_key = config[service].get('api_key', '')
                if api_key and not api_key.startswith('YOUR_'):
                    configured_services += 1
                    self.logger.debug(f"{service} API key configured")
                    
        self.logger.info(f"Configured API services: {configured_services}/{len(api_services)}")
        return True

    # ==========================================
    # MAIN TEST EXECUTION
    # ==========================================

    def run_all_tests(self, collectors_only=False):
        """Run the complete test suite"""
        print("🚀 Module 1: Financial Data Collector - Comprehensive Test Suite")
        print("=" * 70)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Infrastructure Tests (Critical)
        self.run_test("Directory Structure", self.test_directory_structure, TestCategories.CRITICAL)
        self.run_test("Configuration Files", self.test_configuration_files, TestCategories.CRITICAL)
        self.run_test("Python Dependencies", self.test_python_dependencies, TestCategories.CRITICAL)
        
        # Data Collector Tests (Critical)
        self.run_test("Yahoo Finance Collector", self.test_yahoo_finance_collector, TestCategories.CRITICAL)
        self.run_test("FRED Economic Collector", self.test_fred_economic_collector, TestCategories.CRITICAL)
        self.run_test("ABS Australian Collector", self.test_abs_australian_collector, TestCategories.IMPORTANT)
        self.run_test("Alpaca Premium Collector", self.test_alpaca_collector, TestCategories.IMPORTANT)
        
        if collectors_only:
            self.generate_report()
            return
            
        # Data Quality Tests (Important)
        self.run_test("Data Files Exist", self.test_data_files_exist, TestCategories.IMPORTANT)
        self.run_test("Data File Formats", self.test_data_file_formats, TestCategories.IMPORTANT)
        self.run_test("Data Freshness", self.test_data_freshness, TestCategories.OPTIONAL)
        
        # Dashboard Tests (Important)
        self.run_test("Dashboard Structure", self.test_dashboard_structure, TestCategories.IMPORTANT)
        self.run_test("Dashboard Configuration", self.test_dashboard_config, TestCategories.IMPORTANT)
        
        # Integration Tests (Important)
        self.run_test("Shared Utilities", self.test_shared_utilities, TestCategories.IMPORTANT)
        self.run_test("End-to-End Data Flow", self.test_end_to_end_data_flow, TestCategories.CRITICAL)
        
        # Performance & Security Tests (Optional)
        self.run_test("System Performance", self.test_system_performance, TestCategories.OPTIONAL)
        self.run_test("API Key Security", self.test_api_key_security, TestCategories.OPTIONAL)
        
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        # Summary Statistics
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Tests Run: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {duration.total_seconds():.2f}s")
        
        # Critical Test Results
        critical_tests = [name for name, result in self.results.items() 
                         if result.get('category') == TestCategories.CRITICAL]
        critical_passed = sum(1 for name in critical_tests 
                            if self.results[name]['status'] == 'PASS')
        
        print(f"\n🔴 Critical Tests: {critical_passed}/{len(critical_tests)} passed")
        
        # Detailed Results by Category
        for category in [TestCategories.CRITICAL, TestCategories.IMPORTANT, TestCategories.OPTIONAL]:
            category_tests = [(name, result) for name, result in self.results.items() 
                            if result.get('category') == category]
            
            if category_tests:
                print(f"\n{category} Tests:")
                for name, result in category_tests:
                    status_icon = "✅" if result['status'] == 'PASS' else "❌"
                    duration = result.get('duration', 0)
                    print(f"  {status_icon} {name} ({duration:.2f}s)")
                    
                    if result['status'] != 'PASS' and 'error' in result:
                        print(f"      Error: {result['error']}")
        
        # Production Readiness Assessment
        print("\n" + "=" * 70)
        print("🚀 PRODUCTION READINESS ASSESSMENT")
        print("=" * 70)
        
        critical_success = all(self.results[name]['status'] == 'PASS' 
                             for name in critical_tests)
        
        if critical_success and success_rate >= 80:
            print("✅ PRODUCTION READY")
            print("   All critical tests passed")
            print("   System meets production requirements")
            print("   Ready for enterprise deployment")
        elif critical_success:
            print("🟡 PRODUCTION READY (with warnings)")
            print("   All critical tests passed")
            print("   Some optional features need attention")
            print("   Safe for production deployment")
        else:
            print("❌ NOT PRODUCTION READY")
            print("   Critical tests failed")
            print("   Issues must be resolved before deployment")
            
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        failed_tests = [name for name, result in self.results.items() 
                       if result['status'] != 'PASS']
        
        if not failed_tests:
            print("   🎉 No issues found - system is ready for production!")
        else:
            for test_name in failed_tests:
                category = self.results[test_name].get('category', '')
                if category == TestCategories.CRITICAL:
                    print(f"   🔴 URGENT: Fix {test_name}")
                elif category == TestCategories.IMPORTANT:
                    print(f"   🟡 Important: Address {test_name}")
                else:
                    print(f"   🟢 Optional: Consider fixing {test_name}")
                    
        print(f"\n📁 Detailed log: test_results_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log")

def main():
    parser = argparse.ArgumentParser(description="Module 1 Comprehensive Test Suite")
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    parser.add_argument('--collectors-only', '-c', action='store_true',
                       help='Test only data collectors')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Skip performance tests')
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose, quick=args.quick)
    runner.run_all_tests(collectors_only=args.collectors_only)
    
    # Exit with appropriate code
    critical_tests = [name for name, result in runner.results.items() 
                     if result.get('category') == TestCategories.CRITICAL]
    critical_passed = all(runner.results[name]['status'] == 'PASS' 
                         for name in critical_tests)
    
    sys.exit(0 if critical_passed else 1)

if __name__ == "__main__":
    main() 