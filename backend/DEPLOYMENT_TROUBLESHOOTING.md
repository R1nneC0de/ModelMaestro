# Vertex AI Deployment Troubleshooting Guide

## Error: 409 ABORTED

### Problem
You're seeing this error:
```
google.api_core.exceptions.Aborted: 409 ABORTED 10: ABORTED
```

### Root Causes

1. **Endpoint Name Conflict**: An endpoint with the same display name already exists or is being created
2. **Concurrent Operations**: Another operation is modifying the same endpoint
3. **Stale Operation**: A previous operation didn't complete cleanly
4. **Quota Issues**: Project quotas or limits are being hit

### Solutions

#### Solution 1: Use Unique Endpoint Names (Recommended)

Run the deployment with a timestamp-based unique name:

```bash
python3 backend/test_deployment_with_unique_name.py
```

This script automatically generates unique endpoint names like:
- `endpoint_churn_test_20251108_183410_20241109_143022`

#### Solution 2: Clean Up Existing Endpoints

1. List all endpoints:
```bash
python3 backend/fix_endpoint_conflict.py
```

2. Delete conflicting endpoints through the script menu

3. Or use gcloud CLI:
```bash
# List endpoints
gcloud ai endpoints list --region=us-central1

# Delete specific endpoint
gcloud ai endpoints delete ENDPOINT_ID --region=us-central1
```

#### Solution 3: Wait and Retry

Sometimes operations are still in progress:

1. Wait 2-5 minutes
2. Retry the deployment
3. The updated code now handles this automatically with retry logic

#### Solution 4: Check Quotas

Verify you haven't hit quota limits:

```bash
gcloud compute project-info describe --project=YOUR_PROJECT_ID
```

Check for:
- Endpoint quota
- Compute instance quota
- API rate limits

### Prevention

#### 1. Always Use Unique Names

Update your deployment code to include timestamps:

```python
from datetime import datetime

timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
endpoint_name = f"endpoint_{model_id}_{timestamp}"
```

#### 2. Clean Up After Testing

Always undeploy models and delete endpoints when done:

```python
# Undeploy model
endpoint.undeploy(deployed_model_id=model_id, sync=True)

# Delete endpoint
endpoint.delete(force=True, sync=True)
```

#### 3. Use the Fix Script Regularly

Run the cleanup script periodically:

```bash
python3 backend/fix_endpoint_conflict.py
```

### Updated Code

The `vertex_deployment.py` has been updated with:

1. **Better error messages** - Explains the issue and solutions
2. **Automatic retry logic** - Retries finding the endpoint after ABORTED errors
3. **Sync operations** - Waits for operations to complete
4. **Detailed logging** - Shows what's happening at each step

### Testing the Fix

1. **Test with unique name**:
```bash
python3 backend/test_deployment_with_unique_name.py
```

2. **Verify no conflicts**:
```bash
python3 backend/fix_endpoint_conflict.py
```

3. **Check deployment**:
```bash
gcloud ai endpoints list --region=us-central1
```

### Common Patterns

#### Pattern 1: Development Testing

For development, use unique names each time:

```python
endpoint_name = f"dev_endpoint_{model_id}_{timestamp}"
```

#### Pattern 2: Production Deployment

For production, reuse endpoint names but handle conflicts:

```python
# Try to get existing endpoint first
endpoints = aiplatform.Endpoint.list(
    filter=f'display_name="{endpoint_name}"'
)

if endpoints:
    # Reuse existing endpoint
    endpoint = endpoints[0]
else:
    # Create new endpoint
    endpoint = aiplatform.Endpoint.create(...)
```

#### Pattern 3: Blue-Green Deployment

Use versioned endpoint names:

```python
endpoint_name = f"endpoint_{model_id}_v{version}"
```

### Monitoring

After deployment, monitor endpoint health:

```python
from app.services.cloud.health_monitor import DeploymentHealthMonitor

monitor = DeploymentHealthMonitor()
health = await monitor.perform_health_check(
    model_id=model_id,
    endpoint_resource_name=endpoint_resource_name
)
```

### Cost Management

Remember:
- Endpoints cost ~$0.10/hour while running
- Undeploy models when not in use
- Delete unused endpoints
- Use autoscaling to minimize costs

### Getting Help

If issues persist:

1. Check Vertex AI logs:
```bash
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" --limit=50
```

2. Check operation status:
```bash
gcloud ai operations list --region=us-central1
```

3. Contact support with:
   - Error message
   - Endpoint name
   - Model resource name
   - Timestamp of failure
