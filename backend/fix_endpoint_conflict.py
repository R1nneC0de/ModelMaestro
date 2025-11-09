"""
Fix endpoint conflict by listing and optionally deleting existing endpoints.
"""

import asyncio
from google.cloud import aiplatform
from app.core.config import settings

async def list_and_fix_endpoints():
    """List all endpoints and optionally delete conflicting ones."""
    print("\n" + "="*80)
    print("ENDPOINT CONFLICT RESOLVER")
    print("="*80)
    print(f"Project: {settings.GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {settings.VERTEX_AI_LOCATION}")
    
    # Initialize Vertex AI
    aiplatform.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.VERTEX_AI_LOCATION
    )
    
    # List all endpoints
    print("\n📋 Listing all endpoints...")
    endpoints = aiplatform.Endpoint.list()
    
    if not endpoints:
        print("   No endpoints found")
        return
    
    print(f"\n   Found {len(endpoints)} endpoint(s):\n")
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"   {i}. {endpoint.display_name}")
        print(f"      Resource Name: {endpoint.resource_name}")
        print(f"      Created: {endpoint.create_time}")
        
        # Check deployed models
        try:
            deployed_models = endpoint.list_models()
            print(f"      Deployed Models: {len(deployed_models)}")
            for model in deployed_models:
                print(f"         - {model.display_name} (ID: {model.id})")
        except Exception as e:
            print(f"      Error listing models: {e}")
        
        print()
    
    # Ask user what to do
    print("\n" + "="*80)
    print("OPTIONS:")
    print("="*80)
    print("1. Delete a specific endpoint")
    print("2. Delete all endpoints")
    print("3. Exit without changes")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        endpoint_num = input(f"Enter endpoint number to delete (1-{len(endpoints)}): ").strip()
        try:
            idx = int(endpoint_num) - 1
            if 0 <= idx < len(endpoints):
                endpoint = endpoints[idx]
                await delete_endpoint(endpoint)
            else:
                print("❌ Invalid endpoint number")
        except ValueError:
            print("❌ Invalid input")
    
    elif choice == "2":
        confirm = input(f"\n⚠️  Delete ALL {len(endpoints)} endpoints? (yes/no): ").strip()
        if confirm.lower() in ['yes', 'y']:
            for endpoint in endpoints:
                await delete_endpoint(endpoint)
        else:
            print("❌ Cancelled")
    
    else:
        print("✅ No changes made")


async def delete_endpoint(endpoint):
    """Delete an endpoint with all deployed models."""
    print(f"\n🗑️  Deleting endpoint: {endpoint.display_name}")
    print(f"   Resource: {endpoint.resource_name}")
    
    try:
        # Check for deployed models
        deployed_models = endpoint.list_models()
        
        if deployed_models:
            print(f"   Found {len(deployed_models)} deployed model(s)")
            print(f"   Undeploying models first...")
            
            for model in deployed_models:
                print(f"      Undeploying: {model.display_name}")
                try:
                    endpoint.undeploy(deployed_model_id=model.id, sync=True)
                    print(f"      ✅ Undeployed: {model.display_name}")
                except Exception as e:
                    print(f"      ⚠️  Error undeploying {model.display_name}: {e}")
        
        # Delete the endpoint
        print(f"   Deleting endpoint...")
        endpoint.delete(force=True, sync=True)
        print(f"   ✅ Endpoint deleted successfully")
        
    except Exception as e:
        print(f"   ❌ Error deleting endpoint: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(list_and_fix_endpoints())
