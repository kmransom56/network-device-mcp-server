#!/usr/bin/env python3
"""
Network Device Management MCP Server
Supports FortiManager, FortiGate, and Cisco Meraki platforms
Uses .env file for secure credential management
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

import httpx
from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest, 
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

# Import our modules
from config import get_config
from platforms.fortigate import FortiGateManager
from platforms.fortimanager import FortiManagerManager  
from platforms.meraki import MerakiManager

# Set up logging to stderr (not stdout for MCP)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

class NetworkDeviceMCPServer:
    def __init__(self):
        self.server = Server("network-device-mcp")
        
        # Load configuration
        self.config = get_config()
        
        # Initialize platform managers
        self.fortigate = FortiGateManager()
        self.fortimanager = FortiManagerManager()
        self.meraki = MerakiManager()
        
        # Set up tool handlers
        self.setup_tools()
    
    def setup_tools(self):
        """Register all available tools"""
        
        # Register the tool list handler
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            tools = [
                # FortiManager Tools
                Tool(
                    name="list_fortimanager_instances",
                    description="List all available FortiManager instances (Arbys, BWW, Sonic)",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_fortimanager_devices",
                    description="Get managed devices from a FortiManager instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "fortimanager_name": {"type": "string", "description": "FortiManager name (Arbys, BWW, or Sonic)"},
                            "adom": {"type": "string", "default": "root", "description": "Administrative domain"}
                        },
                        "required": ["fortimanager_name"]
                    }
                ),
                Tool(
                    name="get_policy_packages",
                    description="Get policy packages from a FortiManager instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "fortimanager_name": {"type": "string", "description": "FortiManager name (Arbys, BWW, or Sonic)"},
                            "adom": {"type": "string", "default": "root"}
                        },
                        "required": ["fortimanager_name"]
                    }
                ),
                Tool(
                    name="install_policy_package",
                    description="Install policy package to devices via FortiManager",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "fortimanager_name": {"type": "string", "description": "FortiManager name (Arbys, BWW, or Sonic)"},
                            "adom": {"type": "string", "default": "root"},
                            "package": {"type": "string", "description": "Policy package name"},
                            "devices": {"type": "array", "items": {"type": "string"}, "description": "Target device names"}
                        },
                        "required": ["fortimanager_name", "package"]
                    }
                ),
                
                # Infrastructure Summary Tools
                Tool(
                    name="get_network_infrastructure_summary",
                    description="Get comprehensive summary of all managed network infrastructure",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="show_configuration_status",
                    description="Show current MCP server configuration status",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
            
            # Add FortiGate tools if devices are configured
            if self.config.fortigate_devices:
                tools.extend([
                    Tool(
                        name="list_fortigate_devices",
                        description="List all available FortiGate devices",
                        inputSchema={"type": "object", "properties": {}}
                    ),
                    Tool(
                        name="get_fortigate_system_status",
                        description="Get system status from a FortiGate device",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "fortigate_name": {"type": "string", "description": "FortiGate device name"}
                            },
                            "required": ["fortigate_name"]
                        }
                    )
                ])
            
            # Add Meraki tools if configured
            if self.config.has_meraki_config():
                tools.extend([
                    Tool(
                        name="get_meraki_organizations",
                        description="Get Meraki organizations",
                        inputSchema={"type": "object", "properties": {}}
                    ),
                    Tool(
                        name="get_meraki_networks",
                        description="Get networks in the configured Meraki organization",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "org_id": {"type": "string", "description": "Organization ID (optional)"}
                            }
                        }
                    ),
                    Tool(
                        name="get_meraki_devices",
                        description="Get devices in a Meraki network",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "network_id": {"type": "string", "description": "Network ID"}
                            },
                            "required": ["network_id"]
                        }
                    )
                ])
            
            return tools
        
        # FortiManager Tools (Multiple Instances)
        @self.server.call_tool()
        async def list_fortimanager_instances(arguments: dict) -> list[TextContent]:
            """List all available FortiManager instances"""
            try:
                instances = []
                for fm in self.config.fortimanager_instances:
                    instances.append({
                        "name": fm["name"],
                        "host": fm["host"],
                        "description": fm.get("description", "")
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps(instances, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error listing FortiManager instances: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.call_tool()
        async def get_fortimanager_devices(arguments: dict) -> list[TextContent]:
            """Get managed devices from a FortiManager instance"""
            try:
                fm_name = arguments.get("fortimanager_name", "")
                adom = arguments.get("adom", "root")
                
                if not fm_name:
                    available = self.config.list_fortimanager_names()
                    return [TextContent(
                        type="text", 
                        text=f"Error: fortimanager_name required. Available: {', '.join(available)}"
                    )]
                
                fm_config = self.config.get_fortimanager_by_name(fm_name)
                if not fm_config:
                    return [TextContent(type="text", text=f"Error: FortiManager '{fm_name}' not found")]
                
                result = await self.fortimanager.get_managed_devices(
                    fm_config["host"], fm_config["username"], fm_config["password"], adom
                )
                
                # Add FortiManager info to results
                response = {
                    "fortimanager": fm_name,
                    "host": fm_config["host"],
                    "adom": adom,
                    "device_count": len(result),
                    "devices": result
                }
                
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.call_tool()
        async def install_policy_package(arguments: dict) -> list[TextContent]:
            """Install policy package to devices via FortiManager"""
            try:
                fm_name = arguments.get("fortimanager_name", "")
                adom = arguments.get("adom", "root")
                package = arguments.get("package")
                devices = arguments.get("devices", [])
                
                if not fm_name or not package:
                    available = self.config.list_fortimanager_names()
                    return [TextContent(
                        type="text",
                        text=f"Error: fortimanager_name and package required. Available FortiManagers: {', '.join(available)}"
                    )]
                
                fm_config = self.config.get_fortimanager_by_name(fm_name)
                if not fm_config:
                    return [TextContent(type="text", text=f"Error: FortiManager '{fm_name}' not found")]
                
                result = await self.fortimanager.install_policy_package(
                    fm_config["host"], fm_config["username"], fm_config["password"],
                    adom, package, devices
                )
                
                # Add context to result
                response = {
                    "fortimanager": fm_name,
                    "host": fm_config["host"], 
                    "adom": adom,
                    "package": package,
                    "target_devices": devices,
                    "result": result
                }
                
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.call_tool()
        async def get_policy_packages(arguments: dict) -> list[TextContent]:
            """Get policy packages from a FortiManager instance"""
            try:
                fm_name = arguments.get("fortimanager_name", "")
                adom = arguments.get("adom", "root")
                
                if not fm_name:
                    available = self.config.list_fortimanager_names()
                    return [TextContent(
                        type="text",
                        text=f"Error: fortimanager_name required. Available: {', '.join(available)}"
                    )]
                
                fm_config = self.config.get_fortimanager_by_name(fm_name)
                if not fm_config:
                    return [TextContent(type="text", text=f"Error: FortiManager '{fm_name}' not found")]
                
                result = await self.fortimanager.get_policy_packages(
                    fm_config["host"], fm_config["username"], fm_config["password"], adom
                )
                
                response = {
                    "fortimanager": fm_name,
                    "host": fm_config["host"],
                    "adom": adom,
                    "package_count": len(result),
                    "packages": result
                }
                
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        # FortiGate Tools (if configured)
        @self.server.call_tool()
        async def list_fortigate_devices(arguments: dict) -> list[TextContent]:
            """List all available FortiGate devices"""
            try:
                devices = []
                for fg in self.config.fortigate_devices:
                    devices.append({
                        "name": fg["name"],
                        "host": fg["host"],
                        "description": fg.get("description", "")
                    })
                
                return [TextContent(type="text", text=json.dumps(devices, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.call_tool()
        async def get_fortigate_system_status(arguments: dict) -> list[TextContent]:
            """Get system status from a FortiGate device"""
            try:
                fg_name = arguments.get("fortigate_name", "")
                
                if not fg_name:
                    available = self.config.list_fortigate_names()
                    return [TextContent(
                        type="text",
                        text=f"Error: fortigate_name required. Available: {', '.join(available)}"
                    )]
                
                fg_config = self.config.get_fortigate_by_name(fg_name)
                if not fg_config:
                    return [TextContent(type="text", text=f"Error: FortiGate '{fg_name}' not found")]
                
                result = await self.fortigate.get_system_status(fg_config["host"], fg_config["token"])
                
                response = {
                    "fortigate": fg_name,
                    "host": fg_config["host"],
                    "status": result
                }
                
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        # Meraki Tools (if configured)
        @self.server.call_tool()
        async def get_meraki_organizations(arguments: dict) -> list[TextContent]:
            """Get Meraki organizations"""
            try:
                if not self.config.has_meraki_config():
                    return [TextContent(type="text", text="Error: Meraki API key not configured")]
                
                result = await self.meraki.get_organizations(self.config.meraki_api_key)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.call_tool()
        async def get_meraki_networks(arguments: dict) -> list[TextContent]:
            """Get networks in the configured Meraki organization"""
            try:
                if not self.config.has_meraki_config():
                    return [TextContent(type="text", text="Error: Meraki configuration not available")]
                
                org_id = arguments.get("org_id", self.config.meraki_org_id)
                result = await self.meraki.get_networks(self.config.meraki_api_key, org_id)
                
                response = {
                    "organization_id": org_id,
                    "network_count": len(result),
                    "networks": result
                }
                
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.call_tool()
        async def get_meraki_devices(arguments: dict) -> list[TextContent]:
            """Get devices in a Meraki network"""
            try:
                if not self.config.has_meraki_config():
                    return [TextContent(type="text", text="Error: Meraki configuration not available")]
                
                network_id = arguments.get("network_id")
                if not network_id:
                    return [TextContent(type="text", text="Error: network_id required")]
                
                result = await self.meraki.get_devices(self.config.meraki_api_key, network_id)
                
                response = {
                    "network_id": network_id,
                    "device_count": len(result),
                    "devices": result
                }
                
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        # Multi-platform summary tool
        @self.server.call_tool()
        async def get_network_infrastructure_summary(arguments: dict) -> list[TextContent]:
            """Get comprehensive summary of all managed network infrastructure"""
            try:
                summary = {
                    "infrastructure_overview": {
                        "fortimanager_instances": len(self.config.fortimanager_instances),
                        "fortigate_devices": len(self.config.fortigate_devices),
                        "meraki_configured": self.config.has_meraki_config()
                    },
                    "fortimanager_instances": [],
                    "fortigate_devices": [],
                    "meraki_info": {},
                    "configuration_status": self.config.validate_config()
                }
                
                # Get FortiManager summaries
                for fm in self.config.fortimanager_instances:
                    try:
                        devices = await self.fortimanager.get_managed_devices(
                            fm["host"], fm["username"], fm["password"]
                        )
                        summary["fortimanager_instances"].append({
                            "name": fm["name"],
                            "host": fm["host"], 
                            "managed_devices": len(devices),
                            "status": "online"
                        })
                    except Exception as e:
                        summary["fortimanager_instances"].append({
                            "name": fm["name"],
                            "host": fm["host"],
                            "status": "error",
                            "error": str(e)
                        })
                
                # Get Meraki summary if configured
                if self.config.has_meraki_config():
                    try:
                        orgs = await self.meraki.get_organizations(self.config.meraki_api_key)
                        networks = await self.meraki.get_networks(
                            self.config.meraki_api_key, self.config.meraki_org_id
                        )
                        summary["meraki_info"] = {
                            "organizations": len(orgs),
                            "networks": len(networks),
                            "status": "configured"
                        }
                    except Exception as e:
                        summary["meraki_info"] = {
                            "status": "error",
                            "error": str(e)
                        }
                
                return [TextContent(type="text", text=json.dumps(summary, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        # Configuration and status tools
        @self.server.call_tool()
        async def show_configuration_status(arguments: dict) -> list[TextContent]:
            """Show current configuration status"""
            try:
                status = {
                    "configuration_file": ".env",
                    "fortimanager_instances": [
                        {"name": fm["name"], "host": fm["host"]} 
                        for fm in self.config.fortimanager_instances
                    ],
                    "fortigate_devices": [
                        {"name": fg["name"], "host": fg["host"]} 
                        for fg in self.config.fortigate_devices
                    ],
                    "meraki_configured": self.config.has_meraki_config(),
                    "paths": {
                        "backup_path": self.config.backup_path,
                        "report_path": self.config.report_path
                    },
                    "validation": self.config.validate_config()
                }
                
                return [TextContent(type="text", text=json.dumps(status, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

from mcp.server.models import InitializationOptions, ServerCapabilities # Ensure these imports are present
from mcp.server import NotificationOptions # Also needed for capabilities

async def main():
    """Main execution function to run the MCP server with stdio transport."""
    network_server_instance = NetworkDeviceMCPServer()
    logger.info("Starting Network Device MCP Server")

    # Define the capabilities your server supports.
    # For stdio, NotificationOptions is usually a good starting point.
    capabilities = ServerCapabilities(
        notificationOptions=NotificationOptions(), # Or customize if needed
        # Add other capabilities if your server supports them
    )

    # Create the InitializationOptions object with the required fields
    initialization_options = InitializationOptions(
        server_name=network_server_instance.server.name, # Use the name defined in your Server instance
        server_version="1.0.0", # Specify a version for your server
        capabilities=capabilities
    )

    async with stdio_server() as (read_stream, write_stream):
        # Pass the streams AND the initialization_options to the Server object's run method
        await network_server_instance.server.run(
            read_stream, 
            write_stream, 
            initialization_options
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shut down by user.")
    except Exception as e:
        logger.error(f"A top-level error occurred: {e}", exc_info=True)