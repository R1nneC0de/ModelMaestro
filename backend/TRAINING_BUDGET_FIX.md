# Training Budget and Job Monitoring Fixes

## Issues Fixed

### 1. Job Monitoring Error ✅
**Problem**: Training failed with "Unknown job type" error when monitoring AutoML jobs
```
Error: Unknown job type: projects/.../trainingPipelines/...
```

**Root Cause**: The job monitoring code was checking for `autoMlTabularTrainingJobs` in the resource name, but AutoML actually uses `trainingPipelines` in the resource path.

**Fix**: Updated `backend/app/services/cloud/vertex_jobs.py` to recognize both patterns:
```python
# Before
if "autoMlTabularTrainingJobs" in job_resource_name:

# After  
if "trainingPipelines" in job_resource_name or "autoMlTabularTrainingJobs" in job_resource_name:
```

### 2. Training Budget Optimization ✅
**Problem**: Small datasets (1,600 rows) were taking 1 hour to train, which is too slow for quick iterations.

**Solution**: Implemented tiered budget system based on dataset size in `backend/app/services/agent/selection_rules.py`:

| Dataset Size | Budget | Expected Time | Use Case |
|--------------|--------|---------------|----------|
| < 5,000 rows | 0.25 hours | **15-20 mins** | Small datasets, quick iterations |
| < 100,000 rows | 1.0 hours | 45-60 mins | Small-medium datasets |
| < 1,000,000 rows | 4.0 hours | 3-4 hours | Medium datasets |
| ≥ 1,000,000 rows | 24.0 hours | Up to 24 hours | Large datasets |

**Your Dataset**: 1,600 rows → **15 minutes** training time ⚡

## Budget Calculation

The budget is calculated in milli-node-hours:
- 0.25 hours = 250 milli-node-hours
- 1.0 hours = 1,000 milli-node-hours
- 4.0 hours = 4,000 milli-node-hours
- 24.0 hours = 24,000 milli-node-hours

## Cost Impact

Approximate costs per training run:
- **15 min budget**: ~$2 USD
- **1 hour budget**: ~$8 USD
- **4 hour budget**: ~$32 USD
- **24 hour budget**: ~$192 USD

## Testing

To test the fixes, run:
```bash
python3 backend/test_e2e_pipeline.py
```

Expected results:
1. ✅ Job monitoring works correctly
2. ✅ Training completes in ~15-20 minutes for small datasets
3. ✅ No "Unknown job type" errors

## Benefits

1. **Faster Iterations**: 15-20 min training for small datasets (was 60 min)
2. **Cost Efficient**: Lower budget = lower costs for small datasets
3. **Reliable Monitoring**: Fixed job status tracking
4. **Scalable**: Automatically adjusts budget based on dataset size

## Notes

- AutoML will still perform comprehensive model search within the budget
- Smaller budgets mean fewer model architectures tested, but still good results
- For production models, you can manually increase the budget if needed
- The system automatically scales budget up for larger datasets
