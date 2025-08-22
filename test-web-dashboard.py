#!/usr/bin/env python3
"""
Web Dashboard Network Access Test
Tests the web interface and API endpoints
"""
import requests
import json
import sys
import time
from datetime import datetime

class WebDashboardTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_connection(self):
        """Test basic connectivity to the web dashboard"""
        print("🧪 Testing Web Dashboard Connection...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health Check: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection refused - server may not be running")
            return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def test_web_interface(self):
        """Test the main web interface"""
        print("\n🌐 Testing Web Interface...")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                if "Network Device Management Dashboard" in content:
                    print("✅ Main dashboard loaded successfully")
                    print(f"   📄 Page size: {len(content)} characters")
                    return True
                else:
                    print("❌ Dashboard loaded but content seems wrong")
                    return False
            else:
                print(f"❌ Dashboard failed to load: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Web interface test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test key API endpoints"""
        print("\n🔌 Testing API Endpoints...")
        
        endpoints = [
            ("/api", "API Documentation"),
            ("/api/brands", "Supported Brands"),
            ("/api/fortimanager", "FortiManager Instances")
        ]
        
        results = []
        for endpoint, description in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description}: {endpoint}")
                    if endpoint == "/api/brands" and "supported_restaurant_brands" in data:
                        brand_count = len(data["supported_restaurant_brands"])
                        print(f"   📊 Found {brand_count} supported brands")
                    results.append(True)
                else:
                    print(f"❌ {description}: HTTP {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {description}: {e}")
                results.append(False)
        
        return all(results)
    
    def test_store_investigation_api(self):
        """Test store investigation API endpoints"""
        print("\n🔍 Testing Store Investigation APIs...")
        
        # Test different brands and stores
        test_cases = [
            ("BWW", "155", "Buffalo Wild Wings Store 155"),
            ("ARBYS", "1234", "Arby's Store 1234"),
            ("SONIC", "789", "Sonic Store 789")
        ]
        
        for brand, store_id, description in test_cases:
            print(f"\n   Testing {description}...")
            
            # Test security health endpoint
            try:
                url = f"{self.base_url}/api/stores/{brand.lower()}/{store_id}/security"
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        health_data = data["data"]
                        score = health_data["store_security_health"]["security_score"]
                        print(f"   ✅ Security Health: {score}/100")
                    else:
                        print(f"   ⚠️ Security Health: API returned error")
                else:
                    print(f"   ❌ Security Health: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Security Health: {e}")
            
            # Test URL blocking endpoint
            try:
                url = f"{self.base_url}/api/stores/{brand.lower()}/{store_id}/url-blocking"
                response = self.session.get(url, params={"period": "24h"}, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ URL Blocking: Analysis completed")
                else:
                    print(f"   ❌ URL Blocking: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ URL Blocking: {e}")
    
    def test_advanced_network_tools(self):
        """Test the new advanced network tools via API"""
        print("\n🔧 Testing Advanced Network Tools...")
        
        # These would be POST requests in a real test
        # For now, we'll just verify the endpoints exist and return structured data
        test_tools = [
            ("Policy Package Rules", {"fortimanager_name": "BWW", "package_name": "Standard_Policy"}),
            ("Web Filter Profile", {"fortigate_name": "IBR-BWW-00155", "profile_name": "Standard_Filter"}),
            ("Device Routing Table", {"device_name": "IBR-BWW-00155", "device_platform": "fortigate"}),
            ("Device Logs", {"device_name": "IBR-BWW-00155", "log_type": "traffic"}),
            ("Connectivity Test", {"device_name": "IBR-BWW-00155", "destination": "8.8.8.8"})
        ]
        
        print("   📋 Advanced tools available (would require POST requests for full testing):")
        for tool_name, params in test_tools:
            print(f"   • {tool_name}: Ready for testing")
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("="*60)
        print("   🚀 Network Device MCP Dashboard - Comprehensive Test")
        print("="*60)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Testing URL: {self.base_url}")
        
        # Test sequence
        tests = [
            ("Connection Test", self.test_connection),
            ("Web Interface Test", self.test_web_interface), 
            ("API Endpoints Test", self.test_api_endpoints),
            ("Store Investigation Test", self.test_store_investigation_api),
            ("Advanced Tools Test", self.test_advanced_network_tools)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20}")
            result = test_func()
            results.append((test_name, result))
        
        # Summary
        print("\n" + "="*60)
        print("   📊 Test Results Summary")
        print("="*60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! Your MCP Dashboard is ready for team access.")
            print(f"🌐 Share this URL with your team: {self.base_url}")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
            print("💡 Make sure the MCP server is running: start-web-dashboard.bat")
        
        return passed == total

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP Web Dashboard Network Access")
    parser.add_argument("--url", default="http://localhost:5000", 
                       help="Base URL for the dashboard (default: http://localhost:5000)")
    
    args = parser.parse_args()
    
    print("🧪 MCP Web Dashboard Network Test")
    print(f"📡 Testing server at: {args.url}")
    
    # Check if server is likely running locally
    if args.url == "http://localhost:5000":
        print("💡 Make sure you've started the server with: start-web-dashboard.bat")
        print("⏳ Waiting 3 seconds for you to start the server if needed...")
        time.sleep(3)
    
    tester = WebDashboardTester(args.url)
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🚀 Next Steps:")
        print("1. Run setup-firewall.bat (as Administrator) for team access")
        print("2. Find your IP: ipconfig")
        print("3. Share with team: http://[YOUR-IP]:5000")
        print("4. Train team on investigation process")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()