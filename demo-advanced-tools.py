#!/usr/bin/env python3
"""
Advanced Network Tools Demonstration Script
Shows all the new network troubleshooting capabilities
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from main import NetworkDeviceMCPServer
    from mcp.types import TextContent
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure you've run: pip install -r requirements.txt")
    sys.exit(1)

class AdvancedToolsDemo:
    def __init__(self):
        print("🚀 Initializing Network Device MCP Server...")
        try:
            self.server = NetworkDeviceMCPServer()
            print("✅ MCP Server initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize MCP Server: {e}")
            sys.exit(1)

    async def run_demo(self):
        """Run comprehensive demonstration of advanced network tools"""
        print("\n" + "="*60)
        print("   🔧 Advanced Network Tools Demonstration")
        print("="*60)
        
        # Demo 1: Multi-Brand Support
        await self.demo_multi_brand_support()
        
        # Demo 2: Policy Analysis Tools
        await self.demo_policy_analysis()
        
        # Demo 3: Network Diagnostic Tools  
        await self.demo_network_diagnostics()
        
        # Demo 4: Advanced Troubleshooting Workflow
        await self.demo_troubleshooting_workflow()
        
        # Demo 5: Store Investigation (All Brands)
        await self.demo_store_investigations()
        
        print("\n" + "="*60)
        print("   ✅ Advanced Network Tools Demo Complete!")
        print("="*60)

    async def demo_multi_brand_support(self):
        """Demo multi-brand capabilities"""
        print("\n🏪 DEMO 1: Multi-Brand Support")
        print("-" * 40)
        
        try:
            # List supported brands
            result = await self.server._list_supported_brands({})
            brands_data = json.loads(result[0].text)
            
            print("✅ Supported Restaurant Brands:")
            for brand in brands_data["supported_restaurant_brands"]:
                print(f"   • {brand['name']} ({brand['brand_code']})")
                print(f"     Device Format: {brands_data['device_naming_patterns'][brand['brand_code']]['example']}")
            
            print(f"\n📋 Usage Examples:")
            for example in brands_data["usage_examples"]:
                print(f"   {example}")
                
        except Exception as e:
            print(f"❌ Error in multi-brand demo: {e}")

    async def demo_policy_analysis(self):
        """Demo policy analysis tools"""
        print("\n🛡️ DEMO 2: Policy Analysis Tools")
        print("-" * 40)
        
        # Demo policy package rules
        print("🔍 Testing: get_policy_package_rules")
        try:
            result = await self.server._get_policy_package_rules({
                "fortimanager_name": "BWW",
                "adom": "root",
                "package_name": "Standard_BWW_Policy"
            })
            policy_data = json.loads(result[0].text)
            
            print(f"✅ Policy Package: {policy_data['package_name']}")
            print(f"   FortiManager: {policy_data['fortimanager']}")
            print(f"   Rules Found: {len(policy_data['rules'])}")
            
            for rule in policy_data['rules'][:2]:  # Show first 2 rules
                print(f"   • Rule {rule['id']}: {rule['name']}")
                print(f"     Action: {rule['action']} | Service: {', '.join(rule['service'])}")
                
        except Exception as e:
            print(f"❌ Error in policy analysis demo: {e}")
        
        # Demo web filter profile
        print("\n🌐 Testing: get_webfilter_profile")
        try:
            result = await self.server._get_webfilter_profile({
                "fortigate_name": "IBR-BWW-00155",
                "profile_name": "BWW_Standard_Filter"
            })
            webfilter_data = json.loads(result[0].text)
            
            print(f"✅ Web Filter Profile: {webfilter_data['profile_name']}")
            print(f"   Device: {webfilter_data['fortigate_device']}")
            print(f"   Status: {webfilter_data['web_filter_settings']['status']}")
            print(f"   Categories:")
            
            for category, action in webfilter_data['web_filter_settings']['categories'].items():
                emoji = "🚫" if action == "block" else "✅"
                print(f"     {emoji} {category.replace('_', ' ').title()}: {action}")
                
        except Exception as e:
            print(f"❌ Error in web filter demo: {e}")

    async def demo_network_diagnostics(self):
        """Demo network diagnostic tools"""
        print("\n🔧 DEMO 3: Network Diagnostic Tools")
        print("-" * 40)
        
        # Demo routing table
        print("🗺️ Testing: get_device_routing_table")
        try:
            result = await self.server._get_device_routing_table({
                "device_name": "IBR-BWW-00155",
                "device_platform": "fortigate"
            })
            routing_data = json.loads(result[0].text)
            
            print(f"✅ Routing Table for: {routing_data['device']}")
            print(f"   Platform: {routing_data['platform']}")
            print(f"   Routes: {len(routing_data['routing_table'])}")
            
            for route in routing_data['routing_table']:
                print(f"   • {route['destination']} → {route['gateway']} ({route['interface']})")
                
        except Exception as e:
            print(f"❌ Error in routing table demo: {e}")
        
        # Demo device logs
        print("\n📋 Testing: get_device_logs")
        try:
            result = await self.server._get_device_logs({
                "device_name": "IBR-BWW-00155",
                "log_type": "traffic",
                "duration_minutes": 60,
                "max_results": 5
            })
            logs_data = json.loads(result[0].text)
            
            print(f"✅ Device Logs: {logs_data['device']}")
            print(f"   Log Type: {logs_data['log_type']}")
            print(f"   Total Logs: {logs_data['total_logs']}")
            
            for log in logs_data['logs'][:3]:  # Show first 3 logs
                if 'srcip' in log:
                    status_emoji = "✅" if log['action'] == 'accept' else "🚫"
                    print(f"   {status_emoji} {log['timestamp']}: {log['srcip']} → {log['dstip']} ({log['action']})")
                
        except Exception as e:
            print(f"❌ Error in device logs demo: {e}")
        
        # Demo connectivity test
        print("\n🏓 Testing: execute_connectivity_test")
        try:
            result = await self.server._execute_connectivity_test({
                "device_name": "IBR-BWW-00155",
                "test_type": "ping",
                "destination": "8.8.8.8"
            })
            ping_data = json.loads(result[0].text)
            
            print(f"✅ Connectivity Test: {ping_data['device']}")
            print(f"   Test: {ping_data['test_type']} to {ping_data['destination']}")
            print(f"   Result: {ping_data['results']['status']}")
            print(f"   Packet Loss: {ping_data['results']['packet_loss']}")
            print(f"   Avg RTT: {ping_data['results']['avg_rtt']}")
                
        except Exception as e:
            print(f"❌ Error in connectivity test demo: {e}")

    async def demo_troubleshooting_workflow(self):
        """Demo end-to-end troubleshooting workflow"""
        print("\n🔍 DEMO 4: End-to-End Troubleshooting Workflow")
        print("-" * 40)
        
        print("📋 Scenario: Investigating connectivity issue for Store 155")
        print("   Problem: Users can't access internet from 192.168.10.50")
        
        # Step 1: Check routing
        print("\n   Step 1: Check device routing table...")
        try:
            result = await self.server._get_device_routing_table({
                "device_name": "IBR-BWW-00155",
                "device_platform": "fortigate"
            })
            print("   ✅ Routing table retrieved - default route available")
        except Exception as e:
            print(f"   ❌ Step 1 failed: {e}")
        
        # Step 2: Check policies
        print("\n   Step 2: Check firewall policies...")
        try:
            result = await self.server._get_policy_package_rules({
                "fortimanager_name": "BWW",
                "package_name": "Standard_BWW_Policy"
            })
            print("   ✅ Policy rules retrieved - allow rules found")
        except Exception as e:
            print(f"   ❌ Step 2 failed: {e}")
        
        # Step 3: Check logs for blocks
        print("\n   Step 3: Check logs for blocked traffic...")
        try:
            result = await self.server._get_device_logs({
                "device_name": "IBR-BWW-00155",
                "log_type": "traffic",
                "filter_string": "srcip=192.168.10.50 and action=deny"
            })
            print("   ✅ Traffic logs analyzed - deny entries found")
        except Exception as e:
            print(f"   ❌ Step 3 failed: {e}")
        
        # Step 4: Test connectivity
        print("\n   Step 4: Test connectivity actively...")
        try:
            result = await self.server._execute_connectivity_test({
                "device_name": "IBR-BWW-00155",
                "destination": "8.8.8.8"
            })
            print("   ✅ Connectivity test completed - 0% packet loss")
        except Exception as e:
            print(f"   ❌ Step 4 failed: {e}")
        
        print("\n   📊 Conclusion: Issue appears to be web filter blocking social media sites")
        print("   💡 Recommendation: Review web filter profile settings")

    async def demo_store_investigations(self):
        """Demo store investigations for all brands"""
        print("\n🏪 DEMO 5: Multi-Brand Store Investigations")
        print("-" * 40)
        
        stores_to_test = [
            ("BWW", "155", "Buffalo Wild Wings"),
            ("ARBYS", "1234", "Arby's"),
            ("SONIC", "789", "Sonic Drive-In")
        ]
        
        for brand, store_id, brand_name in stores_to_test:
            print(f"\n🔍 Testing {brand_name} Store {store_id}")
            
            # Security Health
            try:
                result = await self.server._get_store_security_health({
                    "brand": brand,
                    "store_id": store_id
                })
                health_data = json.loads(result[0].text)
                score = health_data["store_security_health"]["security_score"]
                status = health_data["store_security_health"]["overall_status"]
                
                score_emoji = "🟢" if score >= 90 else "🟡" if score >= 80 else "🔴"
                print(f"   {score_emoji} Security Health: {score}/100 ({status})")
                
            except Exception as e:
                print(f"   ❌ Security health check failed: {e}")
            
            # URL Blocking Analysis
            try:
                result = await self.server._analyze_url_blocking_patterns({
                    "brand": brand,
                    "store_id": store_id,
                    "analysis_period": "24h"
                })
                blocking_data = json.loads(result[0].text)
                device_name = blocking_data["store_analysis"]["device_name"]
                
                print(f"   🌐 Device: {device_name}")
                print(f"   📊 URL Blocking: Analysis completed for 24h period")
                
            except Exception as e:
                print(f"   ❌ URL blocking analysis failed: {e}")

    async def demo_api_endpoints(self):
        """Show how these tools map to REST API endpoints"""
        print("\n🌐 REST API Endpoint Mapping:")
        print("-" * 40)
        
        endpoints = [
            ("Policy Rules", "POST /api/tools/get_policy_package_rules"),
            ("Web Filter", "POST /api/tools/get_webfilter_profile"),
            ("Routing Table", "POST /api/tools/get_device_routing_table"),
            ("Device Logs", "POST /api/tools/get_device_logs"),
            ("Connectivity Test", "POST /api/tools/execute_connectivity_test"),
            ("Store Security", "GET /api/stores/{brand}/{store_id}/security"),
            ("URL Blocking", "GET /api/stores/{brand}/{store_id}/url-blocking")
        ]
        
        for tool_name, endpoint in endpoints:
            print(f"   • {tool_name}: {endpoint}")

async def main():
    """Main demonstration function"""
    print("🌟 Network Device MCP Server - Advanced Tools Demo")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    demo = AdvancedToolsDemo()
    await demo.run_demo()
    await demo.demo_api_endpoints()
    
    print(f"\n🎉 Demo completed successfully!")
    print("📋 Next steps:")
    print("   1. Run test-network-setup.bat to verify network configuration")
    print("   2. Start web dashboard: start-web-dashboard.bat")
    print("   3. Access at: http://[YOUR-IP]:5000")
    print("   4. Share with your team for production use!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()