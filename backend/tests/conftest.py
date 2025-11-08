"""
Pytest configuration and fixtures.
"""
import os

# Set environment variables BEFORE any imports
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/test-credentials.json"
os.environ["GCS_BUCKET_NAME"] = "test-bucket"
os.environ["GEMINI_API_KEY"] = "test-api-key"
os.environ["ENVIRONMENT"] = "test"

import pytest
