"""List all Vertex AI endpoints."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from google.cloud import aiplatform
from app.core.config import settings

def list_endpoints():
    """List all endpoints in Vertex AI."""
    print("\n" + "="*80)
    print("VERTEX AI ENDPOINTS")
    print("="*80)
    print(f"Project: {settings.GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {settings.VERTEX_AI_LOCATION}")
    
    try:
        aiplatform.init(
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.VERTEX_AI_LOCATION
        )
        
        print("\n🔍 Listing all endpoints...")
        endpoints = aiplatform.Endpoint.list()
        
        if not endpoints:
            print("\n❌ No endpoints found")
            return
        
        print(f"\n✅ Found {len(endpoints)} endpoint(s):\n")
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"{i}. {endpoint.display_name}")
            print(f"   Resource name: {endpoint.resource_name}")
            print(f"   Created: {endpoint.create_time}")
            
            # Check deployed models
            if hasattr(endpoint, 'traffic_split') and endpoint.traffic_split:
                print(f"   🚀 Deployed models: {len(endpoint.traffic_split)}")
                for model_id, traffic in endpoint.traffic_split.items():
                    print(f"      - Model {model_id}: {traffic}% traffic")
            else:
                print(f"   📦 No models deployed yet")
            
            print()
        
    except Exception as e:
        print(f"\n❌ Error listing endpoints: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_endpoints()
