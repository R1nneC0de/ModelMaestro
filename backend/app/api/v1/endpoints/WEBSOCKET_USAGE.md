# WebSocket API Usage Guide

## Overview

The WebSocket API provides real-time updates for ML pipeline execution. Clients can connect to receive live progress updates, logs, decisions, and error notifications.

## Connection

### Endpoint

```
WS/WSS /api/v1/ws/projects/{project_id}/stream
```

**Security Note:** The client automatically uses WSS (secure WebSocket) when:
- The API URL uses HTTPS
- The current page is served over HTTPS
- Production mode is enabled
- `VITE_FORCE_WSS=true` environment variable is set

### Example Connection (JavaScript)

```javascript
const projectId = "proj_abc123";
// Automatically uses WSS if page is served over HTTPS or in production
const wsUrl = window.location.protocol === 'https:' 
  ? `wss://${window.location.host}/api/v1/ws/projects/${projectId}/stream`
  : `ws://localhost:8000/api/v1/ws/projects/${projectId}/stream`;
const ws = new WebSocket(wsUrl);

ws.onopen = () => {
  console.log("Connected to pipeline updates");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handlePipelineEvent(message);
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Connection closed");
  // Implement reconnection logic
  setTimeout(() => reconnect(), 5000);
};
```

### Example Connection (Python)

```python
import asyncio
import websockets
import json
import os

async def connect_to_pipeline(project_id: str, use_ssl: bool = False):
    # Use WSS for production/HTTPS, WS for local development
    protocol = "wss" if use_ssl else "ws"
    host = os.getenv("API_HOST", "localhost:8000")
    uri = f"{protocol}://{host}/api/v1/ws/projects/{project_id}/stream"
    
    # For WSS, you may need to specify SSL context
    ssl_context = None
    if use_ssl:
        import ssl
        ssl_context = ssl.create_default_context()
    
    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        print("Connected to pipeline updates")
        
        async for message in websocket:
            event = json.loads(message)
            handle_pipeline_event(event)
```

## Event Types

### 1. Connected Event

Sent immediately after connection is established.

```json
{
  "event_type": "connected",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "message": "WebSocket connection established"
}
```

### 2. Stage Transition Event

Sent when pipeline moves to a new stage.

```json
{
  "event_type": "stage_transition",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "stage": "training",
    "progress": 0.5,
    "progress_percentage": 50.0,
    "stage_display": "Model Training"
  }
}
```

### 3. Progress Update Event

Sent for progress updates within a stage.

```json
{
  "event_type": "progress_update",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "stage": "training",
    "progress": 0.65,
    "progress_percentage": 65.0,
    "stage_display": "Model Training",
    "message": "Training epoch 5/10",
    "estimated_time_remaining": 300,
    "estimated_time_display": "5m"
  }
}
```

### 4. Log Event

Sent for log messages during pipeline execution.

```json
{
  "event_type": "log",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "level": "info",
    "message": "Starting model training",
    "stage": "training",
    "stage_display": "Model Training"
  }
}
```

### 5. Decision Event

Sent when the agent makes a decision.

```json
{
  "event_type": "decision",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "stage": "model_selection",
    "stage_display": "Model Selection",
    "decision_type": "model_architecture",
    "decision": "xgboost_clf",
    "reasoning": "XGBoost selected due to tabular data with 15k rows",
    "confidence": 0.92,
    "confidence_percentage": 92.0,
    "metadata": {
      "num_rows": 15000,
      "num_features": 25
    }
  }
}
```

### 6. Approval Required Event

Sent when user approval is needed.

```json
{
  "event_type": "approval_required",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "approval_type": "model_selection",
    "message": "Model selection requires approval",
    "approval_data": {
      "architecture": "xgboost_clf",
      "hyperparameters": {...}
    }
  }
}
```

### 7. Pipeline Completed Event

Sent when pipeline completes successfully.

```json
{
  "event_type": "pipeline_completed",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "status": "completed",
    "message": "Pipeline execution completed successfully",
    "result": {
      "model_id": "model_xyz789",
      "metrics": {...}
    }
  }
}
```

### 8. Pipeline Failed Event

Sent when pipeline fails.

```json
{
  "event_type": "pipeline_failed",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "status": "failed",
    "error": "Training job failed: insufficient memory",
    "stage": "training",
    "stage_display": "Model Training",
    "message": "Pipeline failed during Model Training"
  }
}
```

### 9. Error Event

Sent for general errors.

```json
{
  "event_type": "error",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "error": "Connection error",
    "details": "Failed to connect to training service",
    "recoverable": true
  }
}
```

## Client Messages

Clients can send messages to the server for various operations.

### Ping Message

Keep connection alive and check health.

```json
{
  "type": "ping"
}
```

Response:

```json
{
  "event_type": "pong",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Cancel Pipeline

Request pipeline cancellation.

```json
{
  "type": "cancel"
}
```

Response:

```json
{
  "event_type": "cancel_acknowledged",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "message": "Cancellation request received"
  }
}
```

### Get Current State

Request current pipeline state (useful for reconnection).

```json
{
  "type": "get_state"
}
```

## Error Handling and Reconnection

### Automatic Reconnection (JavaScript)

```javascript
class PipelineWebSocket {
  constructor(projectId) {
    this.projectId = projectId;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 5000;
  }

  connect() {
    const url = `ws://localhost:8000/api/v1/projects/${this.projectId}/stream`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("Connected");
      this.reconnectAttempts = 0;
      
      // Request current state after reconnection
      this.ws.send(JSON.stringify({ type: "get_state" }));
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    this.ws.onclose = () => {
      console.log("Connection closed");
      this.reconnect();
    };
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnection attempts reached");
      return;
    }

    this.reconnectAttempts++;
    console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, this.reconnectDelay);
  }

  handleMessage(message) {
    switch (message.event_type) {
      case "stage_transition":
        this.onStageTransition(message.data);
        break;
      case "log":
        this.onLog(message.data);
        break;
      case "error":
        this.onError(message.data);
        break;
      // ... handle other event types
    }
  }

  sendPing() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "ping" }));
    }
  }

  cancelPipeline() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "cancel" }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const pipelineWs = new PipelineWebSocket("proj_abc123");
pipelineWs.connect();

// Send periodic pings
setInterval(() => pipelineWs.sendPing(), 30000);
```

### Error Recovery

When receiving an error event, check the `recoverable` flag:

```javascript
handleError(errorData) {
  if (errorData.recoverable) {
    // Temporary error, connection will recover
    console.warn("Recoverable error:", errorData.error);
  } else {
    // Fatal error, close connection
    console.error("Fatal error:", errorData.error);
    this.disconnect();
  }
}
```

## Best Practices

1. **Implement Reconnection Logic**: Always implement automatic reconnection with exponential backoff
2. **Handle All Event Types**: Ensure your client handles all possible event types
3. **Send Periodic Pings**: Send ping messages every 30-60 seconds to keep connection alive
4. **Request State on Reconnect**: After reconnecting, request current state to catch up on missed events
5. **Graceful Degradation**: If WebSocket fails, fall back to polling the REST API
6. **Connection Limits**: Be aware that there may be connection limits per project
7. **Clean Up**: Always close WebSocket connections when no longer needed

## Testing

### Test Connection

```bash
# Using websocat
websocat ws://localhost:8000/api/v1/projects/proj_abc123/stream

# Using wscat
wscat -c ws://localhost:8000/api/v1/projects/proj_abc123/stream
```

### Check Active Connections

```bash
curl http://localhost:8000/api/v1/projects/proj_abc123/connections
```

Response:

```json
{
  "project_id": "proj_abc123",
  "active_connections": 2
}
```
