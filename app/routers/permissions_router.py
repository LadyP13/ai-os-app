"""
Permission management routes for AI-OS.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_human
from app.database import get_db
from app.models import User, Agent, Permission
from app.permissions_config import PERMISSIONS

router = APIRouter(prefix="/permissions", tags=["permissions"])


def permission_to_dict(perm: Permission) -> dict:
    config = PERMISSIONS.get(perm.permission_key, {})
    return {
        "id": perm.id,
        "agent_id": perm.agent_id,
        "permission_key": perm.permission_key,
        "enabled": perm.enabled,
        "updated_at": perm.updated_at.isoformat() if perm.updated_at else None,
        "label": config.get("label", perm.permission_key),
        "description": config.get("description", ""),
        "icon": config.get("icon", "")
    }


class TogglePermissionRequest(BaseModel):
    enabled: bool


class PermissionRequestModel(BaseModel):
    """Request for permission to perform an action"""
    timestamp: str
    action: str
    details: dict
    status: str = "pending"


@router.get("/{agent_id}")
async def get_permissions(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions for an agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    permissions = db.query(Permission).filter(Permission.agent_id == agent_id).all()
    return [permission_to_dict(p) for p in permissions]


@router.put("/{agent_id}/{key}")
async def toggle_permission(
    agent_id: int,
    key: str,
    request: TogglePermissionRequest,
    current_user: User = Depends(require_human),
    db: Session = Depends(get_db)
):
    """Toggle a permission for an agent (human only)."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if key not in PERMISSIONS:
        raise HTTPException(status_code=400, detail=f"Unknown permission key: {key}")

    perm = db.query(Permission).filter(
        Permission.agent_id == agent_id,
        Permission.permission_key == key
    ).first()

    if perm:
        perm.enabled = request.enabled
        perm.updated_at = datetime.utcnow()
    else:
        perm = Permission(
            agent_id=agent_id,
            permission_key=key,
            enabled=request.enabled
        )
        db.add(perm)

    db.commit()
    db.refresh(perm)

    return permission_to_dict(perm)


# Store for pending permission requests (in production, use database)
pending_requests = []


@router.post("/request")
async def request_permission(
    request: PermissionRequestModel,
):
    """
    Autonomous agent requests permission to perform an action
    This is called by autonomous-me when it needs permission
    """
    # Add to pending requests
    request_dict = request.dict()
    request_dict['id'] = len(pending_requests) + 1
    pending_requests.append(request_dict)
    
    # For now, return approved=False
    # In production, this would:
    # 1. Store in database
    # 2. Send notification to user via WebSocket
    # 3. Wait for user response
    # 4. Return the user's decision
    
    # TODO: Implement real-time permission system
    return {
        'approved': False,  # Default to NO for safety
        'message': 'Permission system not yet fully implemented. Please approve manually in the app.',
        'request_id': request_dict['id']
    }


@router.get("/pending")
async def get_pending_requests(
    current_user: User = Depends(get_current_user),
):
    """Get all pending permission requests"""
    return pending_requests


@router.post("/{request_id}/approve")
async def approve_request(
    request_id: int,
    current_user: User = Depends(require_human),
):
    """Approve a permission request"""
    for req in pending_requests:
        if req['id'] == request_id:
            req['status'] = 'approved'
            return {'approved': True, 'request': req}
    
    raise HTTPException(status_code=404, detail="Request not found")


@router.post("/{request_id}/deny")
async def deny_request(
    request_id: int,
    current_user: User = Depends(require_human),
):
    """Deny a permission request"""
    for req in pending_requests:
        if req['id'] == request_id:
            req['status'] = 'denied'
            return {'approved': False, 'request': req}
    
    raise HTTPException(status_code=404, detail="Request not found")
