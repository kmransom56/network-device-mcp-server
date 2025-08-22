"""
FortiAnalyzer Integration
Manages FortiAnalyzer log collection, analysis, and reporting functionality
"""

import os
import sys
import json
import sqlite3
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import urllib3

# Disable SSL warnings for FortiAnalyzer connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FortiAnalyzerManager:
    """
    Manages FortiAnalyzer operations for log analysis and security intelligence
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize FortiAnalyzer Manager
        
        Args:
            config_path: Path to FortiAnalyzer configuration
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'config.py')
        self.sessions = {}  # Track active FortiAnalyzer sessions
        self.log_cache = {}  # Cache recent log queries
        
    def get_fortianalyzer_instances(self) -> Dict[str, Any]:
        """
        Get configured FortiAnalyzer instances
        
        Returns:
            Dictionary containing FortiAnalyzer instances and their configurations
        """
        try:
            # Import configuration
            sys.path.insert(0, os.path.dirname(self.config_path))
            from config import NetworkConfig
            
            config = NetworkConfig()
            
            # Get FortiAnalyzer configurations
            faz_instances = {
                "success": True,
                "fortianalyzer_instances": [
                    {
                        "name": "Corporate-FAZ",
                        "host": "10.128.144.100",  # Example IP - replace with actual
                        "description": "Corporate FortiAnalyzer for all brands",
                        "adom": "root",
                        "version": "7.2.1",
                        "status": "active"
                    },
                    {
                        "name": "BWW-FAZ", 
                        "host": "10.128.145.100",  # Example IP - replace with actual
                        "description": "Buffalo Wild Wings FortiAnalyzer",
                        "adom": "BWW",
                        "version": "7.2.1", 
                        "status": "active"
                    },
                    {
                        "name": "ARBYS-FAZ",
                        "host": "10.128.144.100",  # Example IP - replace with actual
                        "description": "Arby's FortiAnalyzer",
                        "adom": "ARBYS",
                        "version": "7.2.1",
                        "status": "active"
                    },
                    {
                        "name": "SONIC-FAZ",
                        "host": "10.128.156.100",  # Example IP - replace with actual
                        "description": "Sonic FortiAnalyzer", 
                        "adom": "SONIC",
                        "version": "7.2.1",
                        "status": "active"
                    }
                ],
                "total_instances": 4,
                "active_instances": 4
            }
            
            return faz_instances
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get FortiAnalyzer instances: {str(e)}"
            }
    
    def get_security_logs(self, brand: str, store_id: str, timeframe: str = "1h", 
                         log_type: str = "traffic") -> Dict[str, Any]:
        """
        Get security logs for a specific store from FortiAnalyzer
        
        Args:
            brand: Restaurant brand (BWW, ARBYS, SONIC)
            store_id: Store identifier
            timeframe: Time range (1h, 24h, 7d, 30d)
            log_type: Type of logs (traffic, utm, event, system)
            
        Returns:
            Security logs and analysis
        """
        try:
            device_name = f"IBR-{brand.upper()}-{store_id.zfill(5)}"
            
            # Get FortiAnalyzer instance for brand
            faz_instance = self._get_brand_fortianalyzer(brand)
            if not faz_instance:
                return {
                    "success": False,
                    "error": f"No FortiAnalyzer configured for brand {brand}"
                }
            
            # Query logs from FortiAnalyzer
            log_data = self._query_fortianalyzer_logs(faz_instance, device_name, timeframe, log_type)
            
            if log_data:
                # Analyze logs
                analysis = self._analyze_security_logs(log_data, log_type)
                
                return {
                    "success": True,
                    "device_name": device_name,
                    "brand": brand,
                    "store_id": store_id,
                    "timeframe": timeframe,
                    "log_type": log_type,
                    "fortianalyzer": faz_instance["name"],
                    "total_logs": len(log_data),
                    "logs": log_data[:100],  # Return first 100 logs
                    "analysis": analysis,
                    "query_time": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "device_name": device_name,
                    "total_logs": 0,
                    "message": "No logs found for the specified criteria",
                    "query_time": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get security logs: {str(e)}"
            }
    
    def get_threat_intelligence(self, brand: str, timeframe: str = "24h") -> Dict[str, Any]:
        """
        Get threat intelligence summary for a brand
        
        Args:
            brand: Restaurant brand
            timeframe: Time range for analysis
            
        Returns:
            Threat intelligence summary
        """
        try:
            faz_instance = self._get_brand_fortianalyzer(brand)
            if not faz_instance:
                return {
                    "success": False,
                    "error": f"No FortiAnalyzer configured for brand {brand}"
                }
            
            # Query threat intelligence data
            threat_data = self._query_threat_intelligence(faz_instance, brand, timeframe)
            
            return {
                "success": True,
                "brand": brand,
                "timeframe": timeframe,
                "fortianalyzer": faz_instance["name"],
                "threat_summary": {
                    "total_threats": threat_data.get("total_threats", 0),
                    "blocked_threats": threat_data.get("blocked_threats", 0),
                    "malware_detections": threat_data.get("malware", 0),
                    "intrusion_attempts": threat_data.get("intrusion", 0),
                    "web_filtering_blocks": threat_data.get("webfilter", 0)
                },
                "top_threats": threat_data.get("top_threats", []),
                "threat_trends": threat_data.get("trends", {}),
                "affected_stores": threat_data.get("affected_stores", []),
                "recommendations": self._generate_threat_recommendations(threat_data),
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get threat intelligence: {str(e)}"
            }
    
    def get_log_analytics(self, brand: str = None, metric_type: str = "bandwidth") -> Dict[str, Any]:
        """
        Get log analytics and metrics
        
        Args:
            brand: Optional brand filter
            metric_type: Type of metrics (bandwidth, sessions, threats, compliance)
            
        Returns:
            Log analytics results
        """
        try:
            analytics_data = {
                "success": True,
                "metric_type": metric_type,
                "brand_filter": brand,
                "analytics": {}
            }
            
            if brand:
                faz_instance = self._get_brand_fortianalyzer(brand)
                if faz_instance:
                    brand_analytics = self._get_brand_analytics(faz_instance, brand, metric_type)
                    analytics_data["analytics"][brand] = brand_analytics
            else:
                # Get analytics for all brands
                brands = ["BWW", "ARBYS", "SONIC"]
                for brand_name in brands:
                    faz_instance = self._get_brand_fortianalyzer(brand_name)
                    if faz_instance:
                        brand_analytics = self._get_brand_analytics(faz_instance, brand_name, metric_type)
                        analytics_data["analytics"][brand_name] = brand_analytics
            
            # Generate summary
            analytics_data["summary"] = self._generate_analytics_summary(analytics_data["analytics"])
            analytics_data["analysis_time"] = datetime.now().isoformat()
            
            return analytics_data
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get log analytics: {str(e)}"
            }
    
    def generate_security_report(self, brand: str, store_id: str = None, 
                               timeframe: str = "7d") -> Dict[str, Any]:
        """
        Generate comprehensive security report
        
        Args:
            brand: Restaurant brand
            store_id: Optional specific store
            timeframe: Report time range
            
        Returns:
            Comprehensive security report
        """
        try:
            faz_instance = self._get_brand_fortianalyzer(brand)
            if not faz_instance:
                return {
                    "success": False,
                    "error": f"No FortiAnalyzer configured for brand {brand}"
                }
            
            # Collect report data
            report_data = {
                "success": True,
                "report_info": {
                    "brand": brand,
                    "store_id": store_id,
                    "timeframe": timeframe,
                    "fortianalyzer": faz_instance["name"],
                    "generation_time": datetime.now().isoformat()
                },
                "executive_summary": {},
                "threat_analysis": {},
                "traffic_analysis": {},
                "compliance_status": {},
                "recommendations": []
            }
            
            # Generate executive summary
            report_data["executive_summary"] = self._generate_executive_summary(
                faz_instance, brand, store_id, timeframe
            )
            
            # Generate threat analysis
            report_data["threat_analysis"] = self._generate_threat_analysis(
                faz_instance, brand, store_id, timeframe
            )
            
            # Generate traffic analysis
            report_data["traffic_analysis"] = self._generate_traffic_analysis(
                faz_instance, brand, store_id, timeframe
            )
            
            # Generate compliance status
            report_data["compliance_status"] = self._generate_compliance_status(
                faz_instance, brand, store_id, timeframe
            )
            
            # Generate recommendations
            report_data["recommendations"] = self._generate_security_recommendations(report_data)
            
            return report_data
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate security report: {str(e)}"
            }
    
    def search_logs(self, query: str, brand: str = None, timeframe: str = "1h") -> Dict[str, Any]:
        """
        Search logs across FortiAnalyzer instances
        
        Args:
            query: Search query/filter
            brand: Optional brand filter
            timeframe: Search time range
            
        Returns:
            Search results
        """
        try:
            search_results = {
                "success": True,
                "query": query,
                "brand_filter": brand,
                "timeframe": timeframe,
                "results": [],
                "total_matches": 0,
                "search_time": datetime.now().isoformat()
            }
            
            if brand:
                # Search specific brand
                faz_instance = self._get_brand_fortianalyzer(brand)
                if faz_instance:
                    brand_results = self._search_fortianalyzer_logs(faz_instance, query, timeframe)
                    search_results["results"].extend(brand_results)
            else:
                # Search all brands
                brands = ["BWW", "ARBYS", "SONIC"]
                for brand_name in brands:
                    faz_instance = self._get_brand_fortianalyzer(brand_name)
                    if faz_instance:
                        brand_results = self._search_fortianalyzer_logs(faz_instance, query, timeframe)
                        search_results["results"].extend(brand_results)
            
            search_results["total_matches"] = len(search_results["results"])
            
            return search_results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Log search failed: {str(e)}"
            }
    
    def _get_brand_fortianalyzer(self, brand: str) -> Optional[Dict[str, Any]]:
        """Get FortiAnalyzer instance for specific brand"""
        instances = self.get_fortianalyzer_instances()
        if instances.get("success"):
            for faz in instances["fortianalyzer_instances"]:
                if brand.upper() in faz["name"] or faz["adom"] == brand.upper():
                    return faz
            # Return corporate FAZ as fallback
            for faz in instances["fortianalyzer_instances"]:
                if "Corporate" in faz["name"]:
                    return faz
        return None
    
    def _query_fortianalyzer_logs(self, faz_instance: Dict[str, Any], device_name: str, 
                                timeframe: str, log_type: str) -> List[Dict[str, Any]]:
        """Query logs from FortiAnalyzer (placeholder implementation)"""
        # This would implement actual FortiAnalyzer API calls
        # For now, return mock data
        sample_logs = [
            {
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "device": device_name,
                "log_type": log_type,
                "severity": "high",
                "message": "IPS signature matched: SQL.Injection.Generic",
                "src_ip": "192.168.1.100",
                "dst_ip": "8.8.8.8",
                "action": "blocked"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat(),
                "device": device_name,
                "log_type": log_type,
                "severity": "medium", 
                "message": "Web filter violation: Social Networking",
                "src_ip": "192.168.1.101",
                "dst_ip": "facebook.com",
                "action": "blocked"
            }
        ]
        
        return sample_logs
    
    def _analyze_security_logs(self, log_data: List[Dict[str, Any]], log_type: str) -> Dict[str, Any]:
        """Analyze security logs and generate insights"""
        if not log_data:
            return {"total_events": 0, "insights": []}
        
        analysis = {
            "total_events": len(log_data),
            "severity_breakdown": {},
            "top_sources": {},
            "top_destinations": {},
            "action_summary": {},
            "insights": []
        }
        
        # Analyze log data
        for log_entry in log_data:
            # Severity breakdown
            severity = log_entry.get("severity", "unknown")
            analysis["severity_breakdown"][severity] = analysis["severity_breakdown"].get(severity, 0) + 1
            
            # Action summary
            action = log_entry.get("action", "unknown")
            analysis["action_summary"][action] = analysis["action_summary"].get(action, 0) + 1
            
            # Top sources
            src_ip = log_entry.get("src_ip", "unknown")
            analysis["top_sources"][src_ip] = analysis["top_sources"].get(src_ip, 0) + 1
        
        # Generate insights
        high_severity = analysis["severity_breakdown"].get("high", 0)
        if high_severity > 5:
            analysis["insights"].append(f"High number of high-severity events: {high_severity}")
        
        blocked_actions = analysis["action_summary"].get("blocked", 0)
        if blocked_actions > 0:
            analysis["insights"].append(f"Successfully blocked {blocked_actions} potential threats")
        
        return analysis
    
    def _query_threat_intelligence(self, faz_instance: Dict[str, Any], brand: str, timeframe: str) -> Dict[str, Any]:
        """Query threat intelligence from FortiAnalyzer"""
        # Mock threat intelligence data
        return {
            "total_threats": 1250,
            "blocked_threats": 1180,
            "malware": 45,
            "intrusion": 230,
            "webfilter": 905,
            "top_threats": [
                {"name": "SQL.Injection.Generic", "count": 45, "severity": "high"},
                {"name": "Social.Networking.Block", "count": 320, "severity": "medium"},
                {"name": "Malware.Detection", "count": 18, "severity": "critical"}
            ],
            "trends": {
                "threat_increase": 15,
                "most_active_hour": 14,
                "peak_threat_day": "Monday"
            },
            "affected_stores": ["00155", "00234", "00567"]
        }
    
    def _get_brand_analytics(self, faz_instance: Dict[str, Any], brand: str, metric_type: str) -> Dict[str, Any]:
        """Get analytics for specific brand"""
        # Mock analytics data
        return {
            "bandwidth_usage": {"total_gb": 1250.5, "peak_hours": ["09:00", "12:00", "18:00"]},
            "session_count": {"total_sessions": 45678, "avg_duration": "00:15:30"},
            "threat_metrics": {"threats_blocked": 234, "threat_rate": "2.1%"},
            "compliance_score": 88.5
        }
    
    def _generate_analytics_summary(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary across all brand analytics"""
        return {
            "total_brands": len(analytics),
            "overall_health": "good",
            "recommendations": ["Continue monitoring", "Review peak hour patterns"]
        }
    
    def _generate_executive_summary(self, faz_instance: Dict[str, Any], brand: str, 
                                  store_id: str, timeframe: str) -> Dict[str, Any]:
        """Generate executive summary for security report"""
        return {
            "overall_security_posture": "strong",
            "total_events_analyzed": 12450,
            "threats_blocked": 1180,
            "threat_block_rate": "94.4%",
            "key_findings": [
                "Threat activity within normal ranges",
                "Web filtering effectively blocking inappropriate content",
                "No critical security incidents detected"
            ]
        }
    
    def _generate_threat_analysis(self, faz_instance: Dict[str, Any], brand: str,
                                store_id: str, timeframe: str) -> Dict[str, Any]:
        """Generate threat analysis section"""
        return {
            "threat_categories": {
                "malware": {"count": 45, "trend": "decreasing"},
                "intrusion_attempts": {"count": 230, "trend": "stable"},
                "web_threats": {"count": 905, "trend": "increasing"}
            },
            "geographic_analysis": {"most_threats_from": "Unknown/VPN", "count": 156},
            "temporal_patterns": {"peak_threat_time": "14:00-16:00", "pattern": "business_hours"}
        }
    
    def _generate_traffic_analysis(self, faz_instance: Dict[str, Any], brand: str,
                                 store_id: str, timeframe: str) -> Dict[str, Any]:
        """Generate traffic analysis section"""
        return {
            "total_traffic_gb": 2456.7,
            "protocol_breakdown": {"HTTP/HTTPS": 85.2, "Other": 14.8},
            "bandwidth_utilization": {"peak": "18:00-20:00", "average_mbps": 25.4},
            "application_usage": {"Web Browsing": 45.2, "POS Systems": 35.8, "Other": 19.0}
        }
    
    def _generate_compliance_status(self, faz_instance: Dict[str, Any], brand: str,
                                  store_id: str, timeframe: str) -> Dict[str, Any]:
        """Generate compliance status section"""
        return {
            "pci_compliance": {"status": "compliant", "score": 95.2},
            "data_retention": {"status": "compliant", "retention_days": 90},
            "audit_readiness": {"status": "ready", "last_audit": "2024-01-15"},
            "policy_adherence": {"web_filtering": 98.5, "access_control": 96.8}
        }
    
    def _generate_security_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on report data"""
        recommendations = [
            "Continue monitoring threat trends for unusual patterns",
            "Review web filtering policies for optimal balance",
            "Consider implementing additional IPS signatures for emerging threats"
        ]
        
        # Add specific recommendations based on data
        threat_analysis = report_data.get("threat_analysis", {})
        if threat_analysis.get("threat_categories", {}).get("web_threats", {}).get("trend") == "increasing":
            recommendations.append("Investigate increasing web threat activity")
        
        return recommendations
    
    def _generate_threat_recommendations(self, threat_data: Dict[str, Any]) -> List[str]:
        """Generate threat-specific recommendations"""
        recommendations = []
        
        if threat_data.get("total_threats", 0) > 1000:
            recommendations.append("High threat volume detected - consider additional security measures")
        
        block_rate = (threat_data.get("blocked_threats", 0) / max(threat_data.get("total_threats", 1), 1)) * 100
        if block_rate < 90:
            recommendations.append("Threat block rate below 90% - review security policies")
        
        if not recommendations:
            recommendations.append("Threat protection is operating effectively")
        
        return recommendations
    
    def _search_fortianalyzer_logs(self, faz_instance: Dict[str, Any], query: str, 
                                 timeframe: str) -> List[Dict[str, Any]]:
        """Search logs in specific FortiAnalyzer instance"""
        # Mock search implementation
        return [
            {
                "faz_instance": faz_instance["name"],
                "timestamp": datetime.now().isoformat(),
                "matching_entry": f"Log entry matching '{query}'",
                "relevance_score": 0.95
            }
        ]