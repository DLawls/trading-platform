#!/usr/bin/env python3
"""
System Health Check Utilities
Monitor overall health and status of all financial data collectors.
"""

import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import subprocess
import psutil
import logging

def check_collector_status(collector_name: str, base_path: Path) -> Dict[str, Any]:
    """
    Check the health status of a specific collector
    
    Args:
        collector_name: Name of the collector (e.g., 'yahoo_finance')
        base_path: Base path to financial_data_collector
    
    Returns:
        Status dictionary
    """
    collector_path = base_path / f"{collector_name}_collector"
    
    if not collector_path.exists():
        return {
            'status': 'not_found',
            'collector': collector_name,
            'message': f"Collector directory not found: {collector_path}"
        }
    
    # Check configuration files
    config_path = collector_path / 'config'
    has_config = config_path.exists() and len(list(config_path.glob('*.yaml'))) > 0
    
    # Check ingest modules
    ingest_path = collector_path / 'ingest'
    has_ingest = ingest_path.exists() and len(list(ingest_path.glob('*.py'))) > 0
    
    # Check recent activity (log files or data files)
    has_recent_activity = False
    log_dirs = [collector_path / 'logs', base_path / 'logs' / collector_name]
    for log_dir in log_dirs:
        if log_dir.exists():
            recent_logs = [
                f for f in log_dir.glob('*.log') 
                if datetime.fromtimestamp(f.stat().st_mtime) > datetime.now() - timedelta(days=1)
            ]
            if recent_logs:
                has_recent_activity = True
                break
    
    # Determine overall status
    if has_config and has_ingest:
        if has_recent_activity:
            status = 'active'
        else:
            status = 'configured'
    else:
        status = 'incomplete'
    
    return {
        'status': status,
        'collector': collector_name,
        'has_config': has_config,
        'has_ingest': has_ingest,
        'has_recent_activity': has_recent_activity,
        'path': str(collector_path)
    }

def check_data_health(data_path: Path) -> Dict[str, Any]:
    """
    Check the health of data storage
    
    Args:
        data_path: Path to financial_data directory
    
    Returns:
        Data health status
    """
    if not data_path.exists():
        return {
            'status': 'error',
            'message': 'Data directory does not exist',
            'total_files': 0,
            'total_size_mb': 0
        }
    
    # Count files and calculate total size
    total_files = 0
    total_size_bytes = 0
    data_types = {}
    
    for data_type_dir in data_path.iterdir():
        if data_type_dir.is_dir():
            files = list(data_type_dir.glob('*.parquet'))
            file_count = len(files)
            type_size = sum(f.stat().st_size for f in files)
            
            data_types[data_type_dir.name] = {
                'file_count': file_count,
                'size_mb': type_size / (1024 * 1024)
            }
            
            total_files += file_count
            total_size_bytes += type_size
    
    return {
        'status': 'healthy' if total_files > 0 else 'empty',
        'total_files': total_files,
        'total_size_mb': total_size_bytes / (1024 * 1024),
        'data_types': data_types,
        'last_updated': datetime.fromtimestamp(data_path.stat().st_mtime)
    }

def check_system_resources() -> Dict[str, Any]:
    """
    Check system resource usage
    
    Returns:
        System resource status
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # Disk usage for the current directory
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free_gb = disk.free / (1024**3)
        
        # Determine status based on usage
        status = 'healthy'
        issues = []
        
        if cpu_percent > 80:
            status = 'warning'
            issues.append(f"High CPU usage: {cpu_percent}%")
        
        if memory_percent > 85:
            status = 'warning'
            issues.append(f"High memory usage: {memory_percent}%")
        
        if disk_percent > 90:
            status = 'critical'
            issues.append(f"Low disk space: {disk_percent}% used")
        
        return {
            'status': status,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_available_gb': round(memory_available_gb, 2),
            'disk_percent': disk_percent,
            'disk_free_gb': round(disk_free_gb, 2),
            'issues': issues
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to check system resources: {e}"
        }

def check_api_connectivity() -> Dict[str, Any]:
    """
    Check connectivity to external APIs
    
    Returns:
        API connectivity status
    """
    apis = {
        'yahoo_finance': 'https://finance.yahoo.com',
        'fred': 'https://fred.stlouisfed.org',
        'abs': 'https://api.data.abs.gov.au'
    }
    
    results = {}
    overall_status = 'healthy'
    
    for api_name, url in apis.items():
        try:
            # Simple connectivity check using curl
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            http_code = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            
            if 200 <= http_code < 400:
                api_status = 'reachable'
            else:
                api_status = 'unreachable'
                overall_status = 'degraded'
            
            results[api_name] = {
                'status': api_status,
                'http_code': http_code,
                'url': url
            }
            
        except Exception as e:
            results[api_name] = {
                'status': 'error',
                'error': str(e),
                'url': url
            }
            overall_status = 'degraded'
    
    return {
        'status': overall_status,
        'apis': results
    }

def generate_health_report(base_path: Path) -> Dict[str, Any]:
    """
    Generate comprehensive health report for all systems
    
    Args:
        base_path: Base path to financial_data_collector
    
    Returns:
        Complete health report
    """
    report = {
        'timestamp': datetime.now(),
        'overall_status': 'healthy'
    }
    
    # Check collectors
    collectors = ['yahoo_finance', 'fred_data', 'abs_data', 'alpaca_data']
    collector_statuses = {}
    
    for collector in collectors:
        status = check_collector_status(collector, base_path)
        collector_statuses[collector] = status
        
        if status['status'] in ['not_found', 'incomplete']:
            report['overall_status'] = 'degraded'
    
    report['collectors'] = collector_statuses
    
    # Check data health
    data_path = base_path / 'financial_data'
    data_health = check_data_health(data_path)
    report['data'] = data_health
    
    if data_health['status'] == 'error':
        report['overall_status'] = 'critical'
    elif data_health['status'] == 'empty':
        report['overall_status'] = 'degraded'
    
    # Check system resources
    system_health = check_system_resources()
    report['system'] = system_health
    
    if system_health['status'] == 'critical':
        report['overall_status'] = 'critical'
    elif system_health['status'] == 'warning' and report['overall_status'] == 'healthy':
        report['overall_status'] = 'degraded'
    
    # Check API connectivity
    api_health = check_api_connectivity()
    report['apis'] = api_health
    
    if api_health['status'] == 'degraded' and report['overall_status'] == 'healthy':
        report['overall_status'] = 'degraded'
    
    return report

def format_health_report(health_report: Dict[str, Any]) -> str:
    """
    Format health report as readable text
    
    Args:
        health_report: Health report dictionary
    
    Returns:
        Formatted report string
    """
    lines = [
        "🏥 System Health Report",
        "=" * 50,
        f"Timestamp: {health_report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
        f"Overall Status: {health_report['overall_status'].upper()}",
        ""
    ]
    
    # Collectors section
    lines.append("📊 Collectors:")
    for collector, status in health_report['collectors'].items():
        status_icon = {
            'active': '🟢',
            'configured': '🟡', 
            'incomplete': '🟠',
            'not_found': '🔴'
        }.get(status['status'], '❓')
        
        lines.append(f"  {status_icon} {collector}: {status['status']}")
    
    lines.append("")
    
    # Data section
    data = health_report['data']
    data_icon = {'healthy': '🟢', 'empty': '🟡', 'error': '🔴'}.get(data['status'], '❓')
    lines.append(f"💾 Data: {data_icon} {data['status']}")
    lines.append(f"  Files: {data['total_files']}, Size: {data['total_size_mb']:.1f} MB")
    
    lines.append("")
    
    # System section
    system = health_report['system']
    system_icon = {'healthy': '🟢', 'warning': '🟡', 'critical': '🔴'}.get(system['status'], '❓')
    lines.append(f"💻 System: {system_icon} {system['status']}")
    lines.append(f"  CPU: {system['cpu_percent']}%, Memory: {system['memory_percent']}%, Disk: {system['disk_percent']}%")
    
    return "\n".join(lines) 