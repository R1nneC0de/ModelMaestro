"""Project service for managing ML projects."""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import uuid4

from app.schemas.project import (
    Project,
    ProjectCreate,
    ProjectStatus,
    ProjectListResponse,
    ProjectProgressResponse
)
from app.services.cloud.storage_manager import StorageManager
from app.services.agent.orchestrator import AgentOrchestrator
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing ML training projects."""
    
    def __init__(self, bucket_name: Optional[str] = None, event_broadcaster=None):
        """
        Initialize the project service.
        
        Args:
            bucket_name: GCS bucket name for storage
            event_broadcaster: Optional EventBroadcaster for WebSocket updates
        """
        self.bucket_name = bucket_name or settings.GCS_BUCKET_NAME
        self.storage = StorageManager("projects", Project, self.bucket_name)
        self.orchestrator = AgentOrchestrator(storage_bucket=self.bucket_name)
        self.event_broadcaster = event_broadcaster
        logger.info(f"Initialized ProjectService with bucket {self.bucket_name}")
    
    async def create_project(
        self,
        project_data: ProjectCreate,
        dataset_id: str
    ) -> Project:
        """
        Create a new project and start the pipeline.
        
        Args:
            project_data: Project creation data
            dataset_id: ID of the uploaded dataset
            
        Returns:
            Created project
        """
        # Generate project ID
        project_id = f"proj_{uuid4().hex[:12]}"
        
        # Create project entity
        project = Project(
            id=project_id,
            user_id=project_data.user_id,
            problem_description=project_data.problem_description,
            requires_approval=project_data.requires_approval,
            status=ProjectStatus.ANALYZING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            dataset_id=dataset_id
        )
        
        # Save to storage
        await self.storage.create(project, project_id)
        
        logger.info(f"Created project {project_id} for user {project_data.user_id}")
        
        # Start pipeline in background (non-blocking)
        asyncio.create_task(self._start_pipeline(project_id, dataset_id, project_data))
        
        return project
    
    async def _start_pipeline(
        self,
        project_id: str,
        dataset_id: str,
        project_data: ProjectCreate
    ):
        """
        Start the ML pipeline for a project (runs in background).
        
        Args:
            project_id: Project ID
            dataset_id: Dataset ID
            project_data: Project creation data
        """
        try:
            logger.info(f"Starting pipeline for project {project_id}")
            
            # Register WebSocket event callback if broadcaster is available
            if self.event_broadcaster:
                callback = self.event_broadcaster.create_orchestrator_callback(project_id)
                self.orchestrator.register_event_callback(project_id, callback)
                logger.info(f"Registered WebSocket callback for project {project_id}")
            
            # Task 1.1: Load dataset from GCS
            dataset, data_df = await self._load_dataset(dataset_id)
            
            if dataset is None or data_df is None:
                raise ValueError(f"Failed to load dataset {dataset_id}")
            
            logger.info(
                f"Loaded dataset {dataset_id}: "
                f"{len(data_df)} rows, {len(data_df.columns)} columns"
            )
            
            # Update project status to ANALYZING
            await self.storage.update(
                project_id,
                {"status": ProjectStatus.ANALYZING, "updated_at": datetime.utcnow()}
            )
            
            # Task 1.2: Call orchestrator.execute_pipeline
            # Prepare data sample for analysis (first 100 rows)
            data_sample = data_df.head(100).to_dict(orient='records')
            
            # Execute the pipeline
            result = await self.orchestrator.execute_pipeline(
                project_id=project_id,
                problem_description=project_data.problem_description,
                dataset_id=dataset_id,
                data=data_df,
                data_sample=data_sample,
                num_samples=len(data_df),
                is_labeled=dataset.is_labeled,
                target_column=None,  # Will be detected by analyzer
                data_type_hint=dataset.data_type.value if dataset.data_type else None,
                file_extensions=None,
                requires_approval=project_data.requires_approval
            )
            
            # Task 1.3: Update project status on completion
            logger.info(f"Pipeline completed for project {project_id}")
            
            # Extract model_id from training output if available
            model_id = None
            if result.get("training_output"):
                training_output = result["training_output"]
                if hasattr(training_output, 'model_uri'):
                    # Extract model ID from URI
                    model_id = training_output.model_uri.split('/')[-1] if training_output.model_uri else None
                elif hasattr(training_output, 'job_id'):
                    model_id = training_output.job_id
            
            # Update project with completion status
            update_data = {
                "status": ProjectStatus.COMPLETE,
                "updated_at": datetime.utcnow()
            }
            if model_id:
                update_data["model_id"] = model_id
            
            await self.storage.update(project_id, update_data)
            
            logger.info(
                f"Project {project_id} completed successfully. "
                f"Model ID: {model_id}"
            )
            
        except Exception as e:
            # Task 1.3: Set status to FAILED on errors
            logger.error(f"Pipeline failed for project {project_id}: {e}", exc_info=True)
            await self.storage.update(
                project_id,
                {
                    "status": ProjectStatus.FAILED,
                    "updated_at": datetime.utcnow()
                }
            )
            
            # Send error to WebSocket if broadcaster is available
            if self.event_broadcaster:
                try:
                    await self.event_broadcaster.send_error_to_project(
                        project_id=project_id,
                        error="Pipeline execution failed",
                        details=str(e),
                        recoverable=False
                    )
                except Exception as broadcast_error:
                    logger.error(f"Failed to broadcast error: {broadcast_error}")
        
        finally:
            # Unregister callback when pipeline completes or fails
            if self.event_broadcaster:
                try:
                    callback = self.event_broadcaster.create_orchestrator_callback(project_id)
                    self.orchestrator.unregister_event_callback(project_id, callback)
                    logger.info(f"Unregistered WebSocket callback for project {project_id}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to unregister callback: {cleanup_error}")
    
    async def _load_dataset(self, dataset_id: str):
        """
        Load dataset from GCS and convert to pandas DataFrame.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Tuple of (Dataset, DataFrame) or (None, None) if failed
        """
        import tempfile
        import os
        import pandas as pd
        from app.services.dataset_service import DatasetService
        from app.services.cloud.storage import download_file_from_gcs
        
        try:
            # Get dataset metadata
            dataset = await DatasetService.get_dataset(dataset_id)
            if not dataset:
                logger.error(f"Dataset {dataset_id} not found")
                return None, None
            
            # Get first file path (for now, assume single file datasets)
            if not dataset.file_paths:
                logger.error(f"Dataset {dataset_id} has no file paths")
                return None, None
            
            first_file_gcs = dataset.file_paths[0]
            blob_name = first_file_gcs.replace(f"gs://{self.bucket_name}/", "")
            
            # Download file to temp location
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, os.path.basename(blob_name))
            
            logger.info(f"Downloading dataset from {blob_name}")
            await download_file_from_gcs(blob_name, temp_file_path)
            
            # Parse based on file extension
            file_ext = os.path.splitext(temp_file_path)[1].lower()
            
            if file_ext == '.csv':
                data_df = pd.read_csv(temp_file_path)
            elif file_ext == '.json':
                data_df = pd.read_json(temp_file_path)
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return None, None
            
            # Clean up temp file
            try:
                os.remove(temp_file_path)
                os.rmdir(temp_dir)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temp files: {cleanup_error}")
            
            # Validate data format
            if data_df.empty:
                logger.error(f"Dataset {dataset_id} is empty")
                return None, None
            
            logger.info(
                f"Successfully loaded dataset {dataset_id}: "
                f"shape={data_df.shape}, columns={list(data_df.columns)}"
            )
            
            return dataset, data_df
            
        except Exception as e:
            logger.error(f"Failed to load dataset {dataset_id}: {e}", exc_info=True)
            return None, None
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project if found, None otherwise
        """
        return await self.storage.get(project_id)
    
    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 10,
        user_id: Optional[str] = None
    ) -> ProjectListResponse:
        """
        List projects with pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            user_id: Optional user ID to filter by
            
        Returns:
            Paginated list of projects
        """
        # Get all projects
        all_projects = await self.storage.list()
        
        # Filter by user if specified
        if user_id:
            all_projects = [p for p in all_projects if p.user_id == user_id]
        
        # Sort by created_at descending (newest first)
        all_projects.sort(key=lambda p: p.created_at, reverse=True)
        
        # Paginate
        total = len(all_projects)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        projects = all_projects[start_idx:end_idx]
        
        return ProjectListResponse(
            projects=projects,
            total=total,
            page=page,
            page_size=page_size
        )
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        return await self.storage.delete(project_id)
    
    async def get_project_progress(self, project_id: str) -> Optional[ProjectProgressResponse]:
        """
        Get the current progress of a project's pipeline execution.
        
        Args:
            project_id: Project ID
            
        Returns:
            Progress information if project exists and has state, None otherwise
        """
        # Check if project exists
        project = await self.get_project(project_id)
        if not project:
            return None
        
        # Get pipeline state from orchestrator
        state = self.orchestrator.states.get(project_id)
        
        if state:
            # Return live progress from orchestrator
            return ProjectProgressResponse(
                project_id=project_id,
                stage=state.stage,
                progress=state.progress,
                logs=state.logs,
                decisions=state.decisions,
                error=state.error
            )
        else:
            # No active pipeline state - return project status
            return ProjectProgressResponse(
                project_id=project_id,
                stage=project.status.value,
                progress=1.0 if project.status == ProjectStatus.COMPLETE else 0.0,
                logs=[],
                decisions=[],
                error=None
            )
