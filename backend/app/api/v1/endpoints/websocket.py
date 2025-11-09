"""
WebSocket endpoints for real-time pipeline updates.
"""

import asyncio
import logging
import json
from typing import Dict, Set
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for pipeline updates."""
    
    def __init__(self):
        # Map of project_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        
        async with self._lock:
            if project_id not in self.active_connections:
                self.active_connections[project_id] = set()
            self.active_connections[project_id].add(websocket)
        
        logger.info(f"WebSocket connected: project_id={project_id}, total={len(self.active_connections[project_id])}")
    
    async def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            if project_id in self.active_connections:
                self.active_connections[project_id].discard(websocket)
                if not self.active_connections[project_id]:
                    del self.active_connections[project_id]
        
        logger.info(f"WebSocket disconnected: project_id={project_id}")
    
    async def send_message(self, websocket: WebSocket, message: dict) -> bool:
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_json(message)
            return True
        except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK, RuntimeError):
            return False
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            return False
    
    async def broadcast(self, project_id: str, message: dict) -> int:
        """Broadcast a message to all connections for a project."""
        if project_id not in self.active_connections:
            return 0
        
        connections = list(self.active_connections[project_id])
        failed = []
        success_count = 0
        
        for conn in connections:
            if await self.send_message(conn, message):
                success_count += 1
            else:
                failed.append(conn)
        
        # Clean up failed connections
        if failed:
            async with self._lock:
                for conn in failed:
                    self.active_connections[project_id].discard(conn)
                if not self.active_connections[project_id]:
                    del self.active_connections[project_id]
        
        return success_count


# Global connection manager
manager = ConnectionManager()


@router.websocket("/projects/{project_id}/stream")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time pipeline updates.
    
    Connects to: ws://host/api/v1/ws/projects/{project_id}/stream
    """
    await manager.connect(websocket, project_id)
    
    try:
        # Send connection confirmation
        await manager.send_message(websocket, {
            "event_type": "connected",
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "WebSocket connection established"
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0
                )
                
                # Handle client messages
                try:
                    message = json.loads(data)
                    msg_type = message.get("type")
                    
                    if msg_type == "ping":
                        await manager.send_message(websocket, {
                            "event_type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    elif msg_type == "cancel":
                        logger.info(f"Pipeline cancel requested: {project_id}")
                        await manager.send_message(websocket, {
                            "event_type": "cancel_acknowledged",
                            "project_id": project_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {data[:100]}")
            
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                if not await manager.send_message(websocket, {
                    "event_type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }):
                    break
            
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        logger.error(f"WebSocket error for {project_id}: {e}")
    
    finally:
        await manager.disconnect(websocket, project_id)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager


def get_event_broadcaster():
    """Get the event broadcaster instance."""
    from app.services.event_broadcaster import EventBroadcaster
    return EventBroadcaster(manager)
