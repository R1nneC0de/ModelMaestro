"""
Monitor deployment progress with automatic polling.
"""

import asyncio
import time
from google.cloud import aiplatform
from app.core.config import settings
import os

async def monitor_deployment(check_interval=60, max_checks=15):
    """
    Monitor deployment progress with automatic polling.
    
    Args:
        check_interval: Seconds between checks (default: 60)
        max_checks: Maximum number of checks before stopping (default: 15 = 15 minutes)
    """
    print("\n" + "="*80)
    print("DEPLOYMENT MONITOR")
    print("="*80)
    print(f"Project: {settings.GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {settings.VERTEX_AI_LOCATION}")
    print(f"Check interval: {check_interval} seconds")
    print(f"Max duration: {max_checks * check_interval / 60:.1f} minutes")
    
    # Set credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
    
    # Initialize Vertex AI
    aiplatform.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.VERTEX_AI_LOCATION
    )
    
    check_count = 0
    deployed_endpoints = set()
    
    while check_count < max_checks:
        check_count += 1
        print(f"\n{'='*80}")
        print(f"CHECK #{check_count} - {time.strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        try:
            endpoints = aiplatform.Endpoint.list()
            
            if not endpoints:
                print("   No endpoints found")
                break
            
            all_deployed = True
            newly_deployed = []
            
            for endpoint in endpoints:
                endpoint_id = endpoint.resource_name
                deployed_models = endpoint.list_models()
                
                if deployed_models:
                    # Endpoint is deployed
                    if endpoint_id not in deployed_endpoints:
                        newly_deployed.append(endpoint)
                        deployed_endpoints.add(endpoint_id)
                    
                    print(f"\n✅ {endpoint.display_name}")
                    print(f"   Status: DEPLOYED")
                    print(f"   Models: {len(deployed_models)}")
                    for model in deployed_models:
                        print(f"      - {model.display_name}")
                else:
                    # Still deploying
                    all_deployed = False
                    elapsed = (time.time() - endpoint.create_time.timestamp()) / 60
                    print(f"\n⏳ {endpoint.display_name}")
                    print(f"   Status: DEPLOYING")
                    print(f"   Elapsed: {elapsed:.1f} minutes")
            
            # Show newly deployed endpoints
            if newly_deployed:
                print(f"\n{'='*80}")
                print("🎉 NEWLY DEPLOYED ENDPOINTS")
                print(f"{'='*80}")
                
                for endpoint in newly_deployed:
                    print(f"\n✅ {endpoint.display_name}")
                    print(f"   Endpoint ID: {endpoint.name.split('/')[-1]}")
                    print(f"   Resource: {endpoint.resource_name}")
                    print(f"\n   🌐 Prediction Endpoint:")
                    print(f"      {endpoint.resource_name}:predict")
                    print(f"\n   💡 To make predictions:")
                    print(f"      endpoint = aiplatform.Endpoint('{endpoint.resource_name}')")
                    print(f"      predictions = endpoint.predict(instances=[...])")
            
            # Check if all are deployed
            if all_deployed:
                print(f"\n{'='*80}")
                print("✅ ALL DEPLOYMENTS COMPLETE!")
                print(f"{'='*80}")
                print(f"\n   Total endpoints: {len(endpoints)}")
                print(f"   All deployed: {len(deployed_endpoints)}")
                print(f"\n   💡 Next steps:")
                print(f"      1. Test predictions with your endpoint")
                print(f"      2. Monitor endpoint health")
                print(f"      3. Remember to undeploy when done to save costs")
                print(f"\n   ⚠️  Cost reminder: ~$0.10/hour per endpoint")
                break
            
            # Wait before next check
            if check_count < max_checks:
                print(f"\n⏰ Next check in {check_interval} seconds...")
                print(f"   (Press Ctrl+C to stop monitoring)")
                await asyncio.sleep(check_interval)
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Monitoring stopped by user")
            print(f"   Deployment is still in progress")
            print(f"   Run this script again to continue monitoring")
            break
        
        except Exception as e:
            print(f"\n❌ Error during check: {e}")
            import traceback
            traceback.print_exc()
            
            if check_count < max_checks:
                print(f"\n   Retrying in {check_interval} seconds...")
                await asyncio.sleep(check_interval)
    
    if check_count >= max_checks:
        print(f"\n{'='*80}")
        print("⏰ MONITORING TIMEOUT")
        print(f"{'='*80}")
        print(f"\n   Reached maximum checks ({max_checks})")
        print(f"   Deployment may still be in progress")
        print(f"\n   💡 Options:")
        print(f"      1. Run this script again to continue monitoring")
        print(f"      2. Check manually: python3 backend/check_deployment_status.py")
        print(f"      3. Use gcloud: gcloud ai endpoints list --region=us-central1")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    print("\n🔍 Starting deployment monitor...")
    print("   This will check deployment status every minute")
    print("   Press Ctrl+C to stop\n")
    
    try:
        asyncio.run(monitor_deployment(check_interval=60, max_checks=15))
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring stopped")
