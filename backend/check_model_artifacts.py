"""Check what artifacts exist for the trained models."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.cloud.storage import list_blobs
from app.core.config import settings


async def check_artifacts():
    """Check artifacts for all trained models."""
    print("\n" + "="*80)
    print("CHECKING MODEL ARTIFACTS IN GCS")
    print("="*80)
    print(f"Bucket: {settings.GCS_BUCKET_NAME}")
    
    # The 4 trained models
    model_ids = [
        "churn_test_20251108_183410",
        "churn_test_20251108_175413",
        "churn_test_20251108_151149",
        "churn_test_20251108_135811",
        "churn_test_20251108_120840"  # Also check this one
    ]
    
    for model_id in model_ids:
        print(f"\n{'='*80}")
        print(f"Model: {model_id}")
        print(f"{'='*80}")
        
        # Check in different locations
        locations = [
            f"data/{model_id}/",
            f"training_artifacts/{model_id}/",
            f"models/{model_id}/",
            f"evaluation_reports/{model_id}/"
        ]
        
        found_any = False
        
        for location in locations:
            try:
                blobs = await list_blobs(
                    prefix=location,
                    bucket_name=settings.GCS_BUCKET_NAME
                )
                
                if blobs:
                    found_any = True
                    print(f"\n📁 {location}")
                    print(f"   Found {len(blobs)} files:")
                    
                    # Group by subdirectory
                    subdirs = {}
                    for blob in blobs:
                        parts = blob.replace(location, "").split("/")
                        if len(parts) > 1:
                            subdir = parts[0]
                            if subdir not in subdirs:
                                subdirs[subdir] = []
                            subdirs[subdir].append("/".join(parts[1:]))
                        else:
                            if "root" not in subdirs:
                                subdirs["root"] = []
                            subdirs["root"].append(parts[0])
                    
                    for subdir, files in subdirs.items():
                        if subdir == "root":
                            for f in files[:5]:
                                print(f"      - {f}")
                        else:
                            print(f"      {subdir}/")
                            for f in files[:3]:
                                print(f"         - {f}")
                            if len(files) > 3:
                                print(f"         ... and {len(files) - 3} more")
                    
            except Exception as e:
                pass  # Location doesn't exist
        
        if not found_any:
            print(f"\n❌ No artifacts found for this model")
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print("\nAutoML models store their trained artifacts internally in Vertex AI.")
    print("They don't expose downloadable model files in GCS.")
    print("\nWhat you CAN download:")
    print("  ✅ Preprocessing artifacts (pipeline.pkl, train/val/test.pkl)")
    print("  ✅ Evaluation reports (if generated)")
    print("  ✅ Training logs and metadata")
    print("\nWhat you CANNOT download:")
    print("  ❌ Trained model weights (stored internally by AutoML)")
    print("  ❌ Model architecture files")
    print("\nTo use the trained model:")
    print("  1. Deploy to Vertex AI Endpoint (for real-time predictions)")
    print("  2. Use Batch Prediction API (for batch predictions)")
    print("  3. Export model (if supported by model type)")


if __name__ == "__main__":
    asyncio.run(check_artifacts())
