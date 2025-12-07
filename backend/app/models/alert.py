"""
Alert Data Models
Pydantic models for security alerts
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class Alert(BaseModel):
    """Security alert model"""
    timestamp: datetime = Field(default_factory=datetime.utcnow, alias="@timestamp")
    alert_id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    description: str
    
    # Matched events and context
    matched_events: List[Dict[str, Any]] = []
    event_count: int = 1
    
    # Alert metadata
    status: AlertStatus = AlertStatus.OPEN
    assigned_to: Optional[str] = None
    tags: List[str] = []
    
    # Additional context
    source_ips: List[str] = []
    destination_ips: List[str] = []
    usernames: List[str] = []
    hostnames: List[str] = []
    
    # Remediation
    remediation_steps: Optional[List[str]] = None
    mitre_tactics: Optional[List[str]] = None
    mitre_techniques: Optional[List[str]] = None
    
    class Config:
        populate_by_name = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "@timestamp": "2024-11-22T01:00:00Z",
                "alert_id": "R001_1732233600.123",
                "rule_id": "R001",
                "rule_name": "Multiple Failed SSH Logins",
                "severity": "high",
                "description": "Detected 10 failed SSH login attempts from 192.168.1.100",
                "event_count": 10,
                "status": "open",
                "source_ips": ["192.168.1.100"],
                "usernames": ["admin", "root"],
                "mitre_tactics": ["Credential Access"],
                "mitre_techniques": ["T1110 - Brute Force"]
            }
        }

class AlertSearchRequest(BaseModel):
    """Request model for alert search"""
    severity: Optional[List[AlertSeverity]] = None
    status: Optional[List[AlertStatus]] = None
    rule_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100
    offset: int = 0

class AlertUpdateRequest(BaseModel):
    """Request model for updating alert status"""
    alert_id: str
    status: AlertStatus
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
