"""VisionTrack ANPR — Alert Service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models import AlertRule, AlertEvent, AlertSeverity, AlertStatus, DetectionEvent
from app.schemas import AlertRuleCreate, AlertRuleResponse, AlertEventResponse

logger = get_logger("alert_service")


class AlertService:
    """Manages alert rules and events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Alert Rules ──

    async def create_rule(self, data: AlertRuleCreate, user_id: str | None = None) -> AlertRuleResponse:
        rule = AlertRule(
            name=data.name,
            description=data.description,
            rule_type=data.rule_type,
            conditions=data.conditions,
            severity=AlertSeverity(data.severity),
            enabled=data.enabled,
            camera_ids=data.camera_ids,
            created_by=user_id,
        )
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        return AlertRuleResponse.model_validate(rule)

    async def get_rules(self) -> list[AlertRuleResponse]:
        result = await self.db.execute(select(AlertRule).order_by(desc(AlertRule.created_at)))
        rules = result.scalars().all()
        return [AlertRuleResponse.model_validate(r) for r in rules]

    async def delete_rule(self, rule_id: str) -> None:
        result = await self.db.execute(select(AlertRule).where(AlertRule.id == rule_id))
        rule = result.scalar_one_or_none()
        if not rule:
            raise NotFoundError("Alert rule", rule_id)
        await self.db.delete(rule)

    # ── Alert Events ──

    async def get_events(
        self, status: str | None = None, limit: int = 50
    ) -> list[AlertEventResponse]:
        query = select(AlertEvent).order_by(desc(AlertEvent.created_at)).limit(limit)
        if status:
            query = query.where(AlertEvent.status == AlertStatus(status))
        result = await self.db.execute(query)
        events = result.scalars().all()
        return [AlertEventResponse.model_validate(e) for e in events]

    async def acknowledge_event(self, event_id: str, user_id: str) -> AlertEventResponse:
        result = await self.db.execute(select(AlertEvent).where(AlertEvent.id == event_id))
        event = result.scalar_one_or_none()
        if not event:
            raise NotFoundError("Alert event", event_id)
        event.status = AlertStatus.ACKNOWLEDGED
        event.acknowledged_by = user_id
        event.acknowledged_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(event)
        return AlertEventResponse.model_validate(event)

    async def resolve_event(self, event_id: str) -> AlertEventResponse:
        result = await self.db.execute(select(AlertEvent).where(AlertEvent.id == event_id))
        event = result.scalar_one_or_none()
        if not event:
            raise NotFoundError("Alert event", event_id)
        event.status = AlertStatus.RESOLVED
        event.resolved_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(event)
        return AlertEventResponse.model_validate(event)

    async def evaluate_detection(self, detection: DetectionEvent) -> list[AlertEvent]:
        """Evaluate all active rules against a detection. Create alerts for matches."""
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.enabled == True)
        )
        rules = result.scalars().all()
        triggered = []

        for rule in rules:
            if self._matches_rule(rule, detection):
                alert = AlertEvent(
                    rule_id=rule.id,
                    detection_id=detection.id,
                    severity=rule.severity,
                    title=f"Alert: {rule.name}",
                    message=self._build_alert_message(rule, detection),
                )
                self.db.add(alert)
                triggered.append(alert)
                logger.info(
                    "alert_triggered",
                    rule_id=rule.id,
                    detection_id=detection.id,
                    severity=rule.severity.value,
                )

        if triggered:
            await self.db.flush()

        return triggered

    def _matches_rule(self, rule: AlertRule, detection: DetectionEvent) -> bool:
        """Check if a detection matches an alert rule."""
        conditions = rule.conditions or {}

        # Check camera filter
        if rule.camera_ids and detection.camera_id not in rule.camera_ids:
            return False

        if rule.rule_type == "plate_match":
            target = conditions.get("plate_number", "")
            return detection.plate_number and target.upper() in detection.plate_number.upper()

        elif rule.rule_type == "unknown_plate":
            return detection.plate_number is None or not detection.plate_valid

        elif rule.rule_type == "vehicle_type":
            target = conditions.get("vehicle_type", "")
            return detection.vehicle_type and detection.vehicle_type.value == target

        elif rule.rule_type == "vehicle_color":
            target = conditions.get("vehicle_color", "").lower()
            return detection.vehicle_color and detection.vehicle_color.lower() == target

        elif rule.rule_type == "low_confidence":
            threshold = conditions.get("threshold", 0.5)
            return detection.plate_confidence is not None and detection.plate_confidence < threshold

        return False

    def _build_alert_message(self, rule: AlertRule, detection: DetectionEvent) -> str:
        parts = [f"Rule: {rule.name}"]
        if detection.plate_number:
            parts.append(f"Plate: {detection.plate_number}")
        if detection.vehicle_type:
            parts.append(f"Vehicle: {detection.vehicle_type.value}")
        if detection.plate_confidence is not None:
            parts.append(f"Confidence: {detection.plate_confidence:.0%}")
        return " | ".join(parts)
