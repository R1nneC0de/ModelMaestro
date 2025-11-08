"""Create a GCS bucket."""

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

# Create bucket
bucket_name = "mubbu-is-dumb"
project_id = "agentic-workflow-477603"
location = "us-central1"

client = storage.Client(project=project_id)

try:
    bucket = client.create_bucket(bucket_name, location=location)
    print(f"✅ Bucket {bucket_name} created successfully!")
    print(f"📂 View at: https://console.cloud.google.com/storage/browser/{bucket_name}")
except Exception as e:
    print(f"❌ Error creating bucket: {e}")
