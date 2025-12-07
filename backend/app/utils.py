"""
Utility Functions
Helper functions for the backend application
"""

import hashlib
import json
from typing import Any, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_hash(data: str) -> str:
    """
    Generates SHA256 hash of input data
    
    Args:
        data: Input string
        
    Returns:
        str: Hex digest of hash
    """
    return hashlib.sha256(data.encode()).hexdigest()

def sanitize_dict(data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
    """
    Sanitizes dictionary by removing None values and limiting depth
    
    Args:
        data: Input dictionary
        max_depth: Maximum nesting depth
        
    Returns:
        dict: Sanitized dictionary
    """
    if max_depth <= 0:
        return {}
    
    result = {}
    for key, value in data.items():
        if value is None:
            continue
        
        if isinstance(value, dict):
            sanitized = sanitize_dict(value, max_depth - 1)
            if sanitized:
                result[key] = sanitized
        elif isinstance(value, list):
            result[key] = [
                sanitize_dict(item, max_depth - 1) if isinstance(item, dict) else item
                for item in value if item is not None
            ]
        else:
            result[key] = value
    
    return result

def format_timestamp(timestamp: Any) -> str:
    """
    Formats timestamp to ISO format
    
    Args:
        timestamp: Timestamp (datetime, string, or int)
        
    Returns:
        str: ISO formatted timestamp
    """
    if isinstance(timestamp, datetime):
        return timestamp.isoformat()
    elif isinstance(timestamp, str):
        return timestamp
    elif isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).isoformat()
    else:
        return datetime.utcnow().isoformat()

def validate_ip(ip: str) -> bool:
    """
    Validates IPv4 address
    
    Args:
        ip: IP address string
        
    Returns:
        bool: True if valid IPv4
    """
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)

def truncate_string(text: str, max_length: int = 1000) -> str:
    """
    Truncates string to maximum length
    
    Args:
        text: Input string
        max_length: Maximum length
        
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely loads JSON with fallback
    
    Args:
        data: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {data[:100]}")
        return default

def get_severity_score(severity: str) -> int:
    """
    Converts severity string to numeric score
    
    Args:
        severity: Severity level (low, medium, high, critical)
        
    Returns:
        int: Numeric score (1-4)
    """
    severity_map = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    return severity_map.get(severity.lower(), 0)
