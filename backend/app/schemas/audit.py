"""Audit entry schema definitions."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AuditEntryBase(BaseModel):
    """Base audit entry schema with common fields."""
    stage: str = Field(..., min_length=1)
    decision_type: str = Field(..., min_length=1)
    decision: str = Field(..., min_length=1)
    reasoning: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)


class AuditEntryCreate(AuditEntryBase):
    """Schema for creating a new audit entry."""
    project_id: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AuditEntry(AuditEntryBase):
    """Complete audit entry schema."""
    id: str
    project_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "audit_abc123",
                "project_id": "proj_xyz789",
                "timestamp": "2024-01-01T00:00:00Z",
                "stage": "analyzing",
                "decision_type": "problem_classification",
                "decision": "tabular_classification",
                "reasoning": "Based on the CSV structure with categorical target column",
                "confidence": 0.95,
                "metadata": {
                    "num_features": 10,
                    "num_classes": 3
                }
            }
        }
    }
