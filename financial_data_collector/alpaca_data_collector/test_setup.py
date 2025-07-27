#!/usr/bin/env python3
"""
Alpaca Data Collector Test Setup
Tests configuration and setup without requiring API keys.
"""

import sys
from pathlib import Path
import yaml
import json

def test_configuration_files():
    """Test that all configuration files are valid and complete"""
    print("🧪 Testing Alpaca Collector Configuration...")
    
    # Test data requirements
    try:
        config_path = Path(__file__).parent / 'config' / 'data_requirements.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'ohlcv' in config, "OHLCV configuration missing"
        assert 'events' in config, "Events configuration missing"
        assert 'us_stocks' in config['ohlcv'], "US stocks configuration missing"
        
        print("✅ data_requirements.yaml: Valid")
        
    except Exception as e:
        print(f"❌ data_requirements.yaml: {e}")
        return False
    
    # Test sources configuration  
    try:
        sources_path = Path(__file__).parent / 'config' / 'sources.yaml'
        with open(sources_path, 'r') as f:
            sources = yaml.safe_load(f)
        
        assert 'alpaca' in sources, "Alpaca configuration missing"
        assert 'api_key' in sources['alpaca'], "API key field missing"
        assert 'secret_key' in sources['alpaca'], "Secret key field missing"
        
        print("✅ sources.yaml: Valid")
        
    except Exception as e:
        print(f"❌ sources.yaml: {e}")
        return False
        
    # Test schedule configuration
    try:
        schedule_path = Path(__file__).parent / 'config' / 'cron_schedule.yaml'
        with open(schedule_path, 'r') as f:
            schedule = yaml.safe_load(f)
        
        assert 'daily_collection' in schedule, "Daily collection schedule missing"
        assert 'settings' in schedule, "Schedule settings missing"
        
        print("✅ cron_schedule.yaml: Valid")
        
    except Exception as e:
        print(f"❌ cron_schedule.yaml: {e}")
        return False
    
    return True

def test_import_structure():
    """Test that all Python modules can be imported"""
    print("\n🧪 Testing Python Module Structure...")
    
    try:
        # Test ingest modules can be imported
        from ingest import ohlcv, events
        print("✅ Ingest modules: Importable")
        
        # Test main functions exist
        assert hasattr(ohlcv, 'collect_ohlcv'), "collect_ohlcv function missing"
        assert hasattr(events, 'collect_events'), "collect_events function missing"
        print("✅ Main functions: Available")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Function missing: {e}")
        return False
    
    return True

def test_directory_structure():
    """Test that required directories exist"""
    print("\n🧪 Testing Directory Structure...")
    
    base_path = Path(__file__).parent
    required_dirs = [
        'config',
        'ingest', 
        'logs'
    ]
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/: Exists")
        else:
            print(f"❌ {dir_name}/: Missing")
            return False
    
    return True

def test_shared_schema_access():
    """Test access to shared validation schemas"""
    print("\n🧪 Testing Shared Schema Access...")
    
    try:
        # Test OHLCV schema access
        schema_path = Path(__file__).parent.parent / 'yahoo_finance_collector' / 'schema' / 'ohlcv.json'
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            print("✅ OHLCV schema: Accessible")
        else:
            print("⚠️  OHLCV schema: Not found (will use fallback)")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema access error: {e}")
        return False

def test_data_directory_access():
    """Test access to shared data directory"""
    print("\n🧪 Testing Data Directory Access...")
    
    try:
        data_dir = Path(__file__).parent.parent / 'financial_data'
        data_dir.mkdir(exist_ok=True)
        
        # Test subdirectories
        subdirs = ['ohlcv', 'events']
        for subdir in subdirs:
            (data_dir / subdir).mkdir(exist_ok=True)
            print(f"✅ financial_data/{subdir}/: Ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Data directory error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Alpaca Data Collector Setup Validation")
    print("=" * 50)
    
    tests = [
        test_configuration_files,
        test_import_structure,
        test_directory_structure,
        test_shared_schema_access,
        test_data_directory_access
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Alpaca collector is ready for API key configuration.")
        print("\n📋 Next Steps:")
        print("1. Sign up for Alpaca account: https://app.alpaca.markets/")
        print("2. Get API keys and update config/sources.yaml")
        print("3. Install dependencies: poetry install")
        print("4. Run test collection: python3 ingest/orchestrator.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 