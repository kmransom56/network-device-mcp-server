# test_github_secrets.py - Quick test script for GitHub secrets integration
"""
Test script to verify GitHub secrets are being loaded correctly
"""
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_environment_variables():
    """Check if GitHub secrets are available as environment variables"""
    print("Testing GitHub Secrets Integration")
    print("=" * 50)
    
    required_secrets = [
        'FORTIMANAGER_ARBYS_HOST',
        'FORTIMANAGER_ARBYS_USERNAME',
        'FORTIMANAGER_ARBYS_PASSWORD',
        'FORTIMANAGER_BWW_HOST',
        'FORTIMANAGER_BWW_USERNAME',
        'FORTIMANAGER_BWW_PASSWORD',
        'FORTIMANAGER_SONIC_HOST',
        'FORTIMANAGER_SONIC_USERNAME',
        'FORTIMANAGER_SONIC_PASSWORD'
    ]
    
    print("Environment Variables Status:")
    found_count = 0
    for secret in required_secrets:
        value = os.getenv(secret)
        if value:
            # Don't print actual values for security
            masked_value = f"{value[:3]}{'*' * max(0, len(value) - 6)}{value[-3:] if len(value) > 6 else ''}"
            print(f"  ✓ {secret}: {masked_value}")
            found_count += 1
        else:
            print(f"  ✗ {secret}: Not found")
    
    print(f"\nFound {found_count}/{len(required_secrets)} required secrets")
    return found_count > 0

def test_config_loading():
    """Test the config module loading"""
    print("\nTesting Configuration Loading:")
    try:
        from config import get_config
        config = get_config()
        
        print(f"  ✓ Config module loaded successfully")
        print(f"  - FortiManager instances: {len(config.fortimanager_instances)}")
        print(f"  - FortiGate devices: {len(config.fortigate_devices)}")
        print(f"  - Meraki configured: {config.has_meraki_config()}")
        print(f"  - Running in GitHub Actions: {config.is_github_deployment()}")
        
        if config.fortimanager_instances:
            print("  FortiManager instances found:")
            for fm in config.fortimanager_instances:
                print(f"    - {fm['name']}: {fm['host']}")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed to load config: {e}")
        return False

def main():
    env_test = test_environment_variables()
    config_test = test_config_loading()
    
    print("\n" + "=" * 50)
    if env_test and config_test:
        print("SUCCESS: GitHub secrets integration is working!")
        print("\nNext steps:")
        print("1. Test the MCP server startup")
        print("2. Update Claude Desktop configuration")
        print("3. Test network device operations")
    else:
        print("ISSUES DETECTED:")
        if not env_test:
            print("- GitHub secrets not available as environment variables")
            print("  Make sure secrets are set in your repository")
        if not config_test:
            print("- Configuration loading failed")
            print("  Check for import errors or syntax issues")
    
    return 0 if (env_test and config_test) else 1

if __name__ == "__main__":
    sys.exit(main())
