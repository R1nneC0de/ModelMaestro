"""
Check detailed operation status for deployments.
"""

import subprocess
import json

def check_operations():
    """Check running operations in Vertex AI."""
    print("\n" + "="*80)
    print("CHECKING VERTEX AI OPERATIONS")
    print("="*80)
    
    try:
        # Check running operations
        print("\n📋 Running Operations:")
        result = subprocess.run(
            ["gcloud", "ai", "operations", "list", 
             "--region=us-central1", 
             "--filter=state:RUNNING",
             "--format=json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            operations = json.loads(result.stdout) if result.stdout else []
            
            if operations:
                for op in operations:
                    print(f"\n   Operation: {op.get('name', 'Unknown')}")
                    print(f"   State: {op.get('metadata', {}).get('genericMetadata', {}).get('state', 'Unknown')}")
                    print(f"   Type: {op.get('metadata', {}).get('@type', 'Unknown')}")
            else:
                print("   No running operations found")
                print("\n   ⚠️  This might mean:")
                print("      1. Deployment completed (check endpoints)")
                print("      2. Deployment failed silently")
                print("      3. Operation is in a different state")
        else:
            print(f"   Error: {result.stderr}")
    
    except Exception as e:
        print(f"   Error checking operations: {e}")
    
    # Check all recent operations
    print("\n" + "="*80)
    print("RECENT OPERATIONS (Last 10)")
    print("="*80)
    
    try:
        result = subprocess.run(
            ["gcloud", "ai", "operations", "list", 
             "--region=us-central1", 
             "--limit=10",
             "--format=table(name,metadata.genericMetadata.state,done)"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Check endpoints
    print("\n" + "="*80)
    print("ENDPOINT STATUS")
    print("="*80)
    
    try:
        result = subprocess.run(
            ["gcloud", "ai", "endpoints", "list", 
             "--region=us-central1",
             "--format=table(name,displayName,deployedModels.length)"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("\n💡 If operations show as 'done' but endpoints have no models:")
    print("   - The deployment may have failed")
    print("   - Check Cloud Console for error details")
    print("   - Try deploying to a new endpoint")
    print("\n💡 If no operations are running:")
    print("   - Deployment may have completed or failed")
    print("   - Run: python3 backend/check_deployment_status.py")
    print("\n💡 If taking too long (>25 minutes):")
    print("   - Consider canceling and redeploying")
    print("   - Check project quotas and limits")
    print("   - Try a different region if available")
    print()

if __name__ == "__main__":
    check_operations()
