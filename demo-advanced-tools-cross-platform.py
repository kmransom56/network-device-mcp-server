#!/usr/bin/env python3
"""
Cross-Platform Advanced Network Tools Demo
Works on both Windows and WSL environments
"""
import asyncio
import sys
import os
import platform
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def demo_advanced_tools():
    """Demonstrate all advanced network tools from network_tools.txt"""
    print("=" * 70)
    print("   🔧 Advanced Network Tools Demonstration")
    print("=" * 70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 Platform: {platform.system()} ({platform.platform()})")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Import MCP server components
    try:
        from main import NetworkDeviceMCPServer
        print("✅ Successfully imported MCP server components")
    except ImportError as e:
        print(f"❌ Failed to import MCP server components: {e}")
        print("💡 Make sure you're running from the project root directory")
        return False
    
    print("\n🏗️ Initializing MCP Server...")
    server = NetworkDeviceMCPServer()
    
    # Test all advanced network tools
    tools_to_test = [
        {
            "name": "Policy Package Rules Analysis",
            "tool": "_get_policy_package_rules",
            "args": {
                "fortimanager_name": "BWW",
                "package_name": "Standard_Policy",
                "adom": "root"
            },
            "description": "Analyze FortiManager policy package rules for security compliance"
        },
        {
            "name": "Web Filter Profile Analysis", 
            "tool": "_get_webfilter_profile",
            "args": {
                "fortigate_name": "IBR-BWW-00155",
                "profile_name": "Standard_Filter"
            },
            "description": "Review web filtering policies and blocked categories"
        },
        {
            "name": "Device Routing Table Analysis",
            "tool": "_get_device_routing_table", 
            "args": {
                "device_name": "IBR-BWW-00155",
                "device_platform": "fortigate",
                "route_type": "all"
            },
            "description": "Analyze network routing configuration and connectivity paths"
        },
        {
            "name": "Device Logs Analysis",
            "tool": "_get_device_logs",
            "args": {
                "device_name": "IBR-BWW-00155",
                "log_type": "traffic",
                "time_range": "1h",
                "max_entries": 100
            },
            "description": "Review recent traffic logs for security events and patterns"
        },
        {
            "name": "Network Connectivity Test",
            "tool": "_execute_connectivity_test",
            "args": {
                "device_name": "IBR-BWW-00155",
                "destination": "8.8.8.8",
                "test_type": "ping",
                "protocol": "icmp"
            },
            "description": "Test network connectivity and diagnose connection issues"
        }
    ]
    
    results = []
    
    for i, tool_config in enumerate(tools_to_test, 1):
        print(f"\n{'=' * 60}")
        print(f"   🔧 Test {i}/{len(tools_to_test)}: {tool_config['name']}")
        print("=" * 60)
        print(f"📋 Description: {tool_config['description']}")
        print(f"🛠️  Tool: {tool_config['tool']}")
        print(f"📊 Arguments: {tool_config['args']}")
        
        try:
            # Get the tool handler
            handler = getattr(server, tool_config['tool'])
            
            print("\n🚀 Executing tool...")
            result = await handler(tool_config['args'])
            
            if result:
                print("✅ Tool executed successfully")
                print(f"📄 Response length: {len(str(result))} characters")
                
                # Show key insights from the result
                if isinstance(result, dict):
                    if 'analysis_summary' in result:
                        print(f"🔍 Analysis Summary: {result['analysis_summary']}")
                    if 'total_rules' in result:
                        print(f"📊 Total Rules: {result['total_rules']}")
                    if 'security_score' in result:
                        print(f"🛡️  Security Score: {result['security_score']}/100")
                    if 'connectivity_status' in result:
                        print(f"🌐 Connectivity: {result['connectivity_status']}")
                
                results.append((tool_config['name'], True, None))
            else:
                print("⚠️ Tool returned empty result")
                results.append((tool_config['name'], False, "Empty result"))
                
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            results.append((tool_config['name'], False, str(e)))
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Summary Report
    print("\n" + "=" * 70)
    print("   📊 Advanced Tools Demo - Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for tool_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {tool_name}")
        if error:
            print(f"      Error: {error}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall Results: {passed}/{total} tools tested successfully ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All advanced network tools are working perfectly!")
        print("🚀 Your MCP server now has enhanced network troubleshooting capabilities")
        print("\n✨ Key Capabilities Added:")
        print("   • Policy compliance analysis")
        print("   • Web filtering review and optimization") 
        print("   • Network routing diagnostics")
        print("   • Real-time log analysis")
        print("   • Connectivity testing and troubleshooting")
    else:
        print("⚠️ Some tools encountered issues - this is expected in demo mode")
        print("💡 In production, these tools will connect to your actual FortiGate/FortiManager devices")
    
    print(f"\n🕐 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

def detect_environment():
    """Detect if running in Windows or WSL"""
    if platform.system() == "Windows":
        return "windows"
    elif platform.system() == "Linux":
        # Check if it's WSL
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    return "wsl"
            return "linux"
        except:
            return "linux"
    else:
        return "other"

def check_environment():
    """Check and display environment information"""
    env_type = detect_environment()
    print(f"🔍 Environment Detection: {env_type.upper()}")
    
    if env_type == "windows":
        print("   • Running on native Windows")
        print("   • Virtual environment: venv\\Scripts\\activate.bat")
    elif env_type == "wsl":
        print("   • Running on Windows Subsystem for Linux (WSL)")
        print("   • Virtual environment: venv/bin/activate")
    elif env_type == "linux":
        print("   • Running on native Linux")
        print("   • Virtual environment: venv/bin/activate")
    
    return env_type

async def main():
    """Main demo function with environment detection"""
    print("🔧 Cross-Platform Advanced Network Tools Demo")
    print("=" * 50)
    
    # Environment check
    env_type = check_environment()
    
    # Check if we're in the right directory
    if not os.path.exists("src/main.py"):
        print("❌ Error: This script must be run from the project root directory")
        print("💡 Current directory:", os.getcwd())
        print("💡 Expected to find: src/main.py")
        return False
    
    # Check virtual environment
    venv_activated = False
    if env_type == "windows":
        venv_activated = "VIRTUAL_ENV" in os.environ or os.path.exists("venv/Scripts/activate.bat")
    else:
        venv_activated = "VIRTUAL_ENV" in os.environ or os.path.exists("venv/bin/activate")
    
    if not venv_activated:
        print("⚠️ Warning: Virtual environment may not be activated")
        print("💡 For best results, activate the virtual environment first")
    
    # Run the demo
    success = await demo_advanced_tools()
    
    print("\n" + "=" * 70)
    print("   🎯 Next Steps for Team Access")
    print("=" * 70)
    print("1. 🔥 Configure firewall: setup-firewall.bat (Windows) or setup-firewall.sh (Linux)")
    print("2. 🚀 Start web dashboard: start-web-dashboard.bat or start-web-dashboard.sh")
    print("3. 🌐 Share with team: http://[YOUR-IP]:5000")
    print("4. 📋 Provide training: TEAM-SETUP.md")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)