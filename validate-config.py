#!/usr/bin/env python3
"""
Network Device MCP Server Configuration Validator
Validates configuration and tests connections with absolute path resolution
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Establish absolute paths immediately
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"

# Ensure src directory is in path
sys.path.insert(0, str(SRC_DIR))

# Load .env file with absolute path before any other imports
ENV_FILE = PROJECT_ROOT / ".env"
print(f"Loading .env file from: {ENV_FILE}")

try:
    from dotenv import load_dotenv
    if ENV_FILE.exists():
        result = load_dotenv(ENV_FILE)
        print(f"✓ Loaded .env file successfully (result: {result})")
    else:
        print(f"⚠️ .env file not found at: {ENV_FILE}")
except ImportError:
    print("⚠️ python-dotenv not available")

# Now import the modules
from config import get_config
from platforms.fortimanager import FortiManagerManager

async def test_fortimanager_connection(fm_config):
    """Test connection to a single FortiManager"""
    fm_manager = FortiManagerManager()
    
    try:
        # Test login
        session_id = await fm_manager._login(
            fm_config['host'], 
            fm_config['username'], 
            fm_config['password']
        )
        
        if session_id:
            try:
                # Test getting managed devices
                devices = await fm_manager.get_managed_devices(
                    fm_config['host'], 
                    fm_config['username'], 
                    fm_config['password']
                )
                
                # Logout
                await fm_manager.logout(fm_config['host'])
                
                return {
                    "success": True,
                    "device_count": len(devices),
                    "devices": devices[:3]  # First 3 devices for preview
                }
                
            except Exception as e:
                await fm_manager.logout(fm_config['host'])
                return {
                    "success": True,
                    "connection": "Connected but device query failed",
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "error": "Authentication failed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection failed: {str(e)}"
        }

async def main():
    print("Network Device MCP Server - Configuration Validator")
    print("=" * 55)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Script location: {SCRIPT_PATH}")
    print()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = get_config()
        
        # Display debug info
        debug_info = config.debug_info()
        print("Debug Information:")
        print("-" * 18)
        for key, value in debug_info.items():
            print(f"  {key}: {value}")
        print()
        
        # Configuration Summary
        print("Configuration Summary:")
        print("-" * 21)
        print(f"FortiManager instances: {len(config.fortimanager_instances)}")
        for fm in config.fortimanager_instances:
            print(f"  - {fm['name']}: {fm['host']}")
        
        print(f"FortiGate devices: {len(config.fortigate_devices)}")
        for fg in config.fortigate_devices:
            print(f"  - {fg['name']}: {fg['host']}")
        
        print(f"Meraki configured: {config.has_meraki_config()}")
        if config.has_meraki_config():
            api_key_display = f"{'*' * 20}{config.meraki_api_key[-4:]}" if len(config.meraki_api_key) > 4 else "Set"
            print(f"  - API Key: {api_key_display}")
            print(f"  - Org ID: {config.meraki_org_id}")
        
        print()
        
        # Test FortiManager connections
        if config.fortimanager_instances:
            print("Testing FortiManager Connections:")
            print("-" * 35)
            
            for fm in config.fortimanager_instances:
                print(f"Testing {fm['name']} ({fm['host']})...", end="", flush=True)
                
                result = await test_fortimanager_connection(fm)
                
                if result["success"]:
                    print(" ✓ Connected successfully")
                    if "device_count" in result:
                        print(f"    Found {result['device_count']} managed devices")
                        
                        # Show sample devices
                        for device in result.get("devices", []):
                            status = "Online" if device.get('status') == 'online' else "Offline"
                            print(f"      • {device.get('name', 'Unknown')}: {status}")
                            
                    elif "connection" in result:
                        print(f"    {result['connection']}")
                        if "error" in result:
                            print(f"    Error: {result['error']}")
                else:
                    print(f" ❌ {result['error']}")
                    print("    Check:")
                    print("      - Host IP is reachable")
                    print("      - Username and password are correct") 
                    print("      - FortiManager API/JSONRPC is enabled")
                
                print()
        else:
            print("No FortiManager instances configured.")
            print("Check your .env file configuration.")
            print()
        
        # Path Validation
        print("Path Validation:")
        print("-" * 15)
        
        paths_to_check = [
            ("Backup Path", config.backup_path),
            ("Report Path", config.report_path),
            ("Project Root", config.project_root),
            ("Env File", config.env_file)
        ]
        
        for name, path in paths_to_check:
            if path and Path(path).exists():
                print(f"✓ {name}: {path}")
            elif path:
                print(f"⚠️ {name}: {path} (does not exist)")
            else:
                print(f"❌ {name}: Not configured")
        
        print()
        
        # Validation Summary
        print("Validation Summary:")
        print("=" * 18)
        
        validation = config.validate_config()
        for key, status in validation.items():
            status_icon = "✓" if status else "❌"
            status_text = str(status) if not isinstance(status, bool) else ("Yes" if status else "No")
            print(f"{status_icon} {key.replace('_', ' ').title()}: {status_text}")
        
        print()
        
        # Final recommendations
        if validation['fortimanager_instances'] > 0:
            print("🎉 Configuration validation passed!")
            print()
            print("Next Steps:")
            print("1. Update Claude Desktop MCP configuration")
            print("2. Restart Claude Desktop")
            print("3. Test with: 'Show me my FortiManager instances'")
            print("4. Try: 'Get devices managed by Arbys FortiManager'")
        else:
            print("⚠️ Configuration issues detected.")
            print("Recommendations:")
            if not validation['env_file_found']:
                print("- Create .env file with your credentials")
            else:
                print("- Check .env file contains correct FortiManager variables")
                print("- Verify environment variable names match expected format")
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Check that all required files exist in the project directory")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Check that all required Python packages are installed")
        print("Run: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
