"""
Agent Orchestrator for ML pipeline execution.

This module orchestrates the complete ML pipeline from problem analysis
to model deployment, integrating all agent components and managing state.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from uuid import uuid4
import structlog

from app.services.agent.analyzer import ProblemAnalyzer
from app.services.agent.data_processor import DataProcessor
from app.services.agent.model_selector import ModelSelector
from app.services.agent.training_manager import TrainingManager
from app.services.agent.evaluator import ModelEvaluator
from app.services.agent.gemini_client import GeminiClient
from app.services.cloud.vertex_client import VertexAIClient
from app.services.cloud.storage_manager import StorageManager
from app.services.agent.types import ProblemAnalysis, DataType
from app.services.agent.model_types import DatasetProfile
from app.schemas.project import Project, ProjectStatus
from app.schemas.audit import AuditEntry, AuditEntryCreate
from app.core.config import settings

logger = structlog.get_logger()


class PipelineStage(str):
    """Pipeline execution stages."""
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    LABELING = "labeling"
    MODEL_SELECTION = "model_selection"
    TRAINING = "training"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineState:
    """
    Pipeline execution state.
    
    Tracks the current state of pipeline execution including stage,
    progress, logs, and intermediate results.
    """
    
    def __init__(self, project_id: str):
        """
        Initialize pipeline state.
        
        Args:
            project_id: Unique project identifier
        """
        self.project_id = project_id
        self.stage = PipelineStage.ANALYZING
        self.progress = 0.0
        self.logs: List[Dict[str, Any]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.error: Optional[str] = None
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Intermediate results
        self.problem_analysis: Optional[ProblemAnalysis] = None
        self.dataset_profile: Optional[DatasetProfile] = None
        self.processing_result: Optional[Dict[str, Any]] = None
        self.model_config: Optional[Any] = None
        self.training_output: Optional[Any] = None
        self.evaluation_result: Optional[Any] = None
        self.deployment_result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "project_id": self.project_id,
            "stage": self.stage,
            "progress": self.progress,
            "logs": self.logs,
            "decisions": self.decisions,
            "error": self.error,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AgentOrchestrator:
    """
    Main orchestrator for the ML pipeline.
    
    Coordinates all agent components and manages the complete pipeline
    execution from problem analysis to model deployment.
    """
    
    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        vertex_client: Optional[VertexAIClient] = None,
        storage_bucket: Optional[str] = None
    ):
        """
        Initialize the orchestrator.
        
        Args:
            gemini_client: Gemini client for AI-powered analysis
            vertex_client: Vertex AI client for training
            storage_bucket: GCS bucket for storage
        """
        self.gemini_client = gemini_client or GeminiClient()
        self.vertex_client = vertex_client or VertexAIClient()
        self.storage_bucket = storage_bucket or settings.GCS_BUCKET_NAME
        
        # Initialize agent components
        self.analyzer = ProblemAnalyzer(self.gemini_client)
        self.data_processor = DataProcessor(self.storage_bucket)
        self.model_selector = ModelSelector(self.gemini_client)
        self.training_manager = TrainingManager(self.vertex_client, self.storage_bucket)
        self.evaluator = ModelEvaluator()
        
        # Initialize storage managers
        self.project_storage = StorageManager("projects", Project, self.storage_bucket)
        self.audit_storage = StorageManager("audit", AuditEntry, self.storage_bucket)
        
        # Pipeline state tracking
        self.states: Dict[str, PipelineState] = {}
        
        # Event callbacks for progress updates
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        logger.info("agent_orchestrator_initialized", bucket=self.storage_bucket)
    
    async def execute_pipeline(
        self,
        project_id: str,
        problem_description: str,
        dataset_id: str,
        data: Any,
        data_sample: Any,
        num_samples: int,
        is_labeled: bool,
        target_column: Optional[str] = None,
        data_type_hint: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
        requires_approval: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the complete ML pipeline.
        
        Args:
            project_id: Unique project identifier
            problem_description: User's problem description
            dataset_id: Dataset identifier
            data: Complete dataset
            data_sample: Sample of data for analysis
            num_samples: Total number of samples
            is_labeled: Whether data has labels
            target_column: Target column name
            data_type_hint: Optional data type hint
            file_extensions: File extensions in dataset
            requires_approval: Whether to require user approval
            
        Returns:
            Dictionary with pipeline results
        """
        # Initialize pipeline state
        state = PipelineState(project_id)
        self.states[project_id] = state
        
        logger.info(
            "pipeline_execution_started",
            project_id=project_id,
            dataset_id=dataset_id
        )
        
        try:
            # Stage 1: Problem Analysis
            await self._transition_stage(state, PipelineStage.ANALYZING, 0.0)
            problem_analysis = await self._execute_analysis(
                state, problem_description, data_sample, num_samples,
                is_labeled, data_type_hint, file_extensions
            )
            
            # Stage 2: Data Processing
            await self._transition_stage(state, PipelineStage.PROCESSING, 0.2)
            processing_result = await self._execute_processing(
                state, dataset_id, data, problem_analysis, target_column
            )
            
            # Stage 3: Model Selection
            await self._transition_stage(state, PipelineStage.MODEL_SELECTION, 0.4)
            model_config = await self._execute_model_selection(
                state, problem_analysis, processing_result, data
            )
            
            # Check for approval if required
            if requires_approval:
                await self._request_approval(
                    state, "model_selection", model_config,
                    "Model selection requires approval"
                )
            
            # Stage 4: Training
            await self._transition_stage(state, PipelineStage.TRAINING, 0.5)
            # Use target_variable from problem_analysis if target_column not provided
            actual_target_column = target_column or problem_analysis.target_variable
            training_output = await self._execute_training(
                state, model_config, dataset_id, processing_result,
                actual_target_column, problem_analysis
            )
            
            # Stage 5: Evaluation
            await self._transition_stage(state, PipelineStage.EVALUATION, 0.8)
            evaluation_result = await self._execute_evaluation(
                state, training_output, processing_result, problem_analysis
            )
            
            # Stage 6: Deployment (optional)
            if evaluation_result.decision.value == "ACCEPT":
                await self._transition_stage(state, PipelineStage.DEPLOYMENT, 0.9)
                deployment_result = await self._execute_deployment(
                    state, training_output
                )
            else:
                deployment_result = None
            
            # Complete
            await self._transition_stage(state, PipelineStage.COMPLETED, 1.0)
            
            result = {
                "project_id": project_id,
                "status": "completed",
                "problem_analysis": problem_analysis,
                "model_config": model_config,
                "training_output": training_output,
                "evaluation_result": evaluation_result,
                "deployment_result": deployment_result
            }
            
            logger.info("pipeline_execution_completed", project_id=project_id)
            return result
            
        except Exception as e:
            logger.error(
                "pipeline_execution_failed",
                project_id=project_id,
                error=str(e),
                exc_info=True
            )
            await self._handle_pipeline_error(state, e)
            raise
    
    async def _execute_analysis(
        self,
        state: PipelineState,
        problem_description: str,
        data_sample: Any,
        num_samples: int,
        is_labeled: bool,
        data_type_hint: Optional[str],
        file_extensions: Optional[List[str]]
    ) -> ProblemAnalysis:
        """Execute problem analysis stage."""
        await self._emit_log(state, "info", "Starting problem analysis")
        
        analysis = await self.analyzer.analyze_problem(
            problem_description=problem_description,
            data_sample=data_sample,
            num_samples=num_samples,
            is_labeled=is_labeled,
            data_type_hint=data_type_hint,
            file_extensions=file_extensions
        )
        
        state.problem_analysis = analysis
        
        # Log decision
        await self._log_decision(
            state,
            stage="analyzing",
            decision_type="problem_classification",
            decision=f"{analysis.problem_type.value}/{analysis.data_type.value}",
            reasoning=analysis.reasoning,
            confidence=analysis.confidence,
            metadata={
                "domain": analysis.domain,
                "complexity_score": analysis.complexity_score,
                "suggested_metrics": analysis.suggested_metrics
            }
        )
        
        await self._emit_log(
            state, "info",
            f"Analysis complete: {analysis.problem_type.value} / {analysis.data_type.value}"
        )
        
        return analysis
    
    async def _execute_processing(
        self,
        state: PipelineState,
        dataset_id: str,
        data: Any,
        analysis: ProblemAnalysis,
        target_column: Optional[str]
    ) -> Dict[str, Any]:
        """Execute data processing stage."""
        await self._emit_log(state, "info", "Starting data processing")
        
        result = await self.data_processor.process_and_store(
            dataset_id=dataset_id,
            data=data,
            analysis=analysis,
            target_column=target_column
        )
        
        state.processing_result = result
        
        # Log decision
        await self._log_decision(
            state,
            stage="processing",
            decision_type="data_processing",
            decision=result["processing_strategy"].missing_value_strategy.value,
            reasoning=result["processing_strategy"].reasoning,
            confidence=0.9,
            metadata={
                "split_info": result["split_info"],
                "feature_info": result["feature_info"]
            }
        )
        
        await self._emit_log(state, "info", "Data processing complete")
        
        return result
    
    async def _execute_model_selection(
        self,
        state: PipelineState,
        analysis: ProblemAnalysis,
        processing_result: Dict[str, Any],
        data: Any
    ) -> Any:
        """Execute model selection stage."""
        await self._emit_log(state, "info", "Starting model selection")
        
        # Create dataset profile
        dataset_profile = self._create_dataset_profile(processing_result, data)
        state.dataset_profile = dataset_profile
        
        # Select model
        recommendation = await self.model_selector.select_model(
            problem_analysis=analysis,
            dataset_profile=dataset_profile,
            use_ai=True
        )
        
        state.model_config = recommendation
        
        # Log decision
        await self._log_decision(
            state,
            stage="model_selection",
            decision_type="model_architecture",
            decision=recommendation.architecture.value,
            reasoning=recommendation.reasoning,
            confidence=recommendation.confidence,
            metadata={
                "training_strategy": recommendation.training_strategy.value,
                "vertex_product": recommendation.vertex_product.value,
                "estimated_time_minutes": recommendation.estimated_training_time_minutes,
                "estimated_cost_usd": recommendation.estimated_cost_usd
            }
        )
        
        await self._emit_log(
            state, "info",
            f"Model selected: {recommendation.architecture.value}"
        )
        
        return recommendation
    
    async def _execute_training(
        self,
        state: PipelineState,
        model_config: Any,
        dataset_id: str,
        processing_result: Dict[str, Any],
        target_column: str,
        analysis: ProblemAnalysis
    ) -> Any:
        """Execute training stage."""
        await self._emit_log(state, "info", "Starting model training")
        
        # Convert model recommendation to training config
        from app.services.agent.training_config import ModelConfig as TrainingConfig
        from app.services.agent.training_config import SplitConfig
        
        training_config = TrainingConfig(
            architecture=model_config.architecture.value,
            vertex_ai_type=model_config.training_strategy.value,
            hyperparameters=model_config.hyperparameters.model_specific,
            split_config=SplitConfig(
                train_ratio=0.8,
                val_ratio=0.1,
                test_ratio=0.1,
                random_seed=42,
                stratify=True
            ),
            acceptance_thresholds=self._get_default_thresholds(analysis),
            primary_metric=self._get_primary_metric(analysis)
        )
        
        # Train model
        training_output = await self.training_manager.train_model(
            config=training_config,
            dataset_id=dataset_id,
            training_data_uri=processing_result["gcs_paths"]["train"],
            validation_data_uri=processing_result["gcs_paths"]["val"],
            test_data_uri=processing_result["gcs_paths"]["test"],
            target_column=target_column,
            problem_analysis=analysis,
            preprocessing_metadata=processing_result["metadata"]
        )
        
        state.training_output = training_output
        
        # Log decision
        await self._log_decision(
            state,
            stage="training",
            decision_type="training_completion",
            decision=training_output.state,
            reasoning=f"Training completed with state: {training_output.state}",
            confidence=0.95,
            metadata={
                "job_id": training_output.job_id,
                "duration_seconds": training_output.training_duration_seconds,
                "metrics": training_output.metrics if hasattr(training_output, 'metrics') else {}
            }
        )
        
        await self._emit_log(state, "info", f"Training complete: {training_output.state}")
        
        return training_output
    
    async def _execute_evaluation(
        self,
        state: PipelineState,
        training_output: Any,
        processing_result: Dict[str, Any],
        analysis: ProblemAnalysis
    ) -> Any:
        """Execute evaluation stage."""
        await self._emit_log(state, "info", "Starting model evaluation")
        
        # For now, create a simple evaluation based on training metrics
        # In production, this would load test data and run predictions
        from app.services.agent.evaluation_decision import EvaluationDecision
        from app.services.agent.evaluator import EvaluationResult
        
        # Simplified evaluation - in production would use actual test data
        if hasattr(training_output, 'metrics') and training_output.metrics:
            primary_value = training_output.metrics.get(
                training_output.strategy_config.primary_metric, 0.0
            )
            threshold = training_output.strategy_config.acceptance_thresholds.get(
                training_output.strategy_config.primary_metric, 0.7
            )
            
            decision = EvaluationDecision.ACCEPT if primary_value >= threshold else EvaluationDecision.REJECT
            
            evaluation_result = EvaluationResult(
                decision=decision,
                primary_metric_value=primary_value,
                primary_metric_name=training_output.strategy_config.primary_metric,
                all_metrics=training_output.metrics,
                baseline_metrics={},
                threshold_checks={training_output.strategy_config.primary_metric: primary_value >= threshold},
                sanity_checks={},
                reasoning=f"Model {'meets' if decision == EvaluationDecision.ACCEPT else 'does not meet'} acceptance threshold",
                recommendations=[],
                confidence=0.9
            )
        else:
            # No metrics available - reject
            evaluation_result = EvaluationResult(
                decision=EvaluationDecision.REJECT,
                primary_metric_value=0.0,
                primary_metric_name="unknown",
                all_metrics={},
                baseline_metrics={},
                threshold_checks={},
                sanity_checks={},
                reasoning="No metrics available from training",
                recommendations=["Retry training with valid configuration"],
                confidence=0.5
            )
        
        state.evaluation_result = evaluation_result
        
        # Log decision
        await self._log_decision(
            state,
            stage="evaluation",
            decision_type="acceptance_decision",
            decision=evaluation_result.decision.value,
            reasoning=evaluation_result.reasoning,
            confidence=evaluation_result.confidence,
            metadata={
                "primary_metric": evaluation_result.primary_metric_name,
                "primary_value": evaluation_result.primary_metric_value,
                "all_metrics": evaluation_result.all_metrics
            }
        )
        
        await self._emit_log(
            state, "info",
            f"Evaluation complete: {evaluation_result.decision.value}"
        )
        
        return evaluation_result
    
    async def _execute_deployment(
        self,
        state: PipelineState,
        training_output: Any
    ) -> Dict[str, Any]:
        """Execute deployment stage."""
        await self._emit_log(state, "info", "Starting model deployment")
        
        # Extract Vertex AI model resource name
        model_resource_name = None
        if hasattr(training_output, 'model_resource_name'):
            model_resource_name = training_output.model_resource_name
        elif hasattr(training_output, 'model_uri'):
            # Try to extract from model_uri
            model_resource_name = training_output.model_uri
        
        deployment_result = {
            "status": "deployed",
            "model_uri": training_output.model_uri if hasattr(training_output, 'model_uri') else None,
            "model_resource_name": model_resource_name,
            "endpoint_url": None,  # Would be actual endpoint in production
            "deployed_at": datetime.utcnow().isoformat()
        }
        
        state.deployment_result = deployment_result
        
        # Log decision
        await self._log_decision(
            state,
            stage="deployment",
            decision_type="deployment_completion",
            decision="deployed",
            reasoning="Model artifacts prepared for deployment",
            confidence=0.95,
            metadata=deployment_result
        )
        
        await self._emit_log(state, "info", "Deployment complete")
        
        return deployment_result
    
    def _create_dataset_profile(
        self,
        processing_result: Dict[str, Any],
        data: Any
    ) -> DatasetProfile:
        """Create dataset profile from processing results."""
        import pandas as pd
        
        # Convert data to DataFrame if needed
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            df = pd.DataFrame(data)
        
        split_info = processing_result["split_info"]
        feature_info = processing_result["feature_info"]
        
        # Calculate total samples from split sizes
        total_samples = split_info["train_size"] + split_info["val_size"] + split_info["test_size"]
        num_features = feature_info.get("n_features", len(df.columns))
        
        return DatasetProfile(
            num_samples=total_samples,
            num_features=num_features,
            num_classes=feature_info.get("num_classes"),
            num_numeric_features=len(feature_info.get("numeric_features", [])),
            num_categorical_features=len(feature_info.get("categorical_features", [])),
            missing_value_ratio=0.0,  # Already processed
            class_imbalance_ratio=feature_info.get("class_imbalance_ratio", 1.0),
            dimensionality_ratio=num_features / total_samples if total_samples > 0 else 0.0,
            dataset_size_mb=df.memory_usage(deep=True).sum() / (1024 * 1024)
        )
    
    def _get_default_thresholds(self, analysis: ProblemAnalysis) -> Dict[str, float]:
        """Get default acceptance thresholds based on problem type."""
        from app.services.agent.types import ProblemType
        
        if analysis.problem_type in [ProblemType.CLASSIFICATION, ProblemType.TEXT_CLASSIFICATION]:
            return {
                "roc_auc": 0.70,
                "f1": 0.60,
                "precision": 0.50,
                "recall": 0.50
            }
        elif analysis.problem_type == ProblemType.REGRESSION:
            return {
                "rmse": 0.9,  # Will be multiplied by baseline
                "r2": 0.1,
                "mae": 0.9
            }
        else:
            return {"accuracy": 0.70}
    
    def _get_primary_metric(self, analysis: ProblemAnalysis) -> str:
        """Get primary metric based on problem type."""
        from app.services.agent.types import ProblemType
        
        if analysis.problem_type in [ProblemType.CLASSIFICATION, ProblemType.TEXT_CLASSIFICATION]:
            return "roc_auc"
        elif analysis.problem_type == ProblemType.REGRESSION:
            return "rmse"
        else:
            return "accuracy"
    
    async def _transition_stage(
        self,
        state: PipelineState,
        new_stage: str,
        progress: float
    ) -> None:
        """Transition to a new pipeline stage."""
        state.stage = new_stage
        state.progress = progress
        state.updated_at = datetime.utcnow()
        
        # Emit stage transition event
        await self._emit_event(state, "stage_transition", {
            "stage": new_stage,
            "progress": progress
        })
        
        # Store state to GCS
        await self._store_state(state)
    
    async def _emit_log(
        self,
        state: PipelineState,
        level: str,
        message: str
    ) -> None:
        """Emit a log message."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        }
        state.logs.append(log_entry)
        
        # Emit log event
        await self._emit_event(state, "log", log_entry)
    
    async def _log_decision(
        self,
        state: PipelineState,
        stage: str,
        decision_type: str,
        decision: str,
        reasoning: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a decision to audit trail."""
        decision_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "decision_type": decision_type,
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "metadata": metadata or {}
        }
        state.decisions.append(decision_entry)
        
        # Store to audit log in GCS
        audit_id = f"{state.project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{stage}"
        audit_entry = AuditEntry(
            id=audit_id,
            project_id=state.project_id,
            timestamp=datetime.utcnow(),
            stage=stage,
            decision_type=decision_type,
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        await self.audit_storage.create(
            audit_entry,
            entity_id=audit_id,
            subfolder=state.project_id
        )
        
        # Emit decision event
        await self._emit_event(state, "decision", decision_entry)
    
    async def _request_approval(
        self,
        state: PipelineState,
        approval_type: str,
        data: Any,
        message: str
    ) -> None:
        """Request user approval."""
        await self._emit_event(state, "approval_required", {
            "approval_type": approval_type,
            "data": data,
            "message": message
        })
        
        # In production, this would wait for user response
        # For now, we'll just log it
        await self._emit_log(state, "info", f"Approval requested: {message}")
    
    async def _emit_event(
        self,
        state: PipelineState,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Emit an event to registered callbacks."""
        callbacks = self.event_callbacks.get(state.project_id, [])
        
        event = {
            "project_id": state.project_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(
                    "event_callback_error",
                    project_id=state.project_id,
                    event_type=event_type,
                    error=str(e)
                )
    
    async def _store_state(self, state: PipelineState) -> None:
        """Store pipeline state to GCS."""
        from google.cloud import storage
        
        client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        bucket = client.bucket(self.storage_bucket)
        
        state_path = f"pipeline_states/{state.project_id}/state.json"
        blob = bucket.blob(state_path)
        
        import json
        blob.upload_from_string(
            json.dumps(state.to_dict(), indent=2),
            content_type='application/json'
        )
    
    async def _handle_pipeline_error(
        self,
        state: PipelineState,
        error: Exception
    ) -> None:
        """Handle pipeline execution error."""
        state.stage = PipelineStage.FAILED
        state.error = str(error)
        state.updated_at = datetime.utcnow()
        
        await self._emit_log(state, "error", f"Pipeline failed: {str(error)}")
        await self._emit_event(state, "pipeline_failed", {
            "error": str(error),
            "stage": state.stage
        })
        
        await self._store_state(state)
    
    def register_event_callback(
        self,
        project_id: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Register a callback for pipeline events.
        
        Args:
            project_id: Project identifier
            callback: Callback function to receive events
        """
        if project_id not in self.event_callbacks:
            self.event_callbacks[project_id] = []
        self.event_callbacks[project_id].append(callback)
    
    def unregister_event_callback(
        self,
        project_id: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Unregister an event callback.
        
        Args:
            project_id: Project identifier
            callback: Callback function to remove
        """
        if project_id in self.event_callbacks:
            self.event_callbacks[project_id].remove(callback)
    
    async def cancel_pipeline(self, project_id: str) -> bool:
        """
        Cancel a running pipeline.
        
        Args:
            project_id: Project identifier
            
        Returns:
            True if cancelled, False if not found or already completed
        """
        state = self.states.get(project_id)
        if not state:
            return False
        
        if state.stage in [PipelineStage.COMPLETED, PipelineStage.FAILED, PipelineStage.CANCELLED]:
            return False
        
        state.stage = PipelineStage.CANCELLED
        state.updated_at = datetime.utcnow()
        
        await self._emit_log(state, "info", "Pipeline cancelled by user")
        await self._emit_event(state, "pipeline_cancelled", {})
        await self._store_state(state)
        
        logger.info("pipeline_cancelled", project_id=project_id)
        return True
    
    async def get_pipeline_state(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current pipeline state.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Pipeline state dictionary or None if not found
        """
        state = self.states.get(project_id)
        if state:
            return state.to_dict()
        
        # Try loading from GCS
        from google.cloud import storage
        import json
        
        try:
            client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
            bucket = client.bucket(self.storage_bucket)
            
            state_path = f"pipeline_states/{project_id}/state.json"
            blob = bucket.blob(state_path)
            
            if blob.exists():
                content = blob.download_as_text()
                return json.loads(content)
        except Exception as e:
            logger.error("failed_to_load_state", project_id=project_id, error=str(e))
        
        return None
