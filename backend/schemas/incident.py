from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class IncidentBase(BaseModel):
    title: str = Field(..., description="Short descriptive title of the incident")
    type: str = Field(..., description="Category (e.g., Brute-Force Attack, Phishing, Malware)")
    severity: Optional[str] = Field("AUTO", description="Severity level: AUTO, HIGH, MEDIUM, LOW")
    description: str = Field(..., description="Detailed description of what occurred")
    source_ip: Optional[str] = Field(None, description="Originating IP address")
    username: Optional[str] = Field(None, description="Associated user or service account")
    affected_system: Optional[str] = Field(None, description="System, host, or cloud resource impacted")
    additional_logs: Optional[str] = Field(None, description="Raw logs, alerts, or telemetry headers")

class IncidentCreate(IncidentBase):
    pass

from pydantic import BaseModel, Field, model_validator

class IncidentResolve(BaseModel):
    root_cause: str = Field(..., description="Identified root cause")
    actions_taken: str = Field(..., description="Mitigation steps executed")
    successful_resolution: Optional[str] = Field(None, description="Final resolution summary")
    final_resolution: Optional[str] = Field(None, description="Alias for final resolution summary")
    lessons_learned: Optional[str] = Field(None, description="Key organizational takeaways")
    analyst_feedback: Optional[str] = Field(None, description="Analyst comments & feedback")
    store_in_hindsight: bool = Field(True, description="Whether to persist to Hindsight memory bank")

    @model_validator(mode='before')
    @classmethod
    def sync_resolution_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            res = values.get("successful_resolution") or values.get("final_resolution") or "Mitigation verified and incident closed."
            values["successful_resolution"] = res
            values["final_resolution"] = res
        return values

class IncidentResponse(IncidentBase):
    id: str
    status: str = Field("OPEN", description="OPEN, INVESTIGATING, RESOLVED")
    timestamp: str
    root_cause: Optional[str] = None
    investigation_process: Optional[str] = None
    actions_taken: Optional[str] = None
    successful_resolution: Optional[str] = None
    analyst_feedback: Optional[str] = None
    lessons_learned: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    hindsight_memory_id: Optional[str] = None

class DashboardStats(BaseModel):
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    high_severity: int
    medium_severity: int
    low_severity: int
    categories: Dict[str, int]
    recent_incidents: List[IncidentResponse]
    severity_distribution: Dict[str, int]
    trend_data: Dict[str, Any]
