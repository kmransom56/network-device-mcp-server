# Network Device Management MCP Server

A comprehensive Model Context Protocol (MCP) server for managing FortiGate, FortiManager, and Cisco Meraki network devices. Built specifically for automation and integration with Claude Desktop and Power Automate workflows.

## 🚀 Features

### Supported Platforms
- **FortiGate**: Direct device management via REST API
- **FortiManager**: Centralized management via JSON-RPC API  
- **Cisco Meraki**: Cloud management via Dashboard API

### Core Capabilities
- **Device Status Monitoring**: Real-time system status, interfaces, and performance metrics
- **Configuration Management**: View and modify device configurations
- **Policy Management**: Firewall policies, VPN tunnels, and security rules
- **Network Discovery**: Automatic device discovery and inventory
- **Security Events**: Monitor and analyze security logs and events
- **Multi-Platform Reports**: Unified view across all managed devices

## 📋 Requirements

- Python 3.8 or higher
- Claude Desktop (for MCP integration)
- Network access to your devices
- Valid API credentials for each platform

## 🔧 Installation

### Quick Start
1. **Clone/Download** this repository to `C:\Users\keith.ransom\network-device-mcp-server`
2. **Run the installer**:
   ```cmd
   install.bat
   ```
3. **Configure your devices**:
   ```cmd
   notepad config\devices.json.user
   ```
4. **Add to Claude Desktop**:
   ```cmd
   setup-claude-config.bat
   ```
5. **Test the server**:
   ```cmd
   test-server.bat
   ```

### Manual Installation
```cmd
# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
copy config\devices.json config\devices.json.user
```

## ⚙️ Configuration

Edit `config/devices.json.user` with your actual device credentials:

### FortiGate Configuration
```json
{
  "fortigate": [
    {
      "name": "FortiGate-Main",
      "host": "192.168.1.99", 
      "token": "your-api-token-here",
      "description": "Main firewall"
    }
  ]
}
```

**To get FortiGate API token:**
1. Login to FortiGate web interface
2. Go to System > Administrators  
3. Create new REST API Admin or edit existing
4. Generate API token and copy it

### FortiManager Configuration
```json
{
  "fortimanager": [
    {
      "name": "FortiManager-Primary",
      "host": "192.168.1.100",
      "username": "admin", 
      "password": "your-password-here",
      "description": "Central management"
    }
  ]
}
```

### Meraki Configuration
```json
{
  "meraki": [
    {
      "name": "Meraki-Dashboard",
      "api_key": "your-meraki-api-key-here",
      "org_id": "your-organization-id",
      "description": "Cloud dashboard"
    }
  ]
}
```

**To get Meraki API key:**
1. Login to Meraki Dashboard
2. Go to Organization > Settings > Dashboard API access
3. Enable API access and generate key
4. Find your Organization ID in the URL or API

## 🛠️ Available Tools

### FortiGate Tools
- `get_fortigate_system_status` - System info, CPU, memory, uptime
- `get_fortigate_interfaces` - Network interface status and statistics  
- `get_fortigate_policies` - Firewall policy configuration
- `get_fortigate_vpn_status` - VPN tunnel status
- `get_fortigate_security_events` - Recent security logs

### FortiManager Tools  
- `get_fortimanager_devices` - List all managed devices
- `get_fortimanager_adoms` - Administrative domains
- `install_fortimanager_policy` - Push policies to devices
- `get_policy_packages` - Available policy packages

### Meraki Tools
- `get_meraki_organizations` - Your Meraki organizations
- `get_meraki_networks` - Networks in organization
- `get_meraki_devices` - Devices in network  
- `get_meraki_device_status` - Device online/offline status
- `update_meraki_device` - Update device configuration
- `get_network_clients` - Connected clients
- `get_security_events` - Security event logs

### Multi-Platform Tools
- `get_network_summary` - Unified status across all platforms

## 🔗 Power Automate Integration

### Method 1: File-Based Integration
```python
# Example: Export device status to file for Power Automate monitoring
async def export_status_for_pa():
    status = await get_network_summary()
    with open('C:/temp/network_status.json', 'w') as f:
        json.dump(status, f)
```

### Method 2: REST API Wrapper
Create a simple Flask wrapper around MCP tools:
```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/network/status')
def get_status():
    # Call MCP tools and return results
    return jsonify(network_status)
```

### Method 3: Database Integration
- Export data to SQL Server/Excel
- Power Automate reads from shared database
- Trigger workflows based on device status changes

## 📊 Example Use Cases

### Device Health Monitoring
```plaintext
Claude: "Show me the status of all FortiGate devices"
MCP Server: Returns system status, CPU, memory for all devices
Power Automate: Triggers alert if CPU > 80%
```

### Policy Deployment
```plaintext
Claude: "Install the 'Guest_Access' policy to all branch firewalls"  
MCP Server: Uses FortiManager to push policy
Power Automate: Sends deployment confirmation email
```

### Network Inventory
```plaintext
Claude: "Generate a report of all Meraki devices"
MCP Server: Collects device info from all networks
Power Automate: Creates Excel report and emails to team
```

## 🚨 Troubleshooting

### Common Issues

**"Module not found" errors:**
```cmd
# Ensure virtual environment is activated
venv\Scripts\activate.bat
pip install -r requirements.txt
```

**"Connection refused" errors:**
- Check device IP addresses and network connectivity
- Verify API credentials are correct
- Ensure devices allow API access from your IP

**Claude Desktop doesn't show tools:**
- Restart Claude Desktop completely
- Check `%APPDATA%\Claude\claude_desktop_config.json` 
- Run `test-server.bat` to verify server starts

**FortiGate API issues:**
- Enable REST API in System > Feature Visibility
- Check API admin user has proper permissions
- Verify HTTPS certificate settings

**Meraki API issues:**  
- Ensure API access is enabled in organization settings
- Check API key has proper permissions
- Verify organization ID is correct

### Debug Mode
Enable detailed logging by setting environment variable:
```cmd
set MCP_LOG_LEVEL=DEBUG
python src\main.py
```

### Logs Location
- Server logs: `logs/network-mcp-server.log`
- Claude MCP logs: `%LOCALAPPDATA%\Claude\logs\`

## 🔐 Security Best Practices

1. **Use dedicated API accounts** with minimal required permissions
2. **Store credentials securely** - consider using environment variables
3. **Enable firewall rules** to restrict API access to your IP
4. **Regularly rotate API keys** and tokens
5. **Monitor API usage** for suspicious activity
6. **Use HTTPS only** for all API communications

## 📈 Advanced Features

### Custom Device Types
Extend the server to support additional devices:
```python
# Add new platform module in src/platforms/
class CustomDeviceManager:
    async def get_device_status(self, host, credentials):
        # Implement your device API calls
        pass
```

### Automated Backups
Schedule configuration backups:
```python
# Example backup automation
@scheduler.scheduled_job('cron', hour=2)  # Run daily at 2 AM
async def backup_all_configs():
    for device in fortigate_devices:
        config = await backup_config(device)
        save_backup(config, device['name'])
```

### Custom Reporting
Generate tailored reports for your environment:
```python
async def generate_security_report():
    events = await get_all_security_events()
    threats = analyze_threat_patterns(events)
    return create_executive_summary(threats)
```

## 📞 Support

### Getting Help
1. Check the troubleshooting section above
2. Review logs for specific error messages
3. Test individual components with `test-server.bat`
4. Verify network connectivity to your devices

### Feature Requests
This MCP server is designed to be extensible. Common enhancement requests:
- Additional device platform support
- Custom reporting templates  
- Automated remediation actions
- Integration with SIEM systems
- Mobile device management

## 🎯 Integration with Your Existing Projects

Based on your directory structure, you already have several Fortinet projects:
- `fortigatevlans/` - Can integrate VLAN management
- `fortigate-troubleshooter/` - Can incorporate troubleshooting workflows  
- `fortimanagerdashboard/` - Can extend with MCP capabilities
- `meraki_visualizations/` - Can add MCP data sources

The MCP server can serve as a unified API layer across all these projects!

---

## 📄 License
MIT License - Feel free to modify and extend for your needs.

Built for network administrators who want to automate device management and integrate with modern AI tools like Claude and Power Automate.