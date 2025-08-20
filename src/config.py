"""
Configuration loader for Network Device MCP Server
Loads configuration from environment variables (.env file)
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class NetworkDeviceConfig:
    def __init__(self, env_file: str = ".env"):
        """Initialize configuration from environment variables"""
        
        # Load .env file if it exists
        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.info(f"Loaded configuration from {env_file}")
        else:
            logger.warning(f"Environment file {env_file} not found, using system environment variables")
        
        self._load_config()
    
    def _load_config(self):
        """Load all configuration from environment variables"""
        
        # Server configuration
        self.log_level = os.getenv("MCP_LOG_LEVEL", "INFO")
        self.timeout = int(os.getenv("MCP_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.backup_path = os.getenv("BACKUP_PATH", "C:\\temp\\network-backups")
        self.report_path = os.getenv("REPORT_PATH", "C:\\temp\\network-reports")
        
        # Meraki configuration
        self.meraki_api_key = os.getenv("MERAKI_API_KEY", "")
        self.meraki_org_id = os.getenv("MERAKI_ORG_ID", "")
        
        # Load FortiManager instances
        self.fortimanager_instances = self._load_fortimanager_instances()
        
        # Load FortiGate devices
        self.fortigate_devices = self._load_fortigate_devices()
        
        logger.info(f"Loaded configuration: {len(self.fortimanager_instances)} FortiManager instances, {len(self.fortigate_devices)} FortiGate devices")
    
    def _load_fortimanager_instances(self) -> List[Dict]:
        """Load FortiManager instances from environment variables"""
        instances = []
        
        # Known instances based on your setup
        fm_configs = [
            ("ARBYS", "Arbys"),
            ("BWW", "BWW"), 
            ("SONIC", "Sonic")
        ]
        
        for env_prefix, display_name in fm_configs:
            host = os.getenv(f"FM_{env_prefix}_HOST")
            username = os.getenv(f"FM_{env_prefix}_USERNAME")
            password = os.getenv(f"FM_{env_prefix}_PASSWORD")
            name = os.getenv(f"FM_{env_prefix}_NAME", display_name)
            
            if host and username and password:
                instances.append({
                    "name": name,
                    "host": host,
                    "username": username,
                    "password": password,
                    "description": f"FortiManager for {display_name}"
                })
                logger.info(f"Loaded FortiManager instance: {name} ({host})")
            else:
                logger.warning(f"Incomplete FortiManager config for {env_prefix}")
        
        # Also check for numbered instances (FM_1_HOST, etc.)
        for i in range(1, 10):  # Support up to 9 additional instances
            host = os.getenv(f"FM_{i}_HOST")
            username = os.getenv(f"FM_{i}_USERNAME")
            password = os.getenv(f"FM_{i}_PASSWORD")
            name = os.getenv(f"FM_{i}_NAME", f"FortiManager-{i}")
            
            if host and username and password:
                instances.append({
                    "name": name,
                    "host": host,
                    "username": username,
                    "password": password,
                    "description": f"FortiManager instance {i}"
                })
                logger.info(f"Loaded FortiManager instance: {name} ({host})")
        
        return instances
    
    def _load_fortigate_devices(self) -> List[Dict]:
        """Load FortiGate devices from environment variables"""
        devices = []
        
        # Check for numbered FortiGate instances
        for i in range(1, 20):  # Support up to 19 FortiGate devices
            host = os.getenv(f"FG_HOST_{i}")
            token = os.getenv(f"FG_TOKEN_{i}")
            name = os.getenv(f"FG_NAME_{i}", f"FortiGate-{i}")
            
            if host and token:
                devices.append({
                    "name": name,
                    "host": host,
                    "token": token,
                    "description": f"FortiGate device {i}"
                })
                logger.info(f"Loaded FortiGate device: {name} ({host})")
        
        return devices
    
    def get_fortimanager_by_name(self, name: str) -> Optional[Dict]:
        """Get FortiManager instance by name"""
        for instance in self.fortimanager_instances:
            if instance["name"].lower() == name.lower():
                return instance
        return None
    
    def get_fortigate_by_name(self, name: str) -> Optional[Dict]:
        """Get FortiGate device by name"""
        for device in self.fortigate_devices:
            if device["name"].lower() == name.lower():
                return device
        return None
    
    def list_fortimanager_names(self) -> List[str]:
        """Get list of FortiManager instance names"""
        return [fm["name"] for fm in self.fortimanager_instances]
    
    def list_fortigate_names(self) -> List[str]:
        """Get list of FortiGate device names"""
        return [fg["name"] for fg in self.fortigate_devices]
    
    def has_meraki_config(self) -> bool:
        """Check if Meraki configuration is available"""
        return bool(self.meraki_api_key and self.meraki_org_id)
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration and return status"""
        return {
            "fortimanager_configured": len(self.fortimanager_instances) > 0,
            "fortigate_configured": len(self.fortigate_devices) > 0,
            "meraki_configured": self.has_meraki_config(),
            "backup_path_exists": os.path.exists(self.backup_path),
            "report_path_exists": os.path.exists(self.report_path)
        }
    
    def create_directories(self):
        """Create necessary directories"""
        for path in [self.backup_path, self.report_path]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                logger.info(f"Created directory: {path}")

# Global configuration instance
config = None

def get_config(env_file: str = ".env") -> NetworkDeviceConfig:
    """Get global configuration instance"""
    global config
    if config is None:
        config = NetworkDeviceConfig(env_file)
        config.create_directories()
    return config
