"""
Log Ingestion Endpoint
Receives logs from agents, normalizes, stores in OpenSearch, and evaluates rules
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.event import IngestRequest
from app.opensearch_client import get_opensearch_client
from app.parsers.normalize import normalize_log
from app.rule_engine import evaluate_rules
import logging
from datetime import datetime
import os
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ingest")
async def ingest_log(log_entry: IngestRequest, background_tasks: BackgroundTasks):
    """
    Receives raw logs from agents, normalizes, stores in OpenSearch,
    and evaluates against detection rules
    
    Args:
        log_entry: Raw log with metadata
        background_tasks: FastAPI background tasks for async processing
        
    Returns:
        dict: Ingestion status and event ID
    """
    try:
        # Step 1: Normalize log to ECS format
        normalized_event = normalize_log(
            log_entry.raw_log,
            log_entry.source_type,
            log_entry.metadata
        )
        
        # Step 2: Ensure timestamp is present
        if '@timestamp' not in normalized_event:
            normalized_event['@timestamp'] = datetime.utcnow().isoformat()
        
        # Step 3: Index to OpenSearch
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        index_name = f"{index_prefix}-{datetime.utcnow().strftime('%Y.%m')}"
        
        response = client.index(
            index=index_name,
            body=normalized_event,
            refresh=True  # Make immediately searchable (disable in production for performance)
        )
        
        event_id = response['_id']
        logger.info(f"Indexed event: {event_id} to {index_name}")
        
        # Step 4: Evaluate detection rules and get triggered alerts
        alerts = evaluate_rules(normalized_event)
        
        # Step 5: Broadcast log and alerts via WebSocket
        try:
            from app.websocket import broadcast_log, broadcast_alert
            # Broadcast log
            asyncio.create_task(broadcast_log(normalized_event))
            
            # Broadcast any triggered alerts
            for alert in alerts:
                asyncio.create_task(broadcast_alert(alert))
        except Exception as ws_error:
            logger.warning(f"WebSocket broadcast failed: {ws_error}")
        
        return {
            "status": "success",
            "event_id": event_id,
            "index": index_name,
            "timestamp": normalized_event['@timestamp'],
            "alerts_triggered": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/ingest/batch")
async def ingest_batch(log_entries: list[IngestRequest], background_tasks: BackgroundTasks):
    """
    Batch ingestion endpoint for multiple logs
    
    Args:
        log_entries: List of raw logs
        background_tasks: FastAPI background tasks
        
    Returns:
        dict: Batch ingestion status
    """
    try:
        # Normalize all logs
        normalized_events = []
        for log_entry in log_entries:
            normalized_event = normalize_log(
                log_entry.raw_log,
                log_entry.source_type,
                log_entry.metadata
            )
            if '@timestamp' not in normalized_event:
                normalized_event['@timestamp'] = datetime.utcnow().isoformat()
            normalized_events.append(normalized_event)
        
        # Bulk index to OpenSearch
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        index_name = f"{index_prefix}-{datetime.utcnow().strftime('%Y.%m')}"
        
        # Prepare bulk request
        bulk_body = []
        for event in normalized_events:
            bulk_body.append({"index": {"_index": index_name}})
            bulk_body.append(event)
        
        response = client.bulk(body=bulk_body, refresh=True)
        
        # Count successful and failed
        items = response.get('items', [])
        successful = sum(1 for item in items if item['index']['status'] in [200, 201])
        failed = len(items) - successful
        
        logger.info(f"Batch indexed {successful} events to {index_name}, {failed} failed")
        
        # Evaluate rules for each event and collect alerts
        all_alerts = []
        for event in normalized_events:
            alerts = evaluate_rules(event)
            all_alerts.extend(alerts)
        
        # Broadcast logs and alerts via WebSocket
        try:
            from app.websocket import broadcast_log, broadcast_alert
            for event in normalized_events:
                asyncio.create_task(broadcast_log(event))
            for alert in all_alerts:
                asyncio.create_task(broadcast_alert(alert))
        except Exception as ws_error:
            logger.warning(f"WebSocket broadcast failed: {ws_error}")
        
        return {
            "status": "success",
            "total": len(log_entries),
            "successful": successful,
            "failed": failed,
            "index": index_name,
            "alerts_triggered": len(all_alerts)
        }
        
    except Exception as e:
        logger.error(f"Batch ingestion error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch ingestion failed: {str(e)}")

@router.post("/ingest/windows-events")
async def ingest_windows_events(request: dict):
    """
    Receives already-normalized Windows Event Logs from the collector
    
    Args:
        request: Dict with 'logs' array of normalized events
        
    Returns:
        dict: Ingestion status
    """
    try:
        normalized_events = request.get('logs', [])
        
        if not normalized_events:
            return {"status": "success", "message": "No events to process"}
        
        # Bulk index to OpenSearch
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        index_name = f"{index_prefix}-{datetime.utcnow().strftime('%Y.%m')}"
        
        # Prepare bulk request
        bulk_body = []
        for event in normalized_events:
            # Ensure timestamp
            if '@timestamp' not in event:
                event['@timestamp'] = datetime.utcnow().isoformat()
            bulk_body.append({"index": {"_index": index_name}})
            bulk_body.append(event)
        
        response = client.bulk(body=bulk_body, refresh=True)
        
        # Count successful and failed
        items = response.get('items', [])
        successful = sum(1 for item in items if item['index']['status'] in [200, 201])
        failed = len(items) - successful
        
        logger.info(f"Windows Events: Indexed {successful} events to {index_name}, {failed} failed")
        
        # Evaluate rules for each event and collect alerts
        all_alerts = []
        for event in normalized_events:
            alerts = evaluate_rules(event)
            all_alerts.extend(alerts)
        
        # Broadcast logs and alerts via WebSocket
        try:
            from app.websocket import broadcast_log, broadcast_alert
            for event in normalized_events:
                asyncio.create_task(broadcast_log(event))
            for alert in all_alerts:
                asyncio.create_task(broadcast_alert(alert))
        except Exception as ws_error:
            logger.warning(f"WebSocket broadcast failed: {ws_error}")
        
        return {
            "status": "success",
            "total": len(normalized_events),
            "successful": successful,
            "failed": failed,
            "index": index_name,
            "alerts_triggered": len(all_alerts)
        }
        
    except Exception as e:
        logger.error(f"Windows events ingestion error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/ingest/stats")
async def get_ingestion_stats():
    """
    Returns ingestion statistics
    
    Returns:
        dict: Ingestion statistics
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        
        # Get count of all logs
        response = client.count(index=f"{index_prefix}-*")
        total_logs = response['count']
        
        # Get index stats
        stats = client.indices.stats(index=f"{index_prefix}-*")
        total_size = stats['_all']['total']['store']['size_in_bytes']
        
        return {
            "total_logs": total_logs,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "indices": list(stats['indices'].keys())
        }
        
    except Exception as e:
        logger.error(f"Error getting ingestion stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
