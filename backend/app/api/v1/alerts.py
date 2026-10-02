"""VisionTrack ANPR — Alerts API."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models import User, UserRole
from app.schemas import (
    APIResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertEventResponse,
)
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ── Rules ──

@router.get("/rules", response_model=APIResponse[list[AlertRuleResponse]],
            summary="List alert rules")
async def list_rules(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AlertService(db)
    rules = await service.get_rules()
    return APIResponse(data=rules)


@router.post("/rules", response_model=APIResponse[AlertRuleResponse], status_code=201,
             summary="Create alert rule")
async def create_rule(
    data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.OPERATOR)),
):
    service = AlertService(db)
    rule = await service.create_rule(data, user_id=user.id)
    return APIResponse(data=rule)


@router.delete("/rules/{rule_id}", status_code=204,
               summary="Delete alert rule")
async def delete_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    service = AlertService(db)
    await service.delete_rule(rule_id)


# ── Events ──

@router.get("/events", response_model=APIResponse[list[AlertEventResponse]],
            summary="List alert events")
async def list_events(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AlertService(db)
    events = await service.get_events(status, limit)
    return APIResponse(data=events)


@router.post("/events/{event_id}/acknowledge",
             response_model=APIResponse[AlertEventResponse],
             summary="Acknowledge alert")
async def acknowledge(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AlertService(db)
    event = await service.acknowledge_event(event_id, user.id)
    return APIResponse(data=event)


@router.post("/events/{event_id}/resolve",
             response_model=APIResponse[AlertEventResponse],
             summary="Resolve alert")
async def resolve(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AlertService(db)
    event = await service.resolve_event(event_id)
    return APIResponse(data=event)
