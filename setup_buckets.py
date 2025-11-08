"""Clean up and set up correct GCS bucket structure."""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Set credentials
credentials_path = Path(__file__).parent / 'gcp-credentials' / 'gcp-key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)

project_id = "agentic-workflow-477603"
location = "us-central1"
correct_bucket_name = "agentic-workflow-477603-data"

client = storage.Client(project=project_id)

print("🧹 Cleaning up existing buckets...")

# List all buckets in the project
buckets = list(client.list_buckets())
print(f"Found {len(buckets)} bucket(s) in project")

for bucket in buckets:
    print(f"\n📦 Bucket: {bucket.name}")
    
    # Delete all objects in the bucket first
    blobs = list(bucket.list_blobs())
    if blobs:
        print(f"   Deleting {len(blobs)} object(s)...")
        for blob in blobs:
            blob.delete()
            print(f"   ✓ Deleted {blob.name}")
    
    # Delete the bucket
    bucket.delete()
    print(f"   ✅ Deleted bucket {bucket.name}")

print("\n" + "="*50)
print("🏗️  Creating correct bucket structure...")
print("="*50)

# Create the main bucket
try:
    bucket = client.create_bucket(correct_bucket_name, location=location)
    print(f"\n✅ Created bucket: {correct_bucket_name}")
except Exception as e:
    print(f"\n⚠️  Bucket might already exist or error: {e}")
    bucket = client.bucket(correct_bucket_name)

# Create folder structure by uploading placeholder files
folders = [
    "projects/.placeholder",
    "datasets/.placeholder",
    "models/.placeholder",
    "audit/.placeholder",
    "data/.placeholder",
    "artifacts/.placeholder"
]

print("\n📁 Creating folder structure...")
for folder_path in folders:
    blob = bucket.blob(folder_path)
    blob.upload_from_string("")
    folder_name = folder_path.split('/')[0]
    print(f"   ✓ Created {folder_name}/ folder")

print("\n" + "="*50)
print("✨ Setup complete!")
print("="*50)
print(f"\n📂 Bucket structure:")
print(f"""
gs://{correct_bucket_name}/
├── projects/          # Project metadata JSON files
├── datasets/          # Dataset metadata JSON files
├── models/            # Model metadata JSON files
├── audit/             # Audit logs organized by project
├── data/              # Raw and processed data files
└── artifacts/         # Model artifacts and exports
""")
print(f"\n🌐 View in console:")
print(f"https://console.cloud.google.com/storage/browser/{correct_bucket_name}")
