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

# Initialize Flask app with web template folder
app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')
CORS(app)  # Enable CORS for web access

# Initialize MCP server
mcp_server = None

def get_mcp_server():
    global mcp_server
    if mcp_server is None:
        mcp_server = NetworkDeviceMCPServer()
    return mcp_server

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