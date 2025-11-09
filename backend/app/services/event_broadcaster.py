"""
Event broadcaster for WebSocket updates.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class EventBroadcaster:
    """Broadcasts pipeline events to WebSocket clients."""
    
    def __init__(self, connection_manager):
        self.manager = connection_manager
    
    async def broadcast_event(
        self,
        project_id: str,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Broadcast an event to all connections for a project."""
        message = {
            "event_type": event_type,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        if metadata:
            message["metadata"] = metadata
        
        count = await self.manager.broadcast(project_id, message)
        logger.debug(f"Broadcasted {event_type} to {count} clients for project {project_id}")
    
    async def stage_transition(self, project_id: str, stage: str, progress: float, message: str = ""):
        """Broadcast a stage transition event."""
        await self.broadcast_event(project_id, "stage_transition", {
            "stage": stage,
            "progress": progress,
            "progress_percentage": int(progress * 100),
            "stage_display": stage.replace("_", " ").title(),
            "message": message
        })
    
    async def progress_update(self, project_id: str, stage: str, progress: float, message: str = ""):
        """Broadcast a progress update event."""
        await self.broadcast_event(project_id, "progress_update", {
            "stage": stage,
            "progress": progress,
            "progress_percentage": int(progress * 100),
            "stage_display": stage.replace("_", " ").title(),
            "message": message
        })
    
    async def log_message(self, project_id: str, level: str, message: str, stage: str = ""):
        """Broadcast a log message."""
        await self.broadcast_event(project_id, "log", {
            "level": level,
            "message": message,
            "stage": stage,
            "stage_display": stage.replace("_", " ").title() if stage else ""
        })
    
    async def decision_log(
        self,
        project_id: str,
        stage: str,
        decision_type: str,
        decision: str,
        reasoning: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Broadcast a decision log."""
        await self.broadcast_event(project_id, "decision", {
            "stage": stage,
            "stage_display": stage.replace("_", " ").title(),
            "decision_type": decision_type,
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "confidence_percentage": int(confidence * 100),
            "metadata": metadata or {}
        })
    
    async def pipeline_completed(self, project_id: str, result: Dict[str, Any]):
        """Broadcast pipeline completion."""
        await self.broadcast_event(project_id, "pipeline_completed", {
            "result": result
        })
    
    async def pipeline_failed(self, project_id: str, error: str, stage: str):
        """Broadcast pipeline failure."""
        await self.broadcast_event(project_id, "pipeline_failed", {
            "error": error,
            "stage": stage
        })
    
    async def error_event(self, project_id: str, error: str, details: str = "", recoverable: bool = True):
        """Broadcast an error event."""
        await self.broadcast_event(project_id, "error", {
            "error": error,
            "details": details,
            "recoverable": recoverable
        })
