"""
System Diagnostics Tool (OpenAI-Compatible)
Performs system health checks, resource monitoring, and diagnostics.
"""

import psutil
import platform
import os
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class SystemDiagnosticsTool:
    """
    OpenAI-compatible system diagnostics tool for health monitoring and analysis.
    Supports CPU, memory, disk, and process monitoring.
    """
    
    def __init__(self):
        """Initialize system diagnostics tool."""
        self.system_info = self._get_system_info()
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information.
        
        Returns:
            Dictionary with system information
        """
        try:
            return {
                "success": True,
                "system": self.system_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_cpu(self) -> Dict[str, Any]:
        """
        Check CPU usage and information.
        
        Returns:
            Dictionary with CPU metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            cpu_stats = psutil.cpu_stats()
            
            return {
                "success": True,
                "cpu_count": psutil.cpu_count(logical=True),
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "cpu_percent_total": round(sum(cpu_percent) / len(cpu_percent), 2),
                "cpu_percent_per_core": [round(p, 2) for p in cpu_percent],
                "cpu_frequency_mhz": {
                    "current": round(cpu_freq.current, 2) if cpu_freq else None,
                    "min": round(cpu_freq.min, 2) if cpu_freq else None,
                    "max": round(cpu_freq.max, 2) if cpu_freq else None
                },
                "cpu_stats": {
                    "context_switches": cpu_stats.ctx_switches,
                    "interrupts": cpu_stats.interrupts,
                    "soft_interrupts": cpu_stats.soft_interrupts if hasattr(cpu_stats, 'soft_interrupts') else None
                },
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_memory(self) -> Dict[str, Any]:
        """
        Check memory usage and information.
        
        Returns:
            Dictionary with memory metrics
        """
        try:
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            
            return {
                "success": True,
                "virtual_memory": {
                    "total_gb": round(virtual_memory.total / (1024**3), 2),
                    "available_gb": round(virtual_memory.available / (1024**3), 2),
                    "used_gb": round(virtual_memory.used / (1024**3), 2),
                    "free_gb": round(virtual_memory.free / (1024**3), 2),
                    "percent_used": round(virtual_memory.percent, 2),
                    "percent_available": round(100 - virtual_memory.percent, 2)
                },
                "swap_memory": {
                    "total_gb": round(swap_memory.total / (1024**3), 2),
                    "used_gb": round(swap_memory.used / (1024**3), 2),
                    "free_gb": round(swap_memory.free / (1024**3), 2),
                    "percent_used": round(swap_memory.percent, 2)
                },
                "status": self._get_memory_status(virtual_memory.percent),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_disk(self, path: str = "/") -> Dict[str, Any]:
        """
        Check disk usage and information.
        
        Args:
            path: Path to check disk usage (default: root)
            
        Returns:
            Dictionary with disk metrics
        """
        try:
            disk_usage = psutil.disk_usage(path)
            disk_io = psutil.disk_io_counters()
            
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent_used": round(usage.percent, 2)
                    })
                except:
                    continue
            
            return {
                "success": True,
                "path": path,
                "usage": {
                    "total_gb": round(disk_usage.total / (1024**3), 2),
                    "used_gb": round(disk_usage.used / (1024**3), 2),
                    "free_gb": round(disk_usage.free / (1024**3), 2),
                    "percent_used": round(disk_usage.percent, 2)
                },
                "io_counters": {
                    "read_count": disk_io.read_count if disk_io else None,
                    "write_count": disk_io.write_count if disk_io else None,
                    "read_mb": round(disk_io.read_bytes / (1024**2), 2) if disk_io else None,
                    "write_mb": round(disk_io.write_bytes / (1024**2), 2) if disk_io else None
                },
                "partitions": partitions,
                "status": self._get_disk_status(disk_usage.percent),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_network(self) -> Dict[str, Any]:
        """
        Check network interfaces and statistics.
        
        Returns:
            Dictionary with network metrics
        """
        try:
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interfaces[interface] = []
                for addr in addrs:
                    interfaces[interface].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
            
            return {
                "success": True,
                "io_counters": {
                    "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                    "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errors_in": net_io.errin,
                    "errors_out": net_io.errout,
                    "drops_in": net_io.dropin,
                    "drops_out": net_io.dropout
                },
                "active_connections": net_connections,
                "interfaces": interfaces,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_processes(self, sort_by: str = "cpu", limit: int = 10) -> Dict[str, Any]:
        """
        Check running processes and resource usage.
        
        Args:
            sort_by: Sort by 'cpu', 'memory', or 'name'
            limit: Number of processes to return
            
        Returns:
            Dictionary with process information
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "cpu_percent": round(pinfo['cpu_percent'], 2) if pinfo['cpu_percent'] else 0,
                        "memory_percent": round(pinfo['memory_percent'], 2) if pinfo['memory_percent'] else 0,
                        "status": pinfo['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            if sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            else:
                processes.sort(key=lambda x: x['name'])
            
            return {
                "success": True,
                "total_processes": len(processes),
                "top_processes": processes[:limit],
                "sort_by": sort_by,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.
        
        Returns:
            Dictionary with health check results
        """
        try:
            cpu_check = self.check_cpu()
            memory_check = self.check_memory()
            disk_check = self.check_disk()
            
            issues = []
            warnings = []
            
            # Check CPU
            if cpu_check["success"]:
                cpu_usage = cpu_check["cpu_percent_total"]
                if cpu_usage > 90:
                    issues.append(f"High CPU usage: {cpu_usage}%")
                elif cpu_usage > 75:
                    warnings.append(f"Elevated CPU usage: {cpu_usage}%")
            
            # Check memory
            if memory_check["success"]:
                mem_usage = memory_check["virtual_memory"]["percent_used"]
                if mem_usage > 90:
                    issues.append(f"High memory usage: {mem_usage}%")
                elif mem_usage > 75:
                    warnings.append(f"Elevated memory usage: {mem_usage}%")
            
            # Check disk
            if disk_check["success"]:
                disk_usage = disk_check["usage"]["percent_used"]
                if disk_usage > 90:
                    issues.append(f"Low disk space: {disk_usage}% used")
                elif disk_usage > 75:
                    warnings.append(f"Disk space getting low: {disk_usage}% used")
            
            # Determine overall health
            if issues:
                health_status = "critical"
            elif warnings:
                health_status = "warning"
            else:
                health_status = "healthy"
            
            return {
                "success": True,
                "health_status": health_status,
                "issues": issues,
                "warnings": warnings,
                "checks": {
                    "cpu": cpu_check,
                    "memory": memory_check,
                    "disk": disk_check
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version()
        }
    
    def _get_memory_status(self, percent: float) -> str:
        """Get memory status based on usage percentage."""
        if percent > 90:
            return "critical"
        elif percent > 75:
            return "warning"
        else:
            return "healthy"
    
    def _get_disk_status(self, percent: float) -> str:
        """Get disk status based on usage percentage."""
        if percent > 90:
            return "critical"
        elif percent > 75:
            return "warning"
        else:
            return "healthy"

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get comprehensive system information",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_cpu",
            "description": "Check CPU usage and performance metrics",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_memory",
            "description": "Check memory usage and availability",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_disk",
            "description": "Check disk usage and partition information",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to check", "default": "/"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "health_check",
            "description": "Perform comprehensive system health check",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "system_diagnostics",
    "description": "OpenAI-compatible system diagnostics and health monitoring tool",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "get_system_info",
        "check_cpu",
        "check_memory",
        "check_disk",
        "check_network",
        "check_processes",
        "health_check"
    ],
    "requirements": ["psutil", "platform"],
    "safety_features": [
        "Read-only operations",
        "Error handling",
        "Resource monitoring",
        "Health status indicators"
    ]
}
