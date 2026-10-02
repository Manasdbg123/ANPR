"""VisionTrack ANPR — AI Service with tool-based query processing."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, select, distinct, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models import DetectionEvent, Camera, AlertEvent
from app.schemas import AIQueryResponse

logger = get_logger("ai_service")


# Tool definitions for structured query building
TOOLS = {
    "search_detections": {
        "description": "Search vehicle detections by plate number, vehicle type, color, camera, date range, or confidence",
        "parameters": ["plate_number", "vehicle_type", "vehicle_color", "camera_name", "start_date", "end_date", "min_confidence", "limit"],
    },
    "get_statistics": {
        "description": "Get aggregate statistics: total vehicles, unique plates, averages",
        "parameters": ["metric", "start_date", "end_date", "group_by"],
    },
    "get_camera_stats": {
        "description": "Get per-camera statistics and comparisons",
        "parameters": ["camera_name"],
    },
    "get_plate_history": {
        "description": "Get detection history for a specific plate",
        "parameters": ["plate_number"],
    },
}


class AIService:
    """AI assistant that translates natural language to structured ANPR queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def query(self, message: str, user_id: str | None = None) -> AIQueryResponse:
        """Process a natural language query using intent detection and tool execution."""
        msg_lower = message.lower().strip()
        tool_calls = []

        try:
            # Intent detection — pattern matching for common queries
            if any(w in msg_lower for w in ["how many", "total", "count"]):
                result, tools = await self._handle_count_query(msg_lower)
            elif any(w in msg_lower for w in ["show", "list", "find", "search"]):
                result, tools = await self._handle_search_query(msg_lower)
            elif any(w in msg_lower for w in ["busiest", "most", "top", "highest"]):
                result, tools = await self._handle_ranking_query(msg_lower)
            elif any(w in msg_lower for w in ["camera"]):
                result, tools = await self._handle_camera_query(msg_lower)
            elif any(w in msg_lower for w in ["confidence", "low", "accuracy"]):
                result, tools = await self._handle_confidence_query(msg_lower)
            elif any(w in msg_lower for w in ["plate", "number"]):
                result, tools = await self._handle_plate_query(msg_lower)
            else:
                result = await self._handle_general_query(msg_lower)
                tools = []

            tool_calls = tools
        except Exception as e:
            logger.error("ai_query_error", error=str(e))
            result = "I encountered an error processing your query. Please try rephrasing your question."

        return AIQueryResponse(
            response=result,
            tool_calls=tool_calls,
        )

    async def _handle_count_query(self, msg: str) -> tuple[str, list[dict]]:
        """Handle counting queries."""
        tools = [{"tool": "get_statistics", "params": {"metric": "count"}}]

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        yesterday = today - timedelta(days=1)

        if "today" in msg:
            count_q = select(func.count(DetectionEvent.id)).where(
                DetectionEvent.timestamp >= today
            )
            tools[0]["params"]["start_date"] = today.isoformat()
        elif "yesterday" in msg:
            count_q = select(func.count(DetectionEvent.id)).where(
                and_(DetectionEvent.timestamp >= yesterday, DetectionEvent.timestamp < today)
            )
        elif "unique" in msg:
            count_q = select(func.count(distinct(DetectionEvent.plate_number))).where(
                DetectionEvent.plate_number.isnot(None)
            )
        else:
            count_q = select(func.count(DetectionEvent.id))

        result = await self.db.execute(count_q)
        count = result.scalar() or 0

        if "unique" in msg:
            response = f"There are **{count:,}** unique vehicle plates in the system."
        elif "today" in msg:
            response = f"**{count:,}** vehicles have been detected today."
        elif "yesterday" in msg:
            response = f"**{count:,}** vehicles were detected yesterday."
        else:
            response = f"There are **{count:,}** total vehicle detections in the system."

        return response, tools

    async def _handle_search_query(self, msg: str) -> tuple[str, list[dict]]:
        """Handle search/show queries."""
        tools = [{"tool": "search_detections", "params": {}}]
        query = select(DetectionEvent).order_by(desc(DetectionEvent.timestamp)).limit(10)
        conditions = []

        # Extract color
        colors = ["white", "black", "red", "blue", "green", "silver", "grey", "gray", "yellow"]
        detected_color = None
        for color in colors:
            if color in msg:
                detected_color = color
                conditions.append(DetectionEvent.vehicle_color.ilike(f"%{color}%"))
                tools[0]["params"]["vehicle_color"] = color
                break

        # Extract vehicle type
        types = {"suv": "suv", "car": "car", "truck": "truck", "bus": "bus", "motorcycle": "motorcycle", "bike": "motorcycle"}
        detected_type = None
        for keyword, vtype in types.items():
            if keyword in msg:
                detected_type = vtype
                conditions.append(DetectionEvent.vehicle_type == vtype)
                tools[0]["params"]["vehicle_type"] = vtype
                break

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        detections = result.scalars().all()

        if not detections:
            desc_parts = []
            if detected_color:
                desc_parts.append(detected_color)
            if detected_type:
                desc_parts.append(detected_type)
            desc_str = " ".join(desc_parts) if desc_parts else ""
            return f"No {desc_str} vehicles found matching your criteria.", tools

        lines = [f"Found **{len(detections)}** matching detections:\n"]
        for d in detections[:10]:
            plate = d.plate_number or "Unknown"
            vtype = d.vehicle_type.value if d.vehicle_type else "Unknown"
            color = d.vehicle_color or "Unknown"
            conf = f"{d.plate_confidence:.0%}" if d.plate_confidence else "N/A"
            lines.append(f"- **{plate}** — {color} {vtype}, Confidence: {conf}")

        return "\n".join(lines), tools

    async def _handle_ranking_query(self, msg: str) -> tuple[str, list[dict]]:
        """Handle ranking/top queries."""
        tools = [{"tool": "get_statistics", "params": {"metric": "ranking"}}]

        if "camera" in msg:
            query = (
                select(Camera.name, func.count(DetectionEvent.id).label("cnt"))
                .join(DetectionEvent, DetectionEvent.camera_id == Camera.id)
                .group_by(Camera.name)
                .order_by(func.count(DetectionEvent.id).desc())
                .limit(5)
            )
            result = await self.db.execute(query)
            rows = result.all()
            if not rows:
                return "No camera detection data available yet.", tools
            lines = ["**Camera Rankings by Detection Count:**\n"]
            for i, r in enumerate(rows, 1):
                lines.append(f"{i}. **{r.name}** — {r.cnt:,} detections")
            return "\n".join(lines), tools

        elif "plate" in msg:
            query = (
                select(DetectionEvent.plate_number, func.count(DetectionEvent.id).label("cnt"))
                .where(DetectionEvent.plate_number.isnot(None))
                .group_by(DetectionEvent.plate_number)
                .order_by(func.count(DetectionEvent.id).desc())
                .limit(10)
            )
            result = await self.db.execute(query)
            rows = result.all()
            if not rows:
                return "No plate detection data available yet.", tools
            lines = ["**Most Frequently Detected Plates:**\n"]
            for i, r in enumerate(rows, 1):
                lines.append(f"{i}. **{r.plate_number}** — {r.cnt} detections")
            return "\n".join(lines), tools

        return "Could you be more specific about what ranking you'd like to see?", tools

    async def _handle_camera_query(self, msg: str) -> tuple[str, list[dict]]:
        """Handle camera-related queries."""
        tools = [{"tool": "get_camera_stats", "params": {}}]

        query = (
            select(Camera.name, Camera.status, Camera.location,
                   func.count(DetectionEvent.id).label("cnt"))
            .outerjoin(DetectionEvent, DetectionEvent.camera_id == Camera.id)
            .group_by(Camera.id, Camera.name, Camera.status, Camera.location)
        )
        result = await self.db.execute(query)
        rows = result.all()

        if not rows:
            return "No cameras are configured in the system.", tools

        lines = ["**Camera Overview:**\n"]
        for r in rows:
            status_icon = "🟢" if r.status and r.status.value == "online" else "🔴"
            loc = f" ({r.location})" if r.location else ""
            lines.append(f"- {status_icon} **{r.name}**{loc} — {r.cnt:,} detections")

        return "\n".join(lines), tools

    async def _handle_confidence_query(self, msg: str) -> tuple[str, list[dict]]:
        """Handle confidence-related queries."""
        tools = [{"tool": "search_detections", "params": {"min_confidence": 0, "max_confidence": 0.7}}]

        query = (
            select(DetectionEvent)
            .where(
                and_(
                    DetectionEvent.plate_confidence.isnot(None),
                    DetectionEvent.plate_confidence < 0.7,
                )
            )
            .order_by(DetectionEvent.plate_confidence.asc())
            .limit(10)
        )
        result = await self.db.execute(query)
        detections = result.scalars().all()

        if not detections:
            return "No low-confidence detections found. All OCR results are above 70% confidence.", tools

        lines = ["**Low-Confidence OCR Detections (< 70%):**\n"]
        for d in detections:
            plate = d.plate_number or "Unknown"
            conf = f"{d.plate_confidence:.0%}" if d.plate_confidence else "N/A"
            lines.append(f"- **{plate}** — Confidence: {conf}")

        return "\n".join(lines), tools

    async def _handle_plate_query(self, msg: str) -> tuple[str, list[dict]]:
        """Handle plate-specific queries."""
        tools = [{"tool": "get_plate_history", "params": {}}]

        # Try to extract plate number from message
        import re
        plate_match = re.search(r'[A-Z]{2}\d{2}[A-Z]{0,3}\d{4}', msg.upper())
        if plate_match:
            plate = plate_match.group()
            query = (
                select(DetectionEvent)
                .where(DetectionEvent.plate_number.ilike(f"%{plate}%"))
                .order_by(desc(DetectionEvent.timestamp))
                .limit(10)
            )
            result = await self.db.execute(query)
            detections = result.scalars().all()

            if not detections:
                return f"No detections found for plate **{plate}**.", tools

            lines = [f"**Detection History for {plate}:**\n"]
            for d in detections:
                ts = d.timestamp.strftime("%Y-%m-%d %H:%M") if d.timestamp else "Unknown"
                conf = f"{d.plate_confidence:.0%}" if d.plate_confidence else "N/A"
                lines.append(f"- {ts} — Confidence: {conf}")
            return "\n".join(lines), tools

        return "Please specify a plate number to look up its history.", tools

    async def _handle_general_query(self, msg: str) -> str:
        """Handle general queries with system information."""
        total_result = await self.db.execute(select(func.count(DetectionEvent.id)))
        total = total_result.scalar() or 0

        camera_result = await self.db.execute(select(func.count(Camera.id)))
        cameras = camera_result.scalar() or 0

        return (
            f"👋 I'm the **Vision Assistant**. I can help you query your ANPR data.\n\n"
            f"**System Status:**\n"
            f"- Total detections: **{total:,}**\n"
            f"- Configured cameras: **{cameras}**\n\n"
            f"Try asking me:\n"
            f"- \"How many vehicles were detected today?\"\n"
            f"- \"Show me all white SUVs\"\n"
            f"- \"Which camera had the most detections?\"\n"
            f"- \"Show low-confidence detections\"\n"
            f"- \"Find plate DL01AB1234\""
        )
