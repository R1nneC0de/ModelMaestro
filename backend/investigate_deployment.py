"""
Deep investigation of deployment status.
"""

import asyncio
import os
from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import EndpointServiceClient, ModelServiceClient
from app.core.config import settings

async def investigate():
    """Investigate deployment in detail."""
    print("\n" + "="*80)
    print("DEEP DEPLOYMENT INVESTIGATION")
    print("="*80)
    
    # Set credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
    
    # Initialize
    aiplatform.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.VERTEX_AI_LOCATION
    )
    
    # Check the specific model
    model_resource_name = "projects/314715177005/locations/us-central1/models/7575049075679035392"
    
    print(f"\n📦 Checking Model:")
    print(f"   {model_resource_name}")
    
    try:
        model = aiplatform.Model(model_resource_name)
        print(f"\n   ✅ Model found:")
        print(f"      Display Name: {model.display_name}")
        print(f"      Created: {model.create_time}")
        print(f"      Labels: {model.labels}")
        
        # Check if model has deployment info
        if hasattr(model, 'deployed_models'):
            print(f"      Deployed Models: {len(model.deployed_models) if model.deployed_models else 0}")
        
        # Check model's supported deployment resource pools
        print(f"\n   📋 Model Details:")
        print(f"      Resource Name: {model.resource_name}")
        print(f"      Version ID: {model.version_id if hasattr(model, 'version_id') else 'N/A'}")
        
    except Exception as e:
        print(f"   ❌ Error accessing model: {e}")
    
    # Check endpoints in detail
    print(f"\n" + "="*80)
    print("ENDPOINT DETAILS")
    print("="*80)
    
    try:
        endpoints = aiplatform.Endpoint.list()
        
        for endpoint in endpoints:
            print(f"\n🌐 Endpoint: {endpoint.display_name}")
            print(f"   Resource: {endpoint.resource_name}")
            print(f"   Created: {endpoint.create_time}")
            
            # Try to get more details
            try:
                # Check traffic split
                if hasattr(endpoint, 'traffic_split'):
                    print(f"   Traffic Split: {endpoint.traffic_split}")
                
                # Check deployed models
                deployed_models = endpoint.list_models()
                if deployed_models:
                    print(f"   ✅ Deployed Models: {len(deployed_models)}")
                    for dm in deployed_models:
                        print(f"      - {dm.display_name}")
                        print(f"        ID: {dm.id}")
                        print(f"        Model: {dm.model if hasattr(dm, 'model') else 'N/A'}")
                else:
                    print(f"   ⏳ No models deployed yet")
                    
                    # Try to get the endpoint client for more details
                    try:
                        client = EndpointServiceClient()
                        endpoint_path = endpoint.resource_name
                        endpoint_detail = client.get_endpoint(name=endpoint_path)
                        
                        print(f"\n   📊 Endpoint State:")
                        print(f"      State: {endpoint_detail.state if hasattr(endpoint_detail, 'state') else 'Unknown'}")
                        print(f"      Update Time: {endpoint_detail.update_time if hasattr(endpoint_detail, 'update_time') else 'Unknown'}")
                        
                        if hasattr(endpoint_detail, 'deployed_models'):
                            print(f"      Deployed Models Count: {len(endpoint_detail.deployed_models)}")
                            
                            for dm in endpoint_detail.deployed_models:
                                print(f"\n      Model Deployment:")
                                print(f"         ID: {dm.id}")
                                print(f"         Model: {dm.model}")
                                print(f"         Display Name: {dm.display_name}")
                                
                                if hasattr(dm, 'dedicated_resources'):
                                    dr = dm.dedicated_resources
                                    print(f"         Machine Type: {dr.machine_spec.machine_type if hasattr(dr, 'machine_spec') else 'N/A'}")
                                    print(f"         Min Replicas: {dr.min_replica_count}")
                                    print(f"         Max Replicas: {dr.max_replica_count}")
                        
                    except Exception as e:
                        print(f"   ⚠️  Could not get detailed endpoint info: {e}")
                
            except Exception as e:
                print(f"   ⚠️  Error getting endpoint details: {e}")
    
    except Exception as e:
        print(f"❌ Error listing endpoints: {e}")
    
    # Check for any errors in the deployment
    print(f"\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)
    
    print("\n🔍 Possible Issues:")
    print("   1. AutoML models can take 20-30 minutes for first deployment")
    print("   2. Resource allocation may be delayed")
    print("   3. Model artifacts may be large and slow to load")
    print("   4. Region capacity constraints")
    
    print("\n💡 Recommendations:")
    print("   1. Check Cloud Console for detailed error messages:")
    print("      https://console.cloud.google.com/vertex-ai/endpoints?project=agentic-workflow-477603")
    print("   2. If >30 minutes, consider canceling and redeploying")
    print("   3. Try deploying with min_replica_count=1, max_replica_count=1 (no autoscaling)")
    print("   4. Check project quotas: https://console.cloud.google.com/iam-admin/quotas")
    
    print()

if __name__ == "__main__":
    asyncio.run(investigate())
