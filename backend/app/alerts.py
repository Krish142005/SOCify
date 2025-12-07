"""
Alerts Endpoint
Fetch and manage security alerts
"""

from fastapi import APIRouter, HTTPException, Query
from app.opensearch_client import get_opensearch_client
from app.models.alert import AlertSeverity, AlertStatus, AlertSearchRequest, AlertUpdateRequest
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/alerts")
async def get_alerts(
    severity: Optional[List[str]] = Query(None, description="Filter by severity"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    rule_id: Optional[str] = Query(None, description="Filter by rule ID"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """
    Fetch alerts with filtering and pagination
    
    Returns:
        dict: Alert results with pagination
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("ALERTS_INDEX_PREFIX", "socify-alerts")
        
        # Build query
        must_conditions = []
        
        if severity:
            must_conditions.append({"terms": {"severity": severity}})
        
        if status:
            must_conditions.append({"terms": {"status": status}})
        
        if rule_id:
            must_conditions.append({"term": {"rule_id": rule_id}})
        
        # Time range filter
        if start_time or end_time:
            time_range = {}
            if start_time:
                time_range["gte"] = start_time
            if end_time:
                time_range["lte"] = end_time
            else:
                time_range["lte"] = datetime.utcnow().isoformat()
            
            must_conditions.append({
                "range": {
                    "@timestamp": time_range
                }
            })
        else:
            # Default: last 7 days
            must_conditions.append({
                "range": {
                    "@timestamp": {
                        "gte": (datetime.utcnow() - timedelta(days=7)).isoformat()
                    }
                }
            })
        
        # Build final query
        search_body = {
            "query": {
                "bool": {
                    "must": must_conditions if must_conditions else [{"match_all": {}}]
                }
            },
            "sort": [
                {"@timestamp": {"order": sort_order}}
            ],
            "from": offset,
            "size": limit
        }
        
        # Execute search
        response = client.search(
            index=f"{index_prefix}-*",
            body=search_body
        )
        
        # Format results
        hits = response['hits']['hits']
        total = response['hits']['total']['value']
        
        results = []
        for hit in hits:
            result = hit['_source']
            result['_id'] = hit['_id']
            result['_index'] = hit['_index']
            results.append(result)
        
        return {
            "total": total,
            "count": len(results),
            "offset": offset,
            "limit": limit,
            "alerts": results
        }
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")

@router.get("/alerts/{alert_id}")
async def get_alert_by_id(alert_id: str):
    """
    Get a specific alert by ID
    
    Returns:
        dict: Alert details
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("ALERTS_INDEX_PREFIX", "socify-alerts")
        
        # Search for alert by alert_id field
        search_body = {
            "query": {
                "term": {
                    "alert_id": alert_id
                }
            }
        }
        
        response = client.search(
            index=f"{index_prefix}-*",
            body=search_body
        )
        
        if response['hits']['total']['value'] == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        hit = response['hits']['hits'][0]
        result = hit['_source']
        result['_id'] = hit['_id']
        result['_index'] = hit['_index']
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert {alert_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/alerts/{alert_id}")
async def update_alert(alert_id: str, update: AlertUpdateRequest):
    """
    Update alert status and metadata
    
    Returns:
        dict: Update confirmation
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("ALERTS_INDEX_PREFIX", "socify-alerts")
        
        # Find the alert first
        search_body = {
            "query": {
                "term": {
                    "alert_id": alert_id
                }
            }
        }
        
        response = client.search(
            index=f"{index_prefix}-*",
            body=search_body
        )
        
        if response['hits']['total']['value'] == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        hit = response['hits']['hits'][0]
        doc_id = hit['_id']
        index_name = hit['_index']
        
        # Prepare update
        update_body = {
            "doc": {
                "status": update.status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
        if update.assigned_to:
            update_body["doc"]["assigned_to"] = update.assigned_to
        
        if update.notes:
            # Append to notes array
            current_notes = hit['_source'].get('notes', [])
            current_notes.append({
                "timestamp": datetime.utcnow().isoformat(),
                "note": update.notes
            })
            update_body["doc"]["notes"] = current_notes
        
        # Update document
        client.update(
            index=index_name,
            id=doc_id,
            body=update_body,
            refresh=True
        )
        
        logger.info(f"Updated alert {alert_id} to status {update.status}")
        
        return {
            "status": "success",
            "alert_id": alert_id,
            "updated_fields": update_body["doc"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert {alert_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/stats/summary")
async def get_alert_stats():
    """
    Get alert statistics and summary
    
    Returns:
        dict: Alert statistics
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("ALERTS_INDEX_PREFIX", "socify-alerts")
        
        # Get aggregations
        search_body = {
            "size": 0,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": (datetime.utcnow() - timedelta(days=30)).isoformat()
                    }
                }
            },
            "aggs": {
                "by_severity": {
                    "terms": {
                        "field": "severity",
                        "size": 10
                    }
                },
                "by_status": {
                    "terms": {
                        "field": "status",
                        "size": 10
                    }
                },
                "by_rule": {
                    "terms": {
                        "field": "rule_name.keyword",
                        "size": 10
                    }
                },
                "timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "fixed_interval": "1d"
                    }
                }
            }
        }
        
        response = client.search(
            index=f"{index_prefix}-*",
            body=search_body
        )
        
        total_alerts = response['hits']['total']['value']
        
        return {
            "total_alerts": total_alerts,
            "by_severity": [
                {"severity": b['key'], "count": b['doc_count']}
                for b in response['aggregations']['by_severity']['buckets']
            ],
            "by_status": [
                {"status": b['key'], "count": b['doc_count']}
                for b in response['aggregations']['by_status']['buckets']
            ],
            "top_rules": [
                {"rule": b['key'], "count": b['doc_count']}
                for b in response['aggregations']['by_rule']['buckets']
            ],
            "timeline": [
                {"date": b['key_as_string'], "count": b['doc_count']}
                for b in response['aggregations']['timeline']['buckets']
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting alert stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
