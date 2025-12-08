"""
Network Monitor Tool (OpenAI-Compatible)
Monitors network connectivity, latency, and performs basic network diagnostics.
"""

import subprocess
import socket
import time
import platform
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

class NetworkMonitorTool:
    """
    OpenAI-compatible network monitoring tool for connectivity and performance analysis.
    Supports ping, traceroute, port scanning, and DNS lookups.
    """
    
    def __init__(self):
        """Initialize network monitor."""
        self.system = platform.system()
        
    def ping_host(self, host: str, count: int = 4, timeout: int = 5) -> Dict[str, Any]:
        """
        Ping a host to check connectivity and measure latency.
        
        Args:
            host: Hostname or IP address
            count: Number of ping requests
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with ping results
        """
        try:
            # Construct ping command based on OS
            if self.system == "Windows":
                cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
            else:
                cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
            
            # Execute ping
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout * count + 5
            )
            
            # Parse output
            output = result.stdout
            
            # Extract statistics
            if self.system == "Windows":
                packet_loss_match = re.search(r'(\d+)% loss', output)
                time_matches = re.findall(r'time[=<](\d+)ms', output)
            else:
                packet_loss_match = re.search(r'(\d+)% packet loss', output)
                time_matches = re.findall(r'time=(\d+\.?\d*) ms', output)
            
            packet_loss = int(packet_loss_match.group(1)) if packet_loss_match else 100
            latencies = [float(t) for t in time_matches] if time_matches else []
            
            success = packet_loss < 100 and len(latencies) > 0
            
            stats = {}
            if latencies:
                stats = {
                    "min_ms": round(min(latencies), 2),
                    "max_ms": round(max(latencies), 2),
                    "avg_ms": round(statistics.mean(latencies), 2),
                    "median_ms": round(statistics.median(latencies), 2),
                    "jitter_ms": round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0
                }
            
            return {
                "success": success,
                "host": host,
                "packets_sent": count,
                "packets_received": len(latencies),
                "packet_loss_percent": packet_loss,
                "latencies": latencies,
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Ping command timed out",
                "host": host
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def check_port(self, host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
        """
        Check if a port is open on a host.
        
        Args:
            host: Hostname or IP address
            port: Port number to check
            timeout: Connection timeout in seconds
            
        Returns:
            Dictionary with port status
        """
        try:
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            
            end_time = time.time()
            connection_time = round((end_time - start_time) * 1000, 2)
            
            sock.close()
            
            is_open = result == 0
            
            return {
                "success": True,
                "host": host,
                "port": port,
                "is_open": is_open,
                "status": "open" if is_open else "closed",
                "connection_time_ms": connection_time if is_open else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except socket.gaierror:
            return {
                "success": False,
                "error": "Hostname could not be resolved",
                "host": host,
                "port": port
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "host": host,
                "port": port
            }
    
    def scan_ports(self, host: str, ports: Optional[List[int]] = None, 
                   common_only: bool = True) -> Dict[str, Any]:
        """
        Scan multiple ports on a host.
        
        Args:
            host: Hostname or IP address
            ports: List of ports to scan (defaults to common ports)
            common_only: If True and ports not specified, scan common ports only
            
        Returns:
            Dictionary with scan results
        """
        try:
            if ports is None:
                if common_only:
                    # Common ports
                    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 5900, 8080]
                else:
                    # Well-known ports (1-1024)
                    ports = list(range(1, 1025))
            
            open_ports = []
            closed_ports = []
            
            start_time = time.time()
            
            for port in ports:
                result = self.check_port(host, port, timeout=2)
                
                if result["success"] and result["is_open"]:
                    open_ports.append({
                        "port": port,
                        "service": self._get_service_name(port),
                        "connection_time_ms": result.get("connection_time_ms")
                    })
                else:
                    closed_ports.append(port)
            
            end_time = time.time()
            scan_duration = round(end_time - start_time, 2)
            
            return {
                "success": True,
                "host": host,
                "ports_scanned": len(ports),
                "open_ports_count": len(open_ports),
                "closed_ports_count": len(closed_ports),
                "open_ports": open_ports,
                "scan_duration_seconds": scan_duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def dns_lookup(self, hostname: str) -> Dict[str, Any]:
        """
        Perform DNS lookup for a hostname.
        
        Args:
            hostname: Hostname to lookup
            
        Returns:
            Dictionary with DNS information
        """
        try:
            # Get IP addresses
            ip_addresses = socket.gethostbyname_ex(hostname)
            
            # Try reverse DNS lookup
            try:
                reverse_dns = socket.gethostbyaddr(ip_addresses[2][0])
                hostname_from_ip = reverse_dns[0]
            except:
                hostname_from_ip = None
            
            return {
                "success": True,
                "hostname": hostname,
                "canonical_name": ip_addresses[0],
                "aliases": ip_addresses[1],
                "ip_addresses": ip_addresses[2],
                "primary_ip": ip_addresses[2][0] if ip_addresses[2] else None,
                "reverse_dns": hostname_from_ip,
                "timestamp": datetime.now().isoformat()
            }
            
        except socket.gaierror:
            return {
                "success": False,
                "error": "Hostname could not be resolved",
                "hostname": hostname
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "hostname": hostname
            }
    
    def test_connection(self, host: str, port: int = 80, protocol: str = "http") -> Dict[str, Any]:
        """
        Test network connection with detailed diagnostics.
        
        Args:
            host: Hostname or IP address
            port: Port to test
            protocol: Protocol to test (http, https, tcp)
            
        Returns:
            Dictionary with connection test results
        """
        try:
            results = {
                "success": True,
                "host": host,
                "port": port,
                "protocol": protocol,
                "tests": {}
            }
            
            # DNS lookup
            dns_result = self.dns_lookup(host)
            results["tests"]["dns"] = {
                "passed": dns_result["success"],
                "ip_address": dns_result.get("primary_ip"),
                "resolve_time_ms": 0  # Would need timing
            }
            
            # Ping test
            ping_result = self.ping_host(host, count=3)
            results["tests"]["ping"] = {
                "passed": ping_result["success"],
                "avg_latency_ms": ping_result.get("statistics", {}).get("avg_ms"),
                "packet_loss_percent": ping_result.get("packet_loss_percent")
            }
            
            # Port connectivity
            port_result = self.check_port(host, port)
            results["tests"]["port"] = {
                "passed": port_result.get("is_open", False),
                "connection_time_ms": port_result.get("connection_time_ms")
            }
            
            # Overall status
            all_passed = all(test["passed"] for test in results["tests"].values())
            results["overall_status"] = "healthy" if all_passed else "issues_detected"
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_service_name(self, port: int) -> str:
        """Get common service name for a port."""
        services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP-Alt"
        }
        return services.get(port, "Unknown")

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "ping_host",
            "description": "Ping a host to check connectivity and measure latency",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "Hostname or IP address"},
                    "count": {"type": "integer", "description": "Number of ping requests", "default": 4},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 5}
                },
                "required": ["host"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_port",
            "description": "Check if a specific port is open on a host",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "Hostname or IP address"},
                    "port": {"type": "integer", "description": "Port number to check"},
                    "timeout": {"type": "integer", "description": "Connection timeout", "default": 5}
                },
                "required": ["host", "port"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scan_ports",
            "description": "Scan multiple ports on a host to find open services",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "Hostname or IP address"},
                    "ports": {"type": "array", "items": {"type": "integer"}, "description": "Specific ports to scan"},
                    "common_only": {"type": "boolean", "description": "Scan common ports only", "default": True}
                },
                "required": ["host"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dns_lookup",
            "description": "Perform DNS lookup for a hostname",
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string", "description": "Hostname to lookup"}
                },
                "required": ["hostname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "test_connection",
            "description": "Test network connection with comprehensive diagnostics",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "Hostname or IP address"},
                    "port": {"type": "integer", "description": "Port to test", "default": 80},
                    "protocol": {"type": "string", "description": "Protocol to test", "default": "http"}
                },
                "required": ["host"]
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "network_monitor",
    "description": "OpenAI-compatible network monitoring and diagnostics tool",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "ping_host",
        "check_port",
        "scan_ports",
        "dns_lookup",
        "test_connection"
    ],
    "requirements": ["socket", "subprocess", "platform", "statistics"],
    "safety_features": [
        "Timeout protection",
        "Error handling",
        "Limited port scanning",
        "Non-invasive testing"
    ]
}
