"""
Rule Engine - Core Detection Logic
Evaluates events against SIEM detection rules and generates alerts
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.opensearch_client import get_opensearch_client
import logging
import os

logger = logging.getLogger(__name__)

# Load rules from JSON file
RULES_FILE = os.path.join(os.path.dirname(__file__), 'rules', 'rules.json')
with open(RULES_FILE, 'r') as f:
    RULES = json.load(f)

logger.info(f"Loaded {len(RULES)} detection rules")

def evaluate_rules(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates all applicable rules against an incoming event
    
    Args:
        event: Normalized event in ECS format
        
    Returns:
        list: Generated alerts
    """
    alerts = []
    # Debug logging disabled
    # with open("C:/Users/91751/OneDrive/Desktop/Socify3/backend/debug_log_abs.txt", "a", encoding="utf-8") as f:
    #     f.write(f"Starting rule evaluation for event: {event.get('@timestamp')}\n")
    
    for rule in RULES:
        try:
            # Check if rule applies to this event
            if not check_filter(rule, event):
                # Debug logging disabled
                # with open("C:/Users/91751/OneDrive/Desktop/Socify3/backend/debug_log_abs.txt", "a", encoding="utf-8") as f:
                #     f.write(f"Rule {rule['rule_id']} filter mismatch\n")
                continue
            
            # Debug logging disabled
            # with open("C:/Users/91751/OneDrive/Desktop/Socify3/backend/debug_log_abs.txt", "a", encoding="utf-8") as f:
            #     f.write(f"Evaluating rule {rule['rule_id']} against event\n")
            
            # Evaluate based on rule type
            matched = False
            
            if rule['type'] == 'boolean':
                matched = evaluate_boolean_rule(rule, event)
            
            elif rule['type'] == 'threshold':
                matched = evaluate_threshold_rule(rule, event)
            
            elif rule['type'] == 'correlation':
                matched = evaluate_correlation_rule(rule, event)
            
            elif rule['type'] == 'pattern':
                matched = evaluate_pattern_rule(rule, event)
            
            # Generate alert if rule matched
            if matched:
                alert = generate_alert(rule, event)
                alerts.append(alert)
                logger.info(f"Rule {rule['rule_id']} triggered: {rule.get('rule_name', 'Unknown')}")
        
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.get('rule_id', 'unknown')}: {str(e)}")
    
    # Store alerts in OpenSearch
    if alerts:
        store_alerts(alerts)
    
    return alerts

def check_filter(rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
    """
    Checks if rule filter conditions match the event
    
    Args:
        rule: Rule definition
        event: Event to check
        
    Returns:
        bool: True if filter matches or no filter defined
    """
    # Check log_source filter (application, system, security)
    if 'log_source' in rule:
        log_source = rule['log_source'].lower()
        event_log_source = get_nested_field(event, 'log.source')
        if event_log_source and event_log_source.lower() != log_source:
            return False
    
    if 'filter' not in rule:
        return True
    
    filter_config = rule['filter']
    
    # Handle single filter
    if 'field' in filter_config:
        return check_condition(filter_config, event)
    
    # Handle multiple filters (all must match)
    for key, value in filter_config.items():
        if key == 'field':
            continue
        field_value = get_nested_field(event, key)
        if field_value != value:
            return False
    
    return True

def check_condition(condition: Dict[str, Any], event: Dict[str, Any]) -> bool:
    """
    Checks if a condition matches the event
    """
    field = condition.get('field')
    operator = condition.get('operator', 'equals')
    value = condition.get('value')
    
    field_value = get_nested_field(event, field)
    
    # Debug logging disabled
    # with open("C:/Users/91751/OneDrive/Desktop/Socify3/backend/debug_log_abs.txt", "a", encoding="utf-8") as f:
    #     f.write(f"Checking condition: {field} ({field_value}) {operator} {value}\n")
    
    if field_value is None:
        return False
    
    if operator == 'equals':
        return field_value == value
    elif operator == 'in':
        return field_value in value
    elif operator == 'not_in':
        return field_value not in value
    elif operator == 'contains':
        return value in str(field_value)
    elif operator == 'gt':
        return float(field_value) > float(value)
    elif operator == 'lt':
        return float(field_value) < float(value)
    elif operator == 'gte':
        return float(field_value) >= float(value)
    elif operator == 'lte':
        return float(field_value) <= float(value)
    
    return False

def evaluate_boolean_rule(rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
    """
    Evaluates simple boolean/field matching rules
    
    Example: event.action == "ssh_login_failed"
    """
    if 'match' not in rule:
        # Debug logging disabled
        # with open("C:/Users/91751/OneDrive/Desktop/Socify3/backend/debug_log_abs.txt", "a", encoding="utf-8") as f:
        #     f.write(f"Rule {rule.get('rule_id')} has no match block\n")
        return False
        
    match_conditions = rule['match']
    # Debug logging disabled
    # with open("C:/Users/91751/OneDrive/Desktop/Socify3/backend/debug_log_abs.txt", "a", encoding="utf-8") as f:
    #     f.write(f"Rule {rule.get('rule_id')} match keys: {list(match_conditions.keys())}\n")
    
    for key, value in match_conditions.items():
        # Parse operator from key suffix
        field = key
        operator = 'equals'
        
        if key.endswith('_in'):
            field = key[:-3]
            operator = 'in'
        elif key.endswith('_not_in'):
            field = key[:-7]
            operator = 'not_in'
        elif key.endswith('_contains'):
            field = key[:-9]
            operator = 'contains'
        elif key.endswith('_gt'):
            field = key[:-3]
            operator = 'gt'
        elif key.endswith('_lt'):
            field = key[:-3]
            operator = 'lt'
        elif key.endswith('_gte'):
            field = key[:-4]
            operator = 'gte'
        elif key.endswith('_lte'):
            field = key[:-4]
            operator = 'lte'
            
        # Check condition
        condition = {
            'field': field,
            'operator': operator,
            'value': value
        }
        
        if not check_condition(condition, event):
            return False
            
    return True

def evaluate_threshold_rule(rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
    """
    Evaluates threshold rules - checks if event count exceeds threshold
    
    Example: >5 failed logins from same IP in 5 minutes
    """
    # First check if current event matches the rule criteria
    if not evaluate_boolean_rule(rule, event):
        return False
    
    try:
        client = get_opensearch_client()
        
        # Parse timeframe
        timeframe_minutes = parse_timeframe(rule.get('time_window', '5m'))
        time_ago = datetime.utcnow() - timedelta(minutes=timeframe_minutes)
        
        # Build query
        must_conditions = [
            {"range": {"@timestamp": {"gte": time_ago.isoformat()}}}
        ]
        
        # Add match conditions to query
        if 'match' in rule:
            for key, value in rule['match'].items():
                field = key
                operator = 'equals'
                
                if key.endswith('_in'):
                    field = key[:-3]
                    operator = 'in'
                elif key.endswith('_not_in'):
                    field = key[:-7]
                    operator = 'not_in'
                elif key.endswith('_contains'):
                    field = key[:-9]
                    operator = 'contains'
                # Note: gt/lt not typically used in threshold match filters for query, 
                # but we can support basic term/terms
                
                if operator == 'in':
                    must_conditions.append({"terms": {field: value}})
                elif operator == 'equals':
                    must_conditions.append({"term": {field: value}})
                # For other operators, we might need range queries or wildcards, 
                # but for now let's stick to term/terms which cover most cases
        
        # Build aggregation
        group_by = rule.get('group_by')
        threshold = rule.get('threshold', 1)
        
        search_body = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            },
            "size": 0
        }
        
        if group_by:
            search_body["aggs"] = {
                "group_count": {
                    "terms": {
                        "field": group_by,
                        "min_doc_count": threshold,
                        "size": 100
                    }
                }
            }
        
        # Execute query
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        response = client.search(
            index=f"{index_prefix}-*",
            body=search_body
        )
        
        # Check results
        if group_by:
            buckets = response['aggregations']['group_count']['buckets']
            return len(buckets) > 0
        else:
            total_count = response['hits']['total']['value']
            return total_count >= threshold
    
    except Exception as e:
        logger.error(f"Error in threshold rule evaluation: {str(e)}")
        return False

def evaluate_correlation_rule(rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
    """
    Evaluates correlation rules - checks if multiple conditions occur within timeframe
    
    Example: Failed login followed by privilege escalation from same user
    """
    conditions = rule['conditions']
    correlation_key = rule['correlation_key']
    
    # Get correlation value from current event
    correlation_value = get_nested_field(event, correlation_key)
    if not correlation_value:
        return False
    
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("LOGS_INDEX_PREFIX", "socify-logs")
        
        # Check if all conditions are met
        for condition in conditions:
            timeframe_minutes = parse_timeframe(condition['timeframe'])
            time_ago = datetime.utcnow() - timedelta(minutes=timeframe_minutes)
            
            # Build query
            must_conditions = [
                {"term": {correlation_key: correlation_value}},
                {"range": {"@timestamp": {"gte": time_ago.isoformat()}}}
            ]
            
            # Add condition-specific filters
            field = condition.get('field')
            value = condition.get('value')
            operator = condition.get('operator', 'equals')
            
            if operator == 'in':
                must_conditions.append({"terms": {field: value}})
            else:
                must_conditions.append({"term": {field: value}})
            
            search_body = {
                "query": {
                    "bool": {
                        "must": must_conditions
                    }
                },
                "size": 0
            }
            
            response = client.search(
                index=f"{index_prefix}-*",
                body=search_body
            )
            
            # If any condition is not met, return False
            if response['hits']['total']['value'] == 0:
                return False
        
        # All conditions met
        return True
    
    except Exception as e:
        logger.error(f"Error in correlation rule evaluation: {str(e)}")
        return False

def evaluate_pattern_rule(rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
    """
    Evaluates pattern-based rules using regex
    
    Example: File extension matches ransomware patterns
    """
    condition = rule['condition']
    field = condition.get('field')
    pattern = condition.get('pattern')
    
    field_value = get_nested_field(event, field)
    
    if not field_value or not pattern:
        return False
    
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        return bool(regex.search(str(field_value)))
    except Exception as e:
        logger.error(f"Error in pattern matching: {str(e)}")
        return False

def generate_alert(rule: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates alert document from matched rule and event
    
    Args:
        rule: Matched rule
        event: Triggering event
        
    Returns:
        dict: Alert document
    """
    timestamp = datetime.utcnow()
    
    # Extract relevant fields from event
    source_ips = []
    if 'source' in event and 'ip' in event['source']:
        source_ips.append(event['source']['ip'])
    
    dest_ips = []
    if 'destination' in event and 'ip' in event['destination']:
        dest_ips.append(event['destination']['ip'])
    
    usernames = []
    if 'user' in event and 'name' in event['user']:
        usernames.append(event['user']['name'])
    
    hostnames = []
    if 'host' in event and 'name' in event['host']:
        hostnames.append(event['host']['name'])
    
    alert = {
        "@timestamp": timestamp.isoformat(),
        "alert_id": f"{rule['rule_id']}_{int(timestamp.timestamp() * 1000)}",
        "rule_id": rule['rule_id'],
        "rule_name": rule.get('rule_name', rule.get('name', 'Unknown Rule')),
        "severity": rule.get('severity', 'Medium'),
        "description": rule.get('description', f"Alert triggered by rule {rule['rule_id']}"),
        "matched_events": [event],
        "event_count": 1,
        "status": "open",
        "source_ips": source_ips,
        "destination_ips": dest_ips,
        "usernames": usernames,
        "hostnames": hostnames,
        "mitre_tactics": rule.get('mitre_tactics', []),
        "mitre_techniques": rule.get('mitre_techniques', []),
        "tags": ["auto-generated"],
        "created_at": timestamp.isoformat()
    }
    
    return alert

def store_alerts(alerts: List[Dict[str, Any]]):
    """
    Stores alerts in OpenSearch alerts index
    
    Args:
        alerts: List of alert documents
    """
    try:
        client = get_opensearch_client()
        index_prefix = os.getenv("ALERTS_INDEX_PREFIX", "socify-alerts")
        index_name = f"{index_prefix}-{datetime.utcnow().strftime('%Y.%m')}"
        
        # Bulk index alerts
        bulk_body = []
        for alert in alerts:
            bulk_body.append({"index": {"_index": index_name}})
            bulk_body.append(alert)
        
        response = client.bulk(body=bulk_body, refresh=True)
        
        if response.get('errors'):
            logger.warning(f"Some alerts failed to index: {response}")
        else:
            logger.info(f"Successfully stored {len(alerts)} alerts in {index_name}")
    
    except Exception as e:
        logger.error(f"Error storing alerts: {str(e)}", exc_info=True)

def get_nested_field(obj: Dict[str, Any], field_path: str) -> Any:
    """
    Gets nested field value using dot notation
    
    Example: 'source.ip' -> obj['source']['ip']
    """
    if not field_path:
        return None
    
    keys = field_path.split('.')
    value = obj
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    
    return value

def parse_timeframe(timeframe: str) -> int:
    """
    Converts timeframe string to minutes
    
    Examples:
        '5m' -> 5
        '1h' -> 60
        '1d' -> 1440
    """
    if not timeframe:
        return 5  # Default 5 minutes
    
    unit = timeframe[-1].lower()
    try:
        value = int(timeframe[:-1])
    except ValueError:
        return 5
    
    if unit == 'm':
        return value
    elif unit == 'h':
        return value * 60
    elif unit == 'd':
        return value * 1440
    
    return value

def reload_rules():
    """
    Reloads rules from JSON file
    Useful for dynamic rule updates without restarting
    """
    global RULES
    try:
        with open(RULES_FILE, 'r') as f:
            RULES = json.load(f)
        logger.info(f"Reloaded {len(RULES)} detection rules")
        return {"status": "success", "count": len(RULES)}
    except Exception as e:
        logger.error(f"Error reloading rules: {str(e)}")
        return {"status": "error", "message": str(e)}

def get_rules() -> List[Dict[str, Any]]:
    """
    Returns all loaded rules
    """
    return RULES

def get_rule_by_id(rule_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns a specific rule by ID
    """
    for rule in RULES:
        if rule['rule_id'] == rule_id:
            return rule
    return None
