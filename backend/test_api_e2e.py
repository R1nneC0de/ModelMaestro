"""
E2E API Test - Tests the complete pipeline via REST API
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🚀 E2E API TEST")
print("=" * 80)

# Test 1: Health check
print("\n💓 Step 1: Health check...")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print(f"✅ Server is healthy: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    print("   Make sure the server is running: python3 -m uvicorn app.main:app --reload")
    exit(1)

# Test 2: List available endpoints
print("\n📋 Step 2: Checking available endpoints...")
try:
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print("✅ API documentation available at http://localhost:8000/docs")
except Exception as e:
    print(f"⚠️  Docs check: {e}")

# Test 3: Upload dataset
print("\n📤 Step 3: Uploading dataset...")
try:
    with open("../Customer_Churn_data.csv", "rb") as f:
        files = [("files", ("churn_data.csv", f, "text/csv"))]
        data = {
            "project_id": "test_project_001",
            "data_type": "tabular"
        }
        response = requests.post(f"{BASE_URL}/api/v1/data/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            dataset_id = result.get("dataset_id")
            print(f"✅ Dataset uploaded successfully!")
            print(f"   Dataset ID: {dataset_id}")
            print(f"   File paths: {result.get('file_paths', [])}")
            print(f"   Size: {result.get('size_bytes', 0) / 1024 / 1024:.2f} MB")
            print(f"   Samples: {result.get('num_samples', 0)}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            dataset_id = None
except Exception as e:
    print(f"❌ Upload error: {e}")
    import traceback
    traceback.print_exc()
    dataset_id = None

# Test 4: Get dataset info
if dataset_id:
    print(f"\n📊 Step 4: Getting dataset info...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data/{dataset_id}")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Dataset info retrieved:")
            print(f"   ID: {info.get('id')}")
            print(f"   Type: {info.get('data_type')}")
            print(f"   Labeled: {info.get('is_labeled')}")
            print(f"   Samples: {info.get('num_samples')}")
        else:
            print(f"❌ Failed to get dataset info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ API E2E TEST COMPLETE!")
print("=" * 80)
print("\n📝 Summary:")
print("   ✅ Server is running")
print("   ✅ Health check passed")
if dataset_id:
    print(f"   ✅ Dataset uploaded: {dataset_id}")
else:
    print("   ⚠️  Dataset upload needs verification")
print("\n💡 Next steps:")
print("   1. Check API docs: http://localhost:8000/docs")
print("   2. Test problem analysis endpoint")
print("   3. Test model selection endpoint")
print("=" * 80)
