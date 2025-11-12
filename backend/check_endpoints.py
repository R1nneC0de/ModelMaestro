"""Check deployed Vertex AI endpoints."""
import asyncio
from google.cloud import aiplatform
from app.core.config import settings

async def check_endpoints():
    """Check all deployed endpoints."""
    print("\n" + "="*80)
    print("CHECKING VERTEX AI ENDPOINTS")
    print("="*80)
    print(f"Project: {settings.GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {settings.VERTEX_AI_LOCATION}")
    
    aiplatform.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.VERTEX_AI_LOCATION
    )
    
    print("\n🔍 Listing all endpoints...\n")
    
    try:
        endpoints = aiplatform.Endpoint.list()
        
        if not endpoints:
            print("❌ No endpoints found")
            return
        
        print(f"✅ Found {len(endpoints)} endpoint(s):\n")
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"{i}. {endpoint.display_name}")
            print(f"   Resource name: {endpoint.resource_name}")
            print(f"   Endpoint ID: {endpoint.name.split('/')[-1]}")
            print(f"   Created: {endpoint.create_time}")
            
            # Check deployed models
            if hasattr(endpoint, 'deployed_models') and endpoint.deployed_models:
                print(f"   📦 Deployed models: {len(endpoint.deployed_models)}")
                for dm in endpoint.deployed_models:
                    print(f"      - Model: {dm.model}")
                    print(f"        ID: {dm.id}")
            else:
                print(f"   ⚠️  No models deployed")
            
            # Construct console URL
            project_number = endpoint.resource_name.split('/')[1]
            endpoint_id = endpoint.name.split('/')[-1]
            console_url = (
                f"https://console.cloud.google.com/vertex-ai/locations/"
                f"{settings.VERTEX_AI_LOCATION}/endpoints/{endpoint_id}"
                f"?project={settings.GOOGLE_CLOUD_PROJECT}"
            )
            print(f"   🌐 Console URL: {console_url}")
            print()
            
    except Exception as e:
        print(f"❌ Error checking endpoints: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_endpoints())
