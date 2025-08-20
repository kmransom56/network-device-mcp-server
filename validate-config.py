#!/usr/bin/env python3
"""
Environment Configuration Validator
Validates .env file and tests connections to your FortiManager instances
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import get_config
from platforms.fortimanager import FortiManagerManager

async def main():
    print("Network Device MCP Server - Configuration Validator")
    print("=" * 55)
    print()
    
    try:
        # Load configuration
        print("Loading configuration from .env file...")
        config = get_config()
        print("✓ Configuration loaded successfully")
        print()
        
        # Validate configuration
        print("Configuration Summary:")
        print("-" * 20)
        print(f"FortiManager instances: {len(config.fortimanager_instances)}")
        for fm in config.fortimanager_instances:
            print(f"  - {fm['name']}: {fm['host']}")
        
        print(f"FortiGate devices: {len(config.fortigate_devices)}")
        for fg in config.fortigate_devices:
            print(f"  - {fg['name']}: {fg['host']}")
        
        print(f"Meraki configured: {config.has_meraki_config()}")
        if config.has_meraki_config():
            print(f"  - API Key: {'*' * 20}{config.meraki_api_key[-4:] if len(config.meraki_api_key) > 4 else 'Set'}")
            print(f"  - Org ID: {config.meraki_org_id}")
        
        print()
        
        # Test FortiManager connections
        if config.fortimanager_instances:
            print("Testing FortiManager Connections:")
            print("-" * 35)
            
            fm_manager = FortiManagerManager()
            
            for fm in config.fortimanager_instances:
                print(f"Testing {fm['name']} ({fm['host']})...", end="", flush=True)
                
                try:
                    # Test login
                    session_id = await fm_manager._login(fm['host'], fm['username'], fm['password'])
                    if session_id:
                        print(" ✓ Connected successfully")
                        
                        # Test getting managed devices
                        try:
                            devices = await fm_manager.get_managed_devices(
                                fm['host'], fm['username'], fm['password']
                            )
                            print(f"    Found {len(devices)} managed devices")
                            
                            # Show sample devices
                            if devices:
                                sample_devices = devices[:3]  # Show first 3
                                for device in sample_devices:
                                    status = "🟢 Online" if device.get('status') == 'online' else "🔴 Offline"
                                    print(f"      • {device.get('name', 'Unknown')}: {status}")
                                if len(devices) > 3:
                                    print(f"      ... and {len(devices) - 3} more devices")
                            
                        except Exception as e:
                            print(f"    ⚠️  Connected but could not get devices: {e}")
                        
                        # Logout
                        await fm_manager.logout(fm['host'])
                        
                    else:
                        print(" ❌ Authentication failed")
                        
                except Exception as e:
                    print(f" ❌ Connection failed: {e}")
                    print("    Check:")
                    print("      - Host IP is reachable")
                    print("      - Username and password are correct")
                    print("      - FortiManager API/JSONRPC is enabled")
                
                print()
        
        # Validate paths
        print("Path Validation:")
        print("-" * 15)
        
        paths_to_check = [
            ("Backup Path", config.backup_path),
            ("Report Path", config.report_path)
        ]
        
        for name, path in paths_to_check:
            if os.path.exists(path):
                print(f"✓ {name}: {path}")
            else:
                print(f"⚠️  {name}: {path} (will be created)")
                try:
                    os.makedirs(path, exist_ok=True)
                    print(f"    ✓ Created directory")
                except Exception as e:
                    print(f"    ❌ Could not create: {e}")
        
        print()
        print("Validation Summary:")
        print("=" * 18)
        
        validation = config.validate_config()
        for key, status in validation.items():
            status_icon = "✓" if status else "❌"
            print(f"{status_icon} {key.replace('_', ' ').title()}: {status}")
        
        print()
        
        if all(validation.values()):
            print("🎉 All validations passed! Your configuration is ready.")
        else:
            print("⚠️  Some validations failed. Please check your .env file.")
        
        print()
        print("Next Steps:")
        print("1. If all validations passed, restart Claude Desktop")
        print("2. Test in Claude: 'Show me my FortiManager instances'")  
        print("3. Try: 'Get devices managed by Arbys FortiManager'")
        
    except FileNotFoundError:
        print("❌ .env file not found!")
        print()
        print("Please:")
        print("1. Copy .env.template to .env")
        print("2. Edit .env with your actual credentials")
        print("3. Run this validator again")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
