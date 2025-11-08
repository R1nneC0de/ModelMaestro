"""Test script for uploading a dataset."""

import requests
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000/api/v1/data/upload"
CSV_FILE = "Customer_Churn_data.csv"
PROJECT_ID = "test_project_001"

def test_upload():
    """Test uploading a CSV file."""
    
    # Check if file exists
    file_path = Path(CSV_FILE)
    if not file_path.exists():
        print(f"❌ Error: File not found: {CSV_FILE}")
        return False
    
    print(f"📁 File found: {CSV_FILE}")
    print(f"📊 File size: {file_path.stat().st_size / 1024:.2f} KB")
    
    # Prepare the upload
    with open(file_path, 'rb') as f:
        files = {
            'files': (file_path.name, f, 'text/csv')
        }
        data = {
            'project_id': PROJECT_ID
        }
        
        print(f"\n🚀 Uploading to {API_URL}...")
        print(f"📦 Project ID: {PROJECT_ID}")
        
        try:
            response = requests.post(API_URL, files=files, data=data, timeout=30)
            
            print(f"\n📡 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print("\n✅ Upload successful!")
                print(f"   Dataset ID: {result['dataset_id']}")
                print(f"   Data Type: {result['data_type']}")
                print(f"   Num Files: {result['num_files']}")
                print(f"   Total Size: {result['total_size'] / 1024:.2f} KB")
                print(f"   Num Samples: {result['num_samples']}")
                print(f"   Message: {result['message']}")
                return True
            else:
                print(f"\n❌ Upload failed!")
                print(f"   Error: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to the API server.")
            print("   Make sure the backend is running on http://localhost:8000")
            return False
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return False

if __name__ == "__main__":
    success = test_upload()
    sys.exit(0 if success else 1)
