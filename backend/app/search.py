"""
Search Endpoint
Query logs from OpenSearch with filtering and pagination
"""

from fastapi import APIRouter, HTTPException, Query
from app.opensearch_client import get_opensearch_client
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/search")
async def search_logs(
    query: Optional[str] = Query(None, description="Search query string"),
    source_ip: Optional[str] = Query(None, description="Filter by source IP"),
    destination_ip: Optional[str] = Query(None, description="Filter by destination IP"),
    event_action: Optional[str] = Query(None, description="Filter by event action"),
    event_category: Optional[str] = Query(None, description="Filter by event category"),
    username: Optional[str] = Query(None, description="Filter by username"),
    hostname: Optional[str] = Query(None, description="Filter by hostname"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """
    Search logs with various filters
    
    Returns:
        dict: Search results with pagination
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        
        # Build query
        must_conditions = []
        
        # Text search
        if query:
            must_conditions.append({
                "multi_match": {
                    "query": query,
                    "fields": ["message", "raw_log", "process.name", "file.path"]
                }
            })
        
        # Field filters
        if source_ip:
            must_conditions.append({"term": {"source.ip": source_ip}})
        
        if destination_ip:
            must_conditions.append({"term": {"destination.ip": destination_ip}})
        
        if event_action:
            must_conditions.append({"term": {"event.action": event_action}})
        
        if event_category:
            must_conditions.append({"term": {"event.category": event_category}})
        
        if username:
            must_conditions.append({"term": {"user.name": username}})
        
        if hostname:
            must_conditions.append({"term": {"host.name": hostname}})
        
        if severity:
            must_conditions.append({"term": {"event.severity": severity}})
        
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
        
        # Default time range: last 24 hours if no filters specified
        if not start_time and not end_time and not must_conditions:
            must_conditions.append({
                "range": {
                    "@timestamp": {
                        "gte": (datetime.utcnow() - timedelta(hours=24)).isoformat()
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
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search/aggregations")
async def get_aggregations(
    field: str = Query(..., description="Field to aggregate on"),
    start_time: Optional[str] = Query(None, description="Start time"),
    end_time: Optional[str] = Query(None, description="End time"),
    size: int = Query(10, ge=1, le=100, description="Number of buckets")
):
    """
    Get aggregations for a specific field
    
    Returns:
        dict: Aggregation results
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        
        # Build query with time range
        query = {"match_all": {}}
        if start_time or end_time:
            time_range = {}
            if start_time:
                time_range["gte"] = start_time
            if end_time:
                time_range["lte"] = end_time
            
            query = {
                "range": {
                    "@timestamp": time_range
                }
            }
        
        # Build aggregation
        search_body = {
            "query": query,
            "size": 0,
            "aggs": {
                "field_agg": {
                    "terms": {
                        "field": field,
                        "size": size
                    }
                }
            }
        }
        
        response = client.search(
            index=f"{index_prefix}-*",
            body=search_body
        )
        
        buckets = response['aggregations']['field_agg']['buckets']
        
        return {
            "field": field,
            "total_docs": response['hits']['total']['value'],
            "buckets": [
                {
                    "key": bucket['key'],
                    "count": bucket['doc_count']
                }
                for bucket in buckets
            ]
        }
        
    except Exception as e:
        logger.error(f"Aggregation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/timeline")
async def get_timeline(
    interval: str = Query("1h", description="Time interval (1m, 5m, 1h, 1d)"),
    start_time: Optional[str] = Query(None, description="Start time"),
    end_time: Optional[str] = Query(None, description="End time"),
    event_category: Optional[str] = Query(None, description="Filter by event category")
):
    """
    Get event timeline with time-based aggregations
    
    Returns:
        dict: Timeline data
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        
        # Build query
        must_conditions = []
        
        if event_category:
            must_conditions.append({"term": {"event.category": event_category}})
        
        # Time range
        time_range = {}
        if start_time:
            time_range["gte"] = start_time
        else:
            time_range["gte"] = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        if end_time:
            time_range["lte"] = end_time
        else:
            time_range["lte"] = datetime.utcnow().isoformat()
        
        must_conditions.append({
            "range": {
                "@timestamp": time_range
            }
        })
        
        # Build aggregation
        search_body = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            },
            "size": 0,
            "aggs": {
                "timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "fixed_interval": interval,
                        "min_doc_count": 0
                    }
                }
            }
        }
        
        response = client.search(
            index=f"{index_prefix}-*",
            body=search_body
        )
        
        buckets = response['aggregations']['timeline']['buckets']
        
        return {
            "interval": interval,
            "total_events": response['hits']['total']['value'],
            "timeline": [
                {
                    "timestamp": bucket['key_as_string'],
                    "count": bucket['doc_count']
                }
                for bucket in buckets
            ]
        }
        
    except Exception as e:
        logger.error(f"Timeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
