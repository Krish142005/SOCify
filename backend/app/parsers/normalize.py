"""
Log Normalization to ECS Format
Converts raw logs to Elastic Common Schema
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional
from app.parsers.grok_patterns import PATTERNS
import logging

logger = logging.getLogger(__name__)

def normalize_log(raw_log: str, source_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts raw log to ECS-compliant format
    
    Args:
        raw_log: Raw log string
        source_type: Type of log source (syslog, apache, windows_event, etc.)
        metadata: Additional metadata from agent
        
    Returns:
        dict: Normalized event in ECS format
    """
    # Base event structure
    event = {
        "raw_log": raw_log,
        "@timestamp": datetime.utcnow().isoformat(),
        "host": {
            "name": metadata.get("hostname", "unknown"),
            "os": {
                "family": metadata.get("os_family", "unknown"),
                "version": metadata.get("os_version", "")
            }
        },
        "agent": {
            "type": "socify-agent",
            "version": metadata.get("agent_version", "1.0.0")
        },
        "tags": metadata.get("tags", [])
    }
    
    # Apply source-specific parsing
    try:
        if source_type == "syslog":
            parsed = parse_syslog(raw_log)
        elif source_type == "apache":
            parsed = parse_apache(raw_log)
        elif source_type == "windows_event":
            parsed = parse_windows_event(raw_log)
        elif source_type == "firewall":
            parsed = parse_firewall(raw_log)
        elif source_type == "process":
            parsed = parse_process(raw_log)
        elif source_type == "file":
            parsed = parse_file_operation(raw_log)
        else:
            # Generic parsing - just store the message
            parsed = {"message": raw_log}
        
        # Merge parsed data with base event
        event = deep_merge(event, parsed)
        
    except Exception as e:
        logger.error(f"Error parsing log: {str(e)}")
        event["message"] = raw_log
        event["tags"].append("parse_error")
    
    return event

def parse_syslog(log: str) -> Dict[str, Any]:
    """
    Parses syslog format logs
    Example: Dec 10 06:55:46 server sshd[1234]: Failed password for admin from 192.168.1.100
    """
    pattern = PATTERNS.get("SYSLOG")
    match = re.match(pattern, log)
    
    if not match:
        return {"message": log}
    
    groups = match.groupdict()
    
    # Check for SSH-specific patterns
    message = groups.get("message", "")
    ssh_failed = re.match(PATTERNS["SSH_FAILED_LOGIN"], message)
    ssh_success = re.match(PATTERNS["SSH_SUCCESSFUL_LOGIN"], message)
    
    result = {
        "@timestamp": parse_syslog_timestamp(groups.get("timestamp")),
        "host": {"name": groups.get("host")},
        "process": {
            "name": groups.get("process"),
            "pid": int(groups.get("pid")) if groups.get("pid") else None
        },
        "message": message
    }
    
    if ssh_failed:
        ssh_data = ssh_failed.groupdict()
        result.update({
            "event": {
                "action": "ssh_login_failed",
                "category": "authentication",
                "type": "start",
                "outcome": "failure"
            },
            "user": {"name": ssh_data.get("user")},
            "source": {
                "ip": ssh_data.get("source_ip"),
                "port": int(ssh_data.get("port")) if ssh_data.get("port") else None
            }
        })
    elif ssh_success:
        ssh_data = ssh_success.groupdict()
        result.update({
            "event": {
                "action": "ssh_login_success",
                "category": "authentication",
                "type": "start",
                "outcome": "success"
            },
            "user": {"name": ssh_data.get("user")},
            "source": {
                "ip": ssh_data.get("source_ip"),
                "port": int(ssh_data.get("port")) if ssh_data.get("port") else None
            }
        })
    else:
        result["event"] = {
            "category": "system",
            "type": "info"
        }
    
    return result

def parse_apache(log: str) -> Dict[str, Any]:
    """
    Parses Apache/Nginx access logs
    Example: 192.168.1.1 - - [10/Dec/2024:06:55:46 +0000] "GET /index.html HTTP/1.1" 200 1234
    """
    pattern = PATTERNS.get("APACHE_ACCESS")
    match = re.match(pattern, log)
    
    if not match:
        return {"message": log}
    
    groups = match.groupdict()
    status_code = int(groups.get("status", 0))
    
    return {
        "@timestamp": parse_apache_timestamp(groups.get("timestamp")),
        "source": {"ip": groups.get("client_ip")},
        "http": {
            "request": {
                "method": groups.get("method"),
                "path": groups.get("path")
            },
            "response": {
                "status_code": status_code,
                "bytes": int(groups.get("bytes", 0))
            },
            "version": groups.get("http_version")
        },
        "event": {
            "category": "web",
            "type": "access",
            "outcome": "success" if 200 <= status_code < 400 else "failure"
        },
        "url": {
            "path": groups.get("path")
        },
        "message": log
    }

def parse_windows_event(log: str) -> Dict[str, Any]:
    """
    Parses Windows Event logs (simplified)
    Example: EventID=4625 User=admin Source=192.168.1.100
    """
    pattern = PATTERNS.get("WINDOWS_EVENT")
    match = re.match(pattern, log)
    
    if not match:
        return {"message": log}
    
    groups = match.groupdict()
    event_id = groups.get("event_id")
    
    # Map common Windows Event IDs
    event_mapping = {
        "4624": {"action": "windows_login_success", "outcome": "success"},
        "4625": {"action": "windows_login_failed", "outcome": "failure"},
        "4672": {"action": "privilege_escalation", "outcome": "success"},
        "4688": {"action": "process_creation", "outcome": "success"},
        "4698": {"action": "scheduled_task_created", "outcome": "success"},
    }
    
    event_info = event_mapping.get(event_id, {"action": "windows_event", "outcome": "unknown"})
    
    return {
        "event": {
            "action": event_info["action"],
            "category": "authentication" if event_id in ["4624", "4625"] else "process",
            "outcome": event_info["outcome"],
            "code": event_id
        },
        "user": {"name": groups.get("user")},
        "source": {"ip": groups.get("source_ip")},
        "message": log
    }

def parse_firewall(log: str) -> Dict[str, Any]:
    """
    Parses firewall logs
    Example: DENY TCP 192.168.1.100:12345 -> 10.0.0.1:80
    """
    pattern = PATTERNS.get("FIREWALL")
    match = re.match(pattern, log)
    
    if not match:
        return {"message": log}
    
    groups = match.groupdict()
    
    return {
        "event": {
            "action": f"firewall_{groups.get('action', '').lower()}",
            "category": "network",
            "type": "connection",
            "outcome": "success" if groups.get("action") == "ALLOW" else "denied"
        },
        "network": {
            "protocol": groups.get("protocol", "").lower()
        },
        "source": {
            "ip": groups.get("source_ip"),
            "port": int(groups.get("source_port", 0))
        },
        "destination": {
            "ip": groups.get("dest_ip"),
            "port": int(groups.get("dest_port", 0))
        },
        "message": log
    }

def parse_process(log: str) -> Dict[str, Any]:
    """
    Parses process execution logs
    Example: Process started: cmd.exe PID=1234 User=admin
    """
    pattern = PATTERNS.get("PROCESS_START")
    match = re.match(pattern, log)
    
    if not match:
        return {"message": log}
    
    groups = match.groupdict()
    
    return {
        "event": {
            "action": "process_started",
            "category": "process",
            "type": "start",
            "outcome": "success"
        },
        "process": {
            "name": groups.get("process_name"),
            "pid": int(groups.get("pid", 0))
        },
        "user": {"name": groups.get("user")},
        "message": log
    }

def parse_file_operation(log: str) -> Dict[str, Any]:
    """
    Parses file operation logs
    Example: File created: C:\\Users\\admin\\document.txt
    """
    pattern = PATTERNS.get("FILE_OPERATION")
    match = re.match(pattern, log)
    
    if not match:
        return {"message": log}
    
    groups = match.groupdict()
    file_path = groups.get("file_path", "")
    
    # Extract file name and extension
    import os
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lstrip('.')
    
    return {
        "event": {
            "action": f"file_{groups.get('operation')}",
            "category": "file",
            "type": "change",
            "outcome": "success"
        },
        "file": {
            "path": file_path,
            "name": file_name,
            "extension": file_ext
        },
        "message": log
    }

def parse_syslog_timestamp(timestamp_str: str) -> str:
    """
    Converts syslog timestamp to ISO format
    Example: Dec 10 06:55:46 -> 2024-12-10T06:55:46Z
    """
    try:
        # Add current year since syslog doesn't include it
        current_year = datetime.utcnow().year
        dt = datetime.strptime(f"{timestamp_str} {current_year}", "%b %d %H:%M:%S %Y")
        return dt.isoformat() + "Z"
    except:
        return datetime.utcnow().isoformat() + "Z"

def parse_apache_timestamp(timestamp_str: str) -> str:
    """
    Converts Apache timestamp to ISO format
    Example: 10/Dec/2024:06:55:46 +0000 -> 2024-12-10T06:55:46Z
    """
    try:
        dt = datetime.strptime(timestamp_str.split()[0], "%d/%b/%Y:%H:%M:%S")
        return dt.isoformat() + "Z"
    except:
        return datetime.utcnow().isoformat() + "Z"

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merges two dictionaries
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result
