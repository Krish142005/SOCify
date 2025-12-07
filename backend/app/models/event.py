"""
Event Data Models
Pydantic models for log events following ECS schema
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class HostInfo(BaseModel):
    """Host information"""
    name: Optional[str] = None
    hostname: Optional[str] = None
    os_family: Optional[str] = Field(None, alias="family")
    os_version: Optional[str] = Field(None, alias="version")

class SourceInfo(BaseModel):
    """Source information"""
    ip: Optional[str] = None
    port: Optional[int] = None
    domain: Optional[str] = None

class DestinationInfo(BaseModel):
    """Destination information"""
    ip: Optional[str] = None
    port: Optional[int] = None
    domain: Optional[str] = None

class UserInfo(BaseModel):
    """User information"""
    name: Optional[str] = None
    id: Optional[str] = None
    email: Optional[str] = None

class ProcessInfo(BaseModel):
    """Process information"""
    name: Optional[str] = None
    pid: Optional[int] = None
    command_line: Optional[str] = None
    executable: Optional[str] = None

class FileInfo(BaseModel):
    """File information"""
    path: Optional[str] = None
    name: Optional[str] = None
    extension: Optional[str] = None
    size: Optional[int] = None

class EventInfo(BaseModel):
    """Event classification"""
    action: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    outcome: Optional[str] = None
    severity: Optional[int] = None

class GeoInfo(BaseModel):
    """Geographic information"""
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    location: Optional[Dict[str, float]] = None

class LogEvent(BaseModel):
    """
    Main log event model following ECS schema
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow, alias="@timestamp")
    message: Optional[str] = None
    raw_log: Optional[str] = None
    
    # ECS fields
    event: Optional[EventInfo] = None
    host: Optional[HostInfo] = None
    source: Optional[SourceInfo] = None
    destination: Optional[DestinationInfo] = None
    user: Optional[UserInfo] = None
    process: Optional[ProcessInfo] = None
    file: Optional[FileInfo] = None
    geo: Optional[GeoInfo] = None
    
    # Additional metadata
    tags: Optional[list[str]] = []
    labels: Optional[Dict[str, str]] = {}
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "@timestamp": "2024-11-22T01:00:00Z",
                "message": "Failed password for admin from 192.168.1.100",
                "event": {
                    "action": "ssh_login_failed",
                    "category": "authentication",
                    "outcome": "failure"
                },
                "source": {
                    "ip": "192.168.1.100"
                },
                "user": {
                    "name": "admin"
                },
                "host": {
                    "name": "web-server-01"
                }
            }
        }

class IngestRequest(BaseModel):
    """Request model for log ingestion"""
    raw_log: str
    source_type: str = "generic"
    metadata: Dict[str, Any] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_log": "Dec 10 06:55:46 server sshd[1234]: Failed password for admin from 192.168.1.100",
                "source_type": "syslog",
                "metadata": {
                    "hostname": "web-server-01",
                    "os_family": "linux"
                }
            }
        }
