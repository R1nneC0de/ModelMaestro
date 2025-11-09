"""
Check the status of a Vertex AI endpoint deployment.
"""

import asyncio
from google.cloud import aiplatform
from app.core.config import settings
import time

async def check_deployment_status():
    """Check the status of the latest endpoint deployment."""
    print("\n" + "="*80)
    print("DEPLOYMENT STATUS CHECKER")
    print("="*80)
    print(f"Project: {settings.GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {settings.VERTEX_AI_LOCATION}")
    print(f"Credentials: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
    
    # Set credentials environment variable
    import os
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
    
    # Initialize Vertex AI
    aiplatform.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.VERTEX_AI_LOCATION
    )
    
    # List all endpoints
    print("\n📋 Fetching endpoints...")
    endpoints = aiplatform.Endpoint.list()
    
    if not endpoints:
        print("   No endpoints found")
        return
    
    print(f"\n   Found {len(endpoints)} endpoint(s)\n")
    
    # Show all endpoints with their status
    for i, endpoint in enumerate(endpoints, 1):
        print(f"{i}. {endpoint.display_name}")
        print(f"   Resource: {endpoint.resource_name}")
        print(f"   Created: {endpoint.create_time}")
        
        try:
            deployed_models = endpoint.list_models()
            
            if deployed_models:
                print(f"   ✅ Status: DEPLOYED")
                print(f"   Deployed Models: {len(deployed_models)}")
                
                for model in deployed_models:
                    print(f"      - {model.display_name}")
                    print(f"        Model ID: {model.id}")
                    if hasattr(model, 'create_time'):
                        print(f"        Deployed: {model.create_time}")
                
                # Show prediction endpoint
                print(f"\n   🌐 Prediction Endpoint:")
                print(f"      {endpoint.resource_name}:predict")
                
            else:
                print(f"   ⏳ Status: DEPLOYING (no models deployed yet)")
                print(f"      This usually takes 5-10 minutes")
                print(f"      Run this script again to check progress")
        
        except Exception as e:
            print(f"   ⚠️  Error checking models: {e}")
        
        print()
    
    # Check for operations in progress
    print("\n" + "="*80)
    print("CHECKING OPERATIONS")
    print("="*80)
    
    try:
        # Note: Operations API requires additional setup
        print("\n💡 To check operation status, use:")
        print("   gcloud ai operations list --region=us-central1")
        print("\n   Or wait and run this script again in a few minutes")
    except Exception as e:
        print(f"   Could not check operations: {e}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    deployed_count = sum(1 for ep in endpoints if ep.list_models())
    deploying_count = len(endpoints) - deployed_count
    
    print(f"\n✅ Deployed: {deployed_count}")
    print(f"⏳ Deploying: {deploying_count}")
    
    if deploying_count > 0:
        print(f"\n💡 Deployment in progress. Check again in a few minutes:")
        print(f"   python3 backend/check_deployment_status.py")
    
    print()


if __name__ == "__main__":
    asyncio.run(check_deployment_status())
