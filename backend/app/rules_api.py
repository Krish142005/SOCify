from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.rule_engine import get_rules, get_rule_by_id, reload_rules

router = APIRouter()

@router.get("/rules", response_model=List[Dict[str, Any]])
def list_rules():
    """
    Get all detection rules
    """
    return get_rules()

@router.get("/rules/{rule_id}", response_model=Dict[str, Any])
def get_rule(rule_id: str):
    """
    Get a specific rule by ID
    """
    rule = get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.post("/rules/reload")
def reload_rules_endpoint():
    """
    Reload rules from the rules file
    """
    return reload_rules()
