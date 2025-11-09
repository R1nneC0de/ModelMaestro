"""
Check for trained models in Vertex AI.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from google.cloud import aiplatform
from app.core.config import settings

def check_models():
    """Check for models in Vertex AI."""
    print("\n" + "="*80)
    print("CHECKING VERTEX AI MODELS")
    print("="*80)
    print(f"Project: {settings.GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {settings.VERTEX_AI_LOCATION}")
    
    try:
        aiplatform.init(
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.VERTEX_AI_LOCATION
        )
        
        # List all models
        print("\n🔍 Listing all models...")
        models = aiplatform.Model.list()
        
        if not models:
            print("\n❌ No models found in Vertex AI")
            print("\nThis means:")
            print("  - No training has completed successfully yet")
            print("  - Or training is still in progress")
            print("\nTo check training status, run:")
            print("  python backend/check_training_jobs.py")
            return
        
        print(f"\n✅ Found {len(models)} model(s):\n")
        
        for i, model in enumerate(models, 1):
            print(f"{i}. {model.display_name}")
            print(f"   Resource name: {model.resource_name}")
            print(f"   Created: {model.create_time}")
            
            if hasattr(model, 'labels') and model.labels:
                print(f"   Labels: {model.labels}")
            
            # Check if model has artifact URI
            if hasattr(model, 'artifact_uri') and model.artifact_uri:
                print(f"   Artifact URI: {model.artifact_uri}")
            else:
                print(f"   ℹ️  No artifact URI (AutoML stores internally)")
            
            # Check deployment status
            if hasattr(model, 'deployed_models'):
                deployed = model.deployed_models
                if deployed:
                    print(f"   🚀 Deployed to {len(deployed)} endpoint(s)")
                else:
                    print(f"   📦 Not deployed yet")
            
            print()
        
        print("\n💡 To deploy a model to an endpoint:")
        print("   Use the model resource name with the deployment service")
        
    except Exception as e:
        print(f"\n❌ Error checking models: {e}")
        import traceback
        traceback.print_exc()

def check_training_jobs():
    """Check for training jobs."""
    print("\n" + "="*80)
    print("CHECKING TRAINING JOBS")
    print("="*80)
    
    try:
        aiplatform.init(
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.VERTEX_AI_LOCATION
        )
        
        # List training pipelines
        print("\n🔍 Listing training pipelines...")
        
        from google.cloud.aiplatform_v1 import PipelineServiceClient
        
        client = PipelineServiceClient()
        parent = f"projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.VERTEX_AI_LOCATION}"
        
        pipelines = client.list_training_pipelines(parent=parent)
        
        pipeline_list = list(pipelines)
        
        if not pipeline_list:
            print("\n❌ No training pipelines found")
            return
        
        print(f"\n✅ Found {len(pipeline_list)} training pipeline(s):\n")
        
        for i, pipeline in enumerate(pipeline_list[:10], 1):  # Show last 10
            print(f"{i}. {pipeline.display_name}")
            print(f"   State: {pipeline.state.name}")
            print(f"   Created: {pipeline.create_time}")
            
            if pipeline.state.name == "PIPELINE_STATE_SUCCEEDED":
                print(f"   ✅ Training completed successfully")
                if pipeline.model_to_upload:
                    print(f"   📦 Model: {pipeline.model_to_upload.name}")
            elif pipeline.state.name == "PIPELINE_STATE_RUNNING":
                print(f"   ⏳ Training in progress...")
            elif pipeline.state.name == "PIPELINE_STATE_FAILED":
                print(f"   ❌ Training failed")
                if pipeline.error:
                    print(f"   Error: {pipeline.error.message}")
            
            print()
        
    except Exception as e:
        print(f"\n❌ Error checking training jobs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_models()
    check_training_jobs()
