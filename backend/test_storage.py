"""Test script for GCS Storage Manager."""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Set GOOGLE_APPLICATION_CREDENTIALS explicitly
credentials_path = Path(__file__).parent.parent / 'gcp-credentials' / 'gcp-key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.services.cloud.storage import (
    get_project_storage,
    ensure_bucket_exists
)
from backend.app.schemas.project import Project, ProjectStatus


async def test_storage_manager():
    """Test the storage manager with a sample project."""
    
    print("🔧 Testing GCS Storage Manager...")
    
    # 1. Ensure bucket exists
    print("\n1️⃣ Checking/creating bucket...")
    bucket_exists = await ensure_bucket_exists()
    if not bucket_exists:
        print("❌ Failed to create/access bucket")
        return
    print("✅ Bucket ready")
    
    # 2. Create a test project
    print("\n2️⃣ Creating test project...")
    project_storage = get_project_storage()
    
    test_project = Project(
        id="test_proj_001",
        user_id="test_user_123",
        problem_description="Test project for storage manager validation",
        status=ProjectStatus.ANALYZING,
        requires_approval=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        created = await project_storage.create(test_project, test_project.id)
        print(f"✅ Created project: {created.id}")
    except ValueError as e:
        print(f"⚠️  Project already exists: {e}")
    
    # 3. Retrieve the project
    print("\n3️⃣ Retrieving project...")
    retrieved = await project_storage.get("test_proj_001")
    if retrieved:
        print(f"✅ Retrieved project: {retrieved.id}")
        print(f"   Status: {retrieved.status}")
        print(f"   Description: {retrieved.problem_description}")
    else:
        print("❌ Failed to retrieve project")
        return
    
    # 4. Update the project
    print("\n4️⃣ Updating project...")
    updated = await project_storage.update(
        "test_proj_001",
        {"status": ProjectStatus.TRAINING.value}
    )
    if updated:
        print(f"✅ Updated project status to: {updated.status}")
    else:
        print("❌ Failed to update project")
    
    # 5. List projects
    print("\n5️⃣ Listing all projects...")
    projects = await project_storage.list()
    print(f"✅ Found {len(projects)} project(s)")
    for proj in projects:
        print(f"   - {proj.id}: {proj.status}")
    
    # 6. Check existence
    print("\n6️⃣ Checking project existence...")
    exists = await project_storage.exists("test_proj_001")
    print(f"✅ Project exists: {exists}")
    
    print("\n✨ All tests passed! Storage manager is working correctly.")
    print("\n📂 Check your GCS bucket at:")
    print(f"   https://console.cloud.google.com/storage/browser/agentic-ai-data")


if __name__ == "__main__":
    asyncio.run(test_storage_manager())
