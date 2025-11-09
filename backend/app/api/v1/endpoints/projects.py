"""Project management API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from app.schemas.project import (
    Project,
    ProjectCreate,
    ProjectListResponse,
    ProjectProgressResponse,
    ProjectDeleteResponse
)
from app.services.project_service import ProjectService
from app.api.v1.endpoints.websocket import get_event_broadcaster

logger = logging.getLogger(__name__)

router = APIRouter()

# Singleton project service instance
_project_service: Optional[ProjectService] = None


def get_project_service() -> ProjectService:
    """Dependency to get project service instance (singleton)."""
    global _project_service
    
    if _project_service is None:
        # Get the event broadcaster for WebSocket updates
        event_broadcaster = get_event_broadcaster()
        _project_service = ProjectService(event_broadcaster=event_broadcaster)
        logger.info("Created singleton ProjectService instance")
    
    return _project_service


@router.post("", response_model=Project, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    dataset_id: str = Query(..., description="ID of the uploaded dataset"),
    service: ProjectService = Depends(get_project_service)
):
    """
    Create a new ML training project and start the pipeline.
    
    This endpoint creates a project and initiates the agentic ML pipeline
    that will analyze the problem, process data, select models, train, and evaluate.
    
    Args:
        project_data: Project creation data including problem description
        dataset_id: ID of the previously uploaded dataset
        service: Project service dependency
        
    Returns:
        Created project with initial status
        
    Raises:
        HTTPException: If project creation fails
    """
    try:
        project = await service.create_project(project_data, dataset_id)
        logger.info(f"Created project {project.id} via API")
        return project
    except ValueError as e:
        logger.error(f"Project creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """
    Get a project by ID.
    
    Args:
        project_id: Unique project identifier
        service: Project service dependency
        
    Returns:
        Project details
        
    Raises:
        HTTPException: If project not found
    """
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    service: ProjectService = Depends(get_project_service)
):
    """
    List projects with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        user_id: Optional user ID to filter projects
        service: Project service dependency
        
    Returns:
        Paginated list of projects
    """
    try:
        return await service.list_projects(page, page_size, user_id)
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to list projects")


@router.delete("/{project_id}", response_model=ProjectDeleteResponse)
async def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """
    Delete a project.
    
    Args:
        project_id: Unique project identifier
        service: Project service dependency
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If project not found
    """
    deleted = await service.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    logger.info(f"Deleted project {project_id} via API")
    return ProjectDeleteResponse(
        message="Project deleted successfully",
        project_id=project_id
    )


@router.get("/{project_id}/progress", response_model=ProjectProgressResponse)
async def get_project_progress(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """
    Get the current progress of a project's pipeline execution.
    
    Returns real-time information about the pipeline stage, progress percentage,
    logs, and agent decisions.
    
    Args:
        project_id: Unique project identifier
        service: Project service dependency
        
    Returns:
        Current pipeline progress including stage, logs, and decisions
        
    Raises:
        HTTPException: If project not found
    """
    progress = await service.get_project_progress(project_id)
    if not progress:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return progress
