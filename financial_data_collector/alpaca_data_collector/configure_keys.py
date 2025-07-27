#!/usr/bin/env python3
"""
Alpaca API Key Configuration Helper
Safely updates Alpaca API keys in the configuration files.
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime

def backup_config():
    """Create backup of current configuration"""
    config_path = Path(__file__).parent / 'config' / 'sources.yaml'
    backup_path = config_path.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    shutil.copy2(config_path, backup_path)
    print(f"✅ Configuration backed up to: {backup_path.name}")
    return backup_path

def validate_api_key(api_key):
    """Validate API key format"""
    if not api_key or len(api_key) < 10:
        return False, "API key too short"
    
    # Paper trading keys typically start with 'PK'
    if api_key.startswith('PK'):
        return True, "Paper trading API key detected"
    elif api_key.startswith('AK'):
        return True, "Live trading API key detected (will use paper endpoint)"
    else:
        return True, "API key format accepted"

def validate_secret_key(secret_key):
    """Validate secret key format"""
    if not secret_key or len(secret_key) < 20:
        return False, "Secret key too short"
    
    return True, "Secret key format accepted"

def update_config(api_key, secret_key):
    """Update configuration with new API keys"""
    try:
        config_path = Path(__file__).parent / 'config' / 'sources.yaml'
        
        # Load current config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update Alpaca configuration
        config['alpaca']['api_key'] = api_key
        config['alpaca']['secret_key'] = secret_key
        config['alpaca']['status'] = 'active'
        
        # Write updated config
        with open(config_path, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        
        print("✅ Configuration updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def test_configuration():
    """Test the updated configuration"""
    try:
        config_path = Path(__file__).parent / 'config' / 'sources.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        alpaca_config = config['alpaca']
        api_key = alpaca_config['api_key']
        secret_key = alpaca_config['secret_key']
        status = alpaca_config['status']
        
        print(f"🔍 Configuration Test:")
        print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
        print(f"   Secret Key: {secret_key[:8]}...{secret_key[-4:]}")
        print(f"   Status: {status}")
        print(f"   Endpoint: {alpaca_config['endpoint']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def configure_interactive():
    """Interactive configuration setup"""
    print("🔐 Alpaca API Key Configuration")
    print("=" * 40)
    
    # Get API key
    print("\n📋 Enter your Alpaca API Key:")
    print("   (Should start with 'PK' for paper trading)")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    # Validate API key
    valid, message = validate_api_key(api_key)
    if not valid:
        print(f"❌ Invalid API key: {message}")
        return False
    
    print(f"✅ {message}")
    
    # Get secret key
    print("\n🔒 Enter your Alpaca Secret Key:")
    print("   (Long random string - keep this secure!)")
    secret_key = input("Secret Key: ").strip()
    
    if not secret_key:
        print("❌ No secret key provided. Exiting.")
        return False
    
    # Validate secret key
    valid, message = validate_secret_key(secret_key)
    if not valid:
        print(f"❌ Invalid secret key: {message}")
        return False
    
    print(f"✅ {message}")
    
    # Confirm configuration
    print(f"\n🔍 Configuration Summary:")
    print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"   Secret Key: {secret_key[:8]}...{secret_key[-4:]}")
    
    confirm = input("\n💾 Save this configuration? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Configuration cancelled.")
        return False
    
    # Backup and update
    backup_config()
    
    if update_config(api_key, secret_key):
        print("\n🎉 Alpaca API keys configured successfully!")
        test_configuration()
        return True
    else:
        print("❌ Failed to update configuration.")
        return False

def configure_args(api_key, secret_key):
    """Configure with command line arguments"""
    print("🔐 Configuring Alpaca API Keys...")
    
    # Validate keys
    api_valid, api_msg = validate_api_key(api_key)
    secret_valid, secret_msg = validate_secret_key(secret_key)
    
    if not api_valid:
        print(f"❌ Invalid API key: {api_msg}")
        return False
    
    if not secret_valid:
        print(f"❌ Invalid secret key: {secret_msg}")
        return False
    
    print(f"✅ API Key: {api_msg}")
    print(f"✅ Secret Key: {secret_msg}")
    
    # Backup and update
    backup_config()
    
    if update_config(api_key, secret_key):
        print("🎉 Configuration updated successfully!")
        test_configuration()
        return True
    else:
        return False

def main():
    """Main configuration function"""
    import sys
    
    if len(sys.argv) == 3:
        # Command line mode
        api_key = sys.argv[1]
        secret_key = sys.argv[2]
        return configure_args(api_key, secret_key)
    else:
        # Interactive mode
        return configure_interactive()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 