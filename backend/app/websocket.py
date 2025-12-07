"""
WebSocket Support for Real-Time Log and Alert Streaming
Provides WebSocket endpoints for frontend to receive real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import logging
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Connection managers for different streams
class ConnectionManager:
    """Manages WebSocket connections for broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        # Convert to JSON
        json_message = json.dumps(message)
        
        # Send to all connections
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json_message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                dead_connections.append(connection)
        
        # Remove dead connections
        for conn in dead_connections:
            self.disconnect(conn)


# Create connection managers
log_manager = ConnectionManager()
alert_manager = ConnectionManager()


@router.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming"""
    await log_manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Connected to log stream",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and listen for messages
        while True:
            # Wait for messages (ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back pings
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({
                    "type": "keepalive",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)
        logger.info("Log stream WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"Error in log stream WebSocket: {e}", exc_info=True)
        log_manager.disconnect(websocket)


@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alert streaming"""
    await alert_manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Connected to alert stream",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and listen for messages
        while True:
            # Wait for messages (ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back pings
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({
                    "type": "keepalive",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
    except WebSocketDisconnect:
        alert_manager.disconnect(websocket)
        logger.info("Alert stream WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"Error in alert stream WebSocket: {e}", exc_info=True)
        alert_manager.disconnect(websocket)


async def broadcast_log(log_event: Dict[str, Any]):
    """Broadcast new log to all connected clients"""
    await log_manager.broadcast({
        "type": "log",
        "data": log_event,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_alert(alert: Dict[str, Any]):
    """Broadcast new alert to all connected clients"""
    await alert_manager.broadcast({
        "type": "alert",
        "data": alert,
        "timestamp": datetime.utcnow().isoformat()
    })


def get_log_manager():
    """Get log connection manager"""
    return log_manager


def get_alert_manager():
    """Get alert connection manager"""
    return alert_manager
