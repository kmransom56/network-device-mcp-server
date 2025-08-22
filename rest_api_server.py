#!/usr/bin/env python3
"""
REST API wrapper for MCP Server - Access via HTTP endpoints with Web Interface
"""
import asyncio
import json
import sys
from pathlib import Path
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import NetworkDeviceMCPServer

# Import integration modules
try:
    from integrations import (
        VLANManager,
        FortigateTroubleshooter, 
        FortiAPManager,
        NetworkUtilities,
        DashboardMerger,
        FortiAnalyzerManager,
        WebFiltersManager
    )
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    print("Warning: Integration modules not available. Run from project root directory.")
    INTEGRATIONS_AVAILABLE = False

# Initialize Flask app with web template folder
app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')
CORS(app)  # Enable CORS for web access

# Initialize MCP server and integration managers
mcp_server = None
integration_managers = {}

def get_mcp_server():
    global mcp_server
    if mcp_server is None:
        mcp_server = NetworkDeviceMCPServer()
    return mcp_server

def get_integration_managers():
    global integration_managers
    if not integration_managers and INTEGRATIONS_AVAILABLE:
        integration_managers = {
            'vlan': VLANManager(),
            'troubleshooter': FortigateTroubleshooter(),
            'ap': FortiAPManager(), 
            'utilities': NetworkUtilities(),
            'dashboard': DashboardMerger(),
            'fortianalyzer': FortiAnalyzerManager(),
            'webfilters': WebFiltersManager()
        }
    return integration_managers

async def call_mcp_tool(tool_name: str, arguments: dict):
    """Call MCP tool and return JSON result"""
    try:
        server = get_mcp_server()
        # Use the server's call_tool handler
        result = await server._NetworkDeviceMCPServer__handle_call_tool(tool_name, arguments)
        
        if result and hasattr(result[0], 'text'):
            return {"success": True, "data": json.loads(result[0].text)}
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# REST API Endpoints
@app.route('/api/brands', methods=['GET'])
def list_brands():
    """GET /api/brands - List all supported brands"""
    result = asyncio.run(call_mcp_tool("list_supported_brands", {}))
    return jsonify(result)

@app.route('/api/brands/<brand>/overview', methods=['GET'])
def brand_overview(brand):
    """GET /api/brands/{brand}/overview - Get brand infrastructure overview"""
    result = asyncio.run(call_mcp_tool("get_brand_store_summary", {"brand": brand.upper()}))
    return jsonify(result)

@app.route('/api/stores/<brand>/<store_id>/security', methods=['GET'])
def store_security_health(brand, store_id):
    """GET /api/stores/{brand}/{store_id}/security - Get store security health"""
    include_recommendations = request.args.get('recommendations', 'true').lower() == 'true'
    
    result = asyncio.run(call_mcp_tool("get_store_security_health", {
        "brand": brand.upper(),
        "store_id": store_id,
        "include_recommendations": include_recommendations
    }))
    return jsonify(result)

@app.route('/api/stores/<brand>/<store_id>/url-blocking', methods=['GET'])
def analyze_url_blocking(brand, store_id):
    """GET /api/stores/{brand}/{store_id}/url-blocking - Analyze URL blocking patterns"""
    period = request.args.get('period', '24h')
    export = request.args.get('export', 'true').lower() == 'true'
    
    result = asyncio.run(call_mcp_tool("analyze_url_blocking_patterns", {
        "brand": brand.upper(),
        "store_id": store_id,
        "analysis_period": period,
        "export_report": export
    }))
    return jsonify(result)

@app.route('/api/devices/<device_name>/security-events', methods=['GET'])
def security_events(device_name):
    """GET /api/devices/{device_name}/security-events - Get security event summary"""
    timeframe = request.args.get('timeframe', '24h')
    event_types = request.args.getlist('event_types') or ["webfilter", "ips", "antivirus", "application"]
    top_count = int(request.args.get('top_count', '10'))
    
    result = asyncio.run(call_mcp_tool("get_security_event_summary", {
        "device_name": device_name,
        "timeframe": timeframe,
        "event_types": event_types,
        "top_count": top_count
    }))
    return jsonify(result)

@app.route('/api/fortimanager', methods=['GET'])
def list_fortimanager():
    """GET /api/fortimanager - List FortiManager instances"""
    result = asyncio.run(call_mcp_tool("list_fortimanager_instances", {}))
    return jsonify(result)

@app.route('/api/fortimanager/<fm_name>/devices', methods=['GET'])
def fortimanager_devices(fm_name):
    """GET /api/fortimanager/{fm_name}/devices - Get FortiManager managed devices"""
    adom = request.args.get('adom', 'root')
    
    result = asyncio.run(call_mcp_tool("get_fortimanager_devices", {
        "fortimanager_name": fm_name.upper(),
        "adom": adom
    }))
    return jsonify(result)

# Web Interface Routes
@app.route('/')
def dashboard():
    """Main dashboard web interface"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('web/static', filename)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Network Device MCP REST API"})

# API documentation endpoint
@app.route('/api', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        "name": "Network Device MCP REST API",
        "endpoints": {
            "GET /api/brands": "List all supported restaurant brands",
            "GET /api/brands/{brand}/overview": "Get brand infrastructure overview", 
            "GET /api/stores/{brand}/{store_id}/security": "Get store security health",
            "GET /api/stores/{brand}/{store_id}/url-blocking": "Analyze URL blocking patterns",
            "GET /api/devices/{device_name}/security-events": "Get security event summary",
            "GET /api/fortimanager": "List FortiManager instances",
            "GET /api/fortimanager/{fm_name}/devices": "Get FortiManager managed devices"
        },
        "examples": {
            "BWW Store 155 security": "/api/stores/bww/155/security",
            "Arby's Store 1234 URL blocking": "/api/stores/arbys/1234/url-blocking?period=24h",
            "Sonic device security events": "/api/devices/IBR-SONIC-00789/security-events?timeframe=1h"
        }
    })

# ==============================================================================
# PROJECT INTEGRATION API ENDPOINTS
# Unified API layer connecting all existing Fortinet projects
# ==============================================================================

# VLAN Management Integration (fortigatevlans project)
@app.route('/api/vlans/<brand>/<store_id>', methods=['GET'])
def get_store_vlans(brand, store_id):
    """GET /api/vlans/{brand}/{store_id} - Get VLAN configuration for store"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['vlan'].get_store_vlan_config(brand, store_id)
    return jsonify(result)

@app.route('/api/vlans/<brand>', methods=['GET'])
def get_brand_vlans(brand):
    """GET /api/vlans/{brand} - Get VLAN summary for all stores in brand"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['vlan'].get_brand_vlan_summary(brand)
    return jsonify(result)

@app.route('/api/vlans/<brand>/<store_id>/<vlan_type>', methods=['GET'])
def get_store_vlan_interfaces(brand, store_id, vlan_type):
    """GET /api/vlans/{brand}/{store_id}/{vlan_type} - Get specific VLAN interfaces"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['vlan'].get_vlan_interfaces_by_type(brand, store_id, vlan_type)
    return jsonify(result)

@app.route('/api/vlans/collection', methods=['POST'])
def run_vlan_collection():
    """POST /api/vlans/collection - Run VLAN collection for brand/store"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    brand = data.get('brand')
    store_id = data.get('store_id')
    
    managers = get_integration_managers()
    result = managers['vlan'].run_vlan_collection(brand, store_id)
    return jsonify(result)

# FortiGate Troubleshooting Integration (fortigate-troubleshooter project)
@app.route('/api/troubleshoot/<device_name>', methods=['GET'])
def troubleshoot_device(device_name):
    """GET /api/troubleshoot/{device_name} - Run comprehensive device diagnostics"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['troubleshooter'].run_full_diagnostics(device_name)
    return jsonify(result)

@app.route('/api/troubleshoot/<device_name>/connectivity', methods=['GET'])
def test_device_connectivity(device_name):
    """GET /api/troubleshoot/{device_name}/connectivity - Test basic connectivity"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['troubleshooter'].test_connectivity(device_name)
    return jsonify(result)

@app.route('/api/troubleshoot/<device_name>/gui', methods=['GET'])
def test_device_gui(device_name):
    """GET /api/troubleshoot/{device_name}/gui - Test GUI access and X11 forwarding"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['troubleshooter'].test_gui_access(device_name)
    return jsonify(result)

@app.route('/api/troubleshoot/<device_name>/workflow', methods=['POST'])
def run_troubleshooting_workflow(device_name):
    """POST /api/troubleshoot/{device_name}/workflow - Run specific troubleshooting workflow"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    issue_type = data.get('issue_type', 'connectivity')
    
    managers = get_integration_managers()
    result = managers['troubleshooter'].run_troubleshooting_workflow(device_name, issue_type)
    return jsonify(result)

# FortiAP Management Integration (addfortiap project)
@app.route('/api/fortiaps/<brand>', methods=['GET'])
def get_brand_access_points(brand):
    """GET /api/fortiaps/{brand} - Get all FortiAPs for brand"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['ap'].get_brand_access_points(brand)
    return jsonify(result)

@app.route('/api/fortiaps/<brand>/<store_id>', methods=['GET'])
def get_store_access_points(brand, store_id):
    """GET /api/fortiaps/{brand}/{store_id} - Get FortiAPs for specific store"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['ap'].get_store_access_points(brand, store_id)
    return jsonify(result)

@app.route('/api/fortiaps/<brand>/<store_id>/health', methods=['GET'])
def get_store_ap_health(brand, store_id):
    """GET /api/fortiaps/{brand}/{store_id}/health - Run AP health check"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['ap'].run_ap_health_check(brand, store_id)
    return jsonify(result)

@app.route('/api/fortiaps/<brand>/<store_id>/clients', methods=['GET'])
def get_wireless_clients(brand, store_id):
    """GET /api/fortiaps/{brand}/{store_id}/clients - Get wireless clients"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['ap'].get_wireless_clients(brand, store_id)
    return jsonify(result)

@app.route('/api/fortiaps/<brand>/<store_id>/rf-analysis', methods=['GET'])
def get_rf_analysis(brand, store_id):
    """GET /api/fortiaps/{brand}/{store_id}/rf-analysis - Get RF analysis"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['ap'].get_rf_analysis(brand, store_id)
    return jsonify(result)

@app.route('/api/fortiaps/ap/<ap_serial>', methods=['GET'])
def get_ap_status(ap_serial):
    """GET /api/fortiaps/ap/{ap_serial} - Get status of specific FortiAP"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['ap'].get_ap_status(ap_serial)
    return jsonify(result)

@app.route('/api/fortiaps/<brand>/<store_id>/deploy', methods=['POST'])
def deploy_fortiap(brand, store_id):
    """POST /api/fortiaps/{brand}/{store_id}/deploy - Deploy new FortiAP"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    managers = get_integration_managers()
    result = managers['ap'].deploy_fortiap(brand, store_id, data)
    return jsonify(result)

# Network Utilities Integration (Utilities project)
@app.route('/api/utilities', methods=['GET'])
def get_available_utilities():
    """GET /api/utilities - Get list of available network utilities"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['utilities'].get_available_utilities()
    return jsonify(result)

@app.route('/api/utilities/device-discovery', methods=['POST'])
def run_device_discovery():
    """POST /api/utilities/device-discovery - Run network device discovery"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    target_network = data.get('target_network')
    brand = data.get('brand')
    
    if not target_network:
        return jsonify({"success": False, "error": "target_network required"})
    
    managers = get_integration_managers()
    result = managers['utilities'].run_device_discovery(target_network, brand)
    return jsonify(result)

@app.route('/api/utilities/snmp-check', methods=['POST'])
def check_snmp_connectivity():
    """POST /api/utilities/snmp-check - Check SNMP connectivity"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    device_ip = data.get('device_ip')
    community = data.get('community', 'public')
    
    if not device_ip:
        return jsonify({"success": False, "error": "device_ip required"})
    
    managers = get_integration_managers()
    result = managers['utilities'].check_snmp_connectivity(device_ip, community)
    return jsonify(result)

@app.route('/api/utilities/config-diff', methods=['POST'])
def compare_fortigate_configs():
    """POST /api/utilities/config-diff - Compare FortiGate configurations"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    device1 = data.get('device1')
    device2 = data.get('device2')
    
    if not device1 or not device2:
        return jsonify({"success": False, "error": "device1 and device2 required"})
    
    managers = get_integration_managers()
    result = managers['utilities'].compare_fortigate_configs(device1, device2)
    return jsonify(result)

@app.route('/api/utilities/ssl-diagnostics', methods=['POST'])
def run_ssl_diagnostics():
    """POST /api/utilities/ssl-diagnostics - Run SSL certificate diagnostics"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    device_ip = data.get('device_ip')
    port = data.get('port', 443)
    
    if not device_ip:
        return jsonify({"success": False, "error": "device_ip required"})
    
    managers = get_integration_managers()
    result = managers['utilities'].run_ssl_diagnostics(device_ip, port)
    return jsonify(result)

@app.route('/api/utilities/ip-lookup', methods=['POST'])
def lookup_ip_address():
    """POST /api/utilities/ip-lookup - Perform IP address lookup"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    ip_address = data.get('ip_address')
    
    if not ip_address:
        return jsonify({"success": False, "error": "ip_address required"})
    
    managers = get_integration_managers()
    result = managers['utilities'].lookup_ip_address(ip_address)
    return jsonify(result)

@app.route('/api/utilities/snmp-discovery', methods=['POST'])
def run_unified_snmp_discovery():
    """POST /api/utilities/snmp-discovery - Run unified SNMP discovery"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    brand = data.get('brand')
    
    managers = get_integration_managers()
    result = managers['utilities'].run_unified_snmp_discovery(brand)
    return jsonify(result)

# Dashboard Integration (fortimanagerdashboard project)
@app.route('/api/dashboard/capabilities', methods=['GET'])
def get_dashboard_capabilities():
    """GET /api/dashboard/capabilities - Get available dashboard features"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['dashboard'].get_dashboard_capabilities()
    return jsonify(result)

@app.route('/api/dashboard/fortimanager/<fortimanager_name>/advanced', methods=['GET'])
def get_advanced_fortimanager_data(fortimanager_name):
    """GET /api/dashboard/fortimanager/{name}/advanced - Get advanced FortiManager data"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['dashboard'].get_advanced_fortimanager_data(fortimanager_name)
    return jsonify(result)

@app.route('/api/dashboard/ssl/analysis', methods=['POST'])
def run_ssl_certificate_analysis():
    """POST /api/dashboard/ssl/analysis - Run comprehensive SSL certificate analysis"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    device_ip = data.get('device_ip')
    port = data.get('port', 443)
    
    if not device_ip:
        return jsonify({"success": False, "error": "device_ip required"})
    
    managers = get_integration_managers()
    result = managers['dashboard'].run_ssl_certificate_analysis(device_ip, port)
    return jsonify(result)

@app.route('/api/dashboard/ssl/corporate-solutions', methods=['POST'])
def get_corporate_ssl_solutions():
    """POST /api/dashboard/ssl/corporate-solutions - Get corporate SSL bypass solutions"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    data = request.get_json() or {}
    ssl_issue_type = data.get('ssl_issue_type', 'cert_validation')
    
    managers = get_integration_managers()
    result = managers['dashboard'].get_corporate_ssl_solutions(ssl_issue_type)
    return jsonify(result)

@app.route('/api/dashboard/operations', methods=['GET'])
def get_enhanced_api_operations():
    """GET /api/dashboard/operations - Get enhanced API operations"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['dashboard'].get_enhanced_api_operations()
    return jsonify(result)

@app.route('/api/dashboard/components/merge', methods=['GET'])
def merge_dashboard_components():
    """GET /api/dashboard/components/merge - Merge dashboard components"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['dashboard'].merge_dashboard_components()
    return jsonify(result)

# ==============================================================================
# FORTIANALYZER INTEGRATION API ENDPOINTS
# Log collection, analysis, and security intelligence from FortiAnalyzer
# ==============================================================================

@app.route('/api/fortianalyzer/instances', methods=['GET'])
def get_fortianalyzer_instances():
    """GET /api/fortianalyzer/instances - Get FortiAnalyzer instances"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['fortianalyzer'].get_fortianalyzer_instances()
    return jsonify(result)

@app.route('/api/fortianalyzer/logs/<brand>/<store_id>', methods=['GET'])
def get_security_logs(brand, store_id):
    """GET /api/fortianalyzer/logs/{brand}/{store_id} - Get security logs for store"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    timeframe = request.args.get('timeframe', '1h')
    log_type = request.args.get('log_type', 'traffic')
    
    managers = get_integration_managers()
    result = managers['fortianalyzer'].get_security_logs(brand, store_id, timeframe, log_type)
    return jsonify(result)

@app.route('/api/fortianalyzer/threats/<brand>', methods=['GET'])
def get_threat_intelligence(brand):
    """GET /api/fortianalyzer/threats/{brand} - Get threat intelligence for brand"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    timeframe = request.args.get('timeframe', '24h')
    
    managers = get_integration_managers()
    result = managers['fortianalyzer'].get_threat_intelligence(brand, timeframe)
    return jsonify(result)

@app.route('/api/fortianalyzer/analytics', methods=['GET'])
def get_log_analytics():
    """GET /api/fortianalyzer/analytics - Get log analytics and metrics"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    brand = request.args.get('brand')
    metric_type = request.args.get('metric_type', 'bandwidth')
    
    managers = get_integration_managers()
    result = managers['fortianalyzer'].get_log_analytics(brand, metric_type)
    return jsonify(result)

@app.route('/api/fortianalyzer/reports/<brand>', methods=['GET'])
def generate_security_report(brand):
    """GET /api/fortianalyzer/reports/{brand} - Generate security report"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    store_id = request.args.get('store_id')
    timeframe = request.args.get('timeframe', '7d')
    
    managers = get_integration_managers()
    result = managers['fortianalyzer'].generate_security_report(brand, store_id, timeframe)
    return jsonify(result)

@app.route('/api/fortianalyzer/search', methods=['GET'])
def search_logs():
    """GET /api/fortianalyzer/search - Search logs across FortiAnalyzer instances"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    query = request.args.get('query')
    brand = request.args.get('brand')
    timeframe = request.args.get('timeframe', '1h')
    
    if not query:
        return jsonify({"success": False, "error": "query parameter required"})
    
    managers = get_integration_managers()
    result = managers['fortianalyzer'].search_logs(query, brand, timeframe)
    return jsonify(result)

# ==============================================================================
# WEB FILTERS INTEGRATION API ENDPOINTS  
# Web filtering policies, SSL certificates, and log analysis
# ==============================================================================

@app.route('/api/webfilters/status', methods=['GET'])
def get_webfilters_status():
    """GET /api/webfilters/status - Get web filters application status"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['webfilters'].get_webfilters_status()
    return jsonify(result)

@app.route('/api/webfilters/server/start', methods=['POST'])
def start_webfilters_server():
    """POST /api/webfilters/server/start - Start web filters PowerShell server"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['webfilters'].start_webfilters_server()
    return jsonify(result)

@app.route('/api/webfilters/server/stop', methods=['POST'])
def stop_webfilters_server():
    """POST /api/webfilters/server/stop - Stop web filters PowerShell server"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['webfilters'].stop_webfilters_server()
    return jsonify(result)

@app.route('/api/webfilters/policies', methods=['GET'])
def get_web_filtering_policies():
    """GET /api/webfilters/policies - Get web filtering policies"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    brand = request.args.get('brand')
    
    managers = get_integration_managers()
    result = managers['webfilters'].get_web_filtering_policies(brand)
    return jsonify(result)

@app.route('/api/webfilters/<brand>/<store_id>', methods=['GET'])
def get_store_web_filters(brand, store_id):
    """GET /api/webfilters/{brand}/{store_id} - Get store web filtering config"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['webfilters'].get_store_web_filters(brand, store_id)
    return jsonify(result)

@app.route('/api/webfilters/analytics', methods=['GET'])
def get_web_filter_analytics():
    """GET /api/webfilters/analytics - Get web filtering analytics"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    brand = request.args.get('brand')
    timeframe = request.args.get('timeframe', '24h')
    
    managers = get_integration_managers()
    result = managers['webfilters'].get_web_filter_analytics(brand, timeframe)
    return jsonify(result)

@app.route('/api/webfilters/<brand>/<store_id>/policy', methods=['POST'])
def update_web_filter_policy(brand, store_id):
    """POST /api/webfilters/{brand}/{store_id}/policy - Update web filter policy"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    policy_data = request.get_json() or {}
    
    managers = get_integration_managers()
    result = managers['webfilters'].update_web_filter_policy(brand, store_id, policy_data)
    return jsonify(result)

@app.route('/api/webfilters/ssl/status', methods=['GET'])
def get_ssl_certificate_status():
    """GET /api/webfilters/ssl/status - Get SSL certificate and Vault status"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['webfilters'].get_ssl_certificate_status()
    return jsonify(result)

@app.route('/api/webfilters/logs/search', methods=['GET'])
def search_web_filter_logs():
    """GET /api/webfilters/logs/search - Search web filtering logs"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    query = request.args.get('query')
    brand = request.args.get('brand')
    timeframe = request.args.get('timeframe', '1h')
    
    if not query:
        return jsonify({"success": False, "error": "query parameter required"})
    
    managers = get_integration_managers()
    result = managers['webfilters'].search_web_filter_logs(query, brand, timeframe)
    return jsonify(result)

@app.route('/api/webfilters/integration/summary', methods=['GET'])
def get_webfilters_integration_summary():
    """GET /api/webfilters/integration/summary - Get webfilters integration summary"""
    if not INTEGRATIONS_AVAILABLE:
        return jsonify({"success": False, "error": "Integration modules not available"})
    
    managers = get_integration_managers()
    result = managers['webfilters'].get_webfilters_integration_summary()
    return jsonify(result)

@app.route('/api/integration/status', methods=['GET'])
def get_integration_status():
    """GET /api/integration/status - Get overall integration status"""
    status = {
        "success": True,
        "integrations_available": INTEGRATIONS_AVAILABLE,
        "integrated_projects": {
            "fortigatevlans": "VLAN management and configuration",
            "fortigate-troubleshooter": "Device diagnostics and troubleshooting", 
            "addfortiap": "FortiAP deployment and wireless management",
            "Utilities": "Network utilities and diagnostic tools",
            "fortimanagerdashboard": "Advanced dashboard features",
            "fortianalyzer": "Log collection, analysis, and security intelligence",
            "fortinet-webfilters-web": "Web filtering policies and SSL certificate management"
        },
        "new_api_endpoints": 65,
        "unified_platform_status": "fully_operational" if INTEGRATIONS_AVAILABLE else "limited_functionality",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    if INTEGRATIONS_AVAILABLE:
        managers = get_integration_managers()
        status["active_managers"] = list(managers.keys())
    
    return jsonify(status)

if __name__ == '__main__':
    print("🚀 Starting Network Device MCP Web Dashboard & REST API Server")
    print("=" * 60)
    print("🌐 Web Dashboard: http://localhost:5000")
    print("📊 API Documentation: http://localhost:5000/api")
    print("🏪 Example API: http://localhost:5000/api/stores/bww/155/security")
    print("=" * 60)
    print("📋 Your team can now access the web interface!")
    print("   - Store Investigation Tool")
    print("   - Brand Overviews (BWW, Arby's, Sonic)")
    print("   - FortiManager Status")
    print("   - Real-time Security Monitoring")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)