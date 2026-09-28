from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel
from backend.schemas.incident import IncidentCreate, IncidentResolve, IncidentResponse
from backend.services.incident_service import incident_service
from backend.services.ai_service import ai_service
from backend.services.hindsight_service import hindsight_service

router = APIRouter(prefix="/api", tags=["Incidents & Memory"])

class MemorySearchRequest(BaseModel):
    query: str
    incident_type: Optional[str] = None
    limit: Optional[int] = 5

class MemoryStoreRequest(BaseModel):
    incident_id: str
    incident_type: str
    title: str
    description: str
    root_cause: str
    investigation_process: str
    actions_taken: str
    successful_resolution: str
    lessons_learned: Optional[str] = ""
    analyst_feedback: Optional[str] = ""

@router.get("/incidents", response_model=List[IncidentResponse])
async def get_all_incidents(
    status: Optional[str] = Query(None, description="Filter by status: OPEN, INVESTIGATING, RESOLVED"),
    severity: Optional[str] = Query(None, description="Filter by severity: HIGH, MEDIUM, LOW")
):
    """Retrieve all logged incidents with optional filtering"""
    return incident_service.get_all(status=status, severity=severity)

@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str = Path(..., description="Unique Incident ID (e.g. INC-2026-0812)")
):
    """Get single incident details by ID"""
    incident = incident_service.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    return incident

@router.post("/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(data: IncidentCreate):
    """Create and log a new incoming security incident"""
    return incident_service.create(data)

@router.post("/incidents/{incident_id}/analyze")
async def analyze_incident_endpoint(
    incident_id: str,
    use_hindsight: bool = Query(True, description="Whether to query Hindsight memory for similar historical incidents")
):
    """
    Analyzes an incident using AI and Hindsight Persistent Memory.
    Returns: AI classification, root cause, investigation steps, similar memories, and memory-aware response recommendations.
    """
    incident = incident_service.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")

    # 1. Query Hindsight for similar historical incidents
    similar_memories = []
    if use_hindsight:
        query_text = f"{incident.title} {incident.type} {incident.description} {incident.additional_logs or ''}"
        similar_memories = await hindsight_service.search_memories(
            query=query_text,
            incident_type=incident.type,
            limit=3
        )

    # 2. Perform AI Investigation synthesized with historical memories
    ai_result = await ai_service.analyze_incident(
        incident_data=incident.model_dump(),
        historical_memories=similar_memories
    )

    # Attach similar memories to AI result payload
    ai_result["similar_historical_incidents"] = similar_memories
    ai_result["memory_augmented"] = len(similar_memories) > 0

    # 3. Update Incident record with analysis
    updated_inc = incident_service.update_analysis(incident_id, ai_result)
    return {
        "incident": updated_inc,
        "analysis": ai_result,
        "similar_incidents": similar_memories
    }

@router.get("/incidents/{incident_id}/similar")
async def get_similar_incidents_endpoint(incident_id: str):
    """Retrieve similar historical incidents from Hindsight memory bank"""
    incident = incident_service.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    
    query_text = f"{incident.title} {incident.type} {incident.description}"
    memories = await hindsight_service.search_memories(
        query=query_text,
        incident_type=incident.type,
        limit=4
    )
    return {"incident_id": incident_id, "similar_memories": memories}

@router.post("/incidents/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident_endpoint(
    incident_id: str,
    resolve_data: IncidentResolve
):
    """
    Mark an incident as resolved, record root cause, and persist lessons learned into Hindsight memory.
    """
    incident = incident_service.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")

    memory_id = None
    if resolve_data.store_in_hindsight:
        mem_result = await hindsight_service.store_memory(
            incident_id=incident_id,
            incident_type=incident.type,
            title=incident.title,
            description=incident.description,
            root_cause=resolve_data.root_cause,
            investigation_process=incident.investigation_process or "Triage conducted with Incident Response Agent AI",
            actions_taken=resolve_data.actions_taken,
            successful_resolution=resolve_data.successful_resolution,
            lessons_learned=resolve_data.lessons_learned,
            analyst_feedback=resolve_data.analyst_feedback
        )
        memory_id = mem_result.get("memory_id")

    updated = incident_service.resolve(incident_id, resolve_data, memory_id=memory_id)
    return updated

@router.post("/memory/search")
async def search_memory_endpoint(req: MemorySearchRequest):
    """Direct search endpoint for Hindsight Organizational Security Memory with AI answer synthesis"""
    results = await hindsight_service.search_memories(
        query=req.query,
        incident_type=req.incident_type,
        limit=req.limit or 5
    )
    answer = await ai_service.synthesize_memory_answer(req.query, results)
    return {
        "query": req.query,
        "answer": answer,
        "results": results,
        "count": len(results)
    }

@router.post("/memory/store")
async def store_memory_endpoint(req: MemoryStoreRequest):
    """Direct endpoint to manually persist security knowledge into Hindsight bank"""
    result = await hindsight_service.store_memory(
        incident_id=req.incident_id,
        incident_type=req.incident_type,
        title=req.title,
        description=req.description,
        root_cause=req.root_cause,
        investigation_process=req.investigation_process,
        actions_taken=req.actions_taken,
        successful_resolution=req.successful_resolution,
        lessons_learned=req.lessons_learned,
        analyst_feedback=req.analyst_feedback
    )
    return result

@router.post("/sync/supabase")
async def sync_supabase_endpoint():
    """Sync all local incidents to Supabase cloud table editor"""
    from backend.services.supabase_service import supabase_service
    from backend.database import db_get_all
    incidents = db_get_all()
    result = await supabase_service.sync_all_incidents(incidents)
    return result

