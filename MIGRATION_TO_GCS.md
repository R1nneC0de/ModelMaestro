# Migration to GCS-Only Storage

This document summarizes the changes made to remove PostgreSQL database dependency and use Google Cloud Storage for all data persistence.

## Changes Made

### 1. Removed Files
- `backend/alembic/` - Entire Alembic migration directory
- `backend/alembic.ini` - Alembic configuration
- `backend/app/db/` - Database connection and session management
- `backend/app/models/` - SQLAlchemy models directory

### 2. Updated Dependencies (pyproject.toml)
**Removed:**
- `sqlalchemy`
- `alembic`
- `psycopg2-binary`

**Kept:**
- `pydantic` - For data validation and schemas
- `google-cloud-storage` - For GCS operations
- All other dependencies remain unchanged

### 3. Updated Docker Compose
**Removed:**
- PostgreSQL service and volume
- `DATABASE_URL` environment variable from backend and celery services

**Updated:**
- Backend and celery services now only depend on Redis
- Added explicit GCS environment variables

### 4. Updated Configuration
**backend/app/core/config.py:**
- Removed `DATABASE_URL` setting
- Kept all GCS-related settings

**.env.example:**
- Removed `DATABASE_URL`
- All GCS settings remain

### 5. Updated Documentation

**README.md:**
- Removed database migration steps
- Updated tech stack section
- Updated troubleshooting section
- Removed Alembic guide reference

**Design Document:**
- Updated architecture diagram (removed PostgreSQL)
- Changed "Database Schema" to "GCS Storage Structure"
- Converted SQLAlchemy models to Pydantic schemas
- Added GCS bucket structure documentation

**Tasks Document:**
- Task 2 changed from "Implement database models and migrations" to "Implement GCS-based storage service"
- Subtask 2.1: Create StorageManager class for GCS operations
- Subtask 2.2: Create Pydantic schemas instead of SQLAlchemy models
- Updated all references to "database" to "GCS" throughout

### 6. New Documentation
**docs/guides/gcs-storage-structure.md:**
- Complete guide to GCS storage structure
- JSON schema examples for all entities
- Storage manager interface description
- Trade-offs and migration path

## Next Steps

To implement the GCS storage approach:

1. **Create StorageManager** (Task 2.1)
   - Implement CRUD operations for JSON files in GCS
   - Add list/query functionality with filtering
   - Handle concurrency with optimistic locking

2. **Create Pydantic Schemas** (Task 2.2)
   - Define Project, Dataset, Model, AuditEntry schemas
   - Add validation rules
   - Implement serialization/deserialization

3. **Update All Services**
   - Replace database session dependencies with StorageManager
   - Update all CRUD operations to use GCS
   - Adjust query patterns for file-based storage

## Benefits

- **Simpler Architecture**: No database to manage or migrate
- **Lower Costs**: No Cloud SQL instance needed
- **Faster Setup**: One less service to configure
- **Easy Backups**: Just copy the GCS bucket

## Considerations

- Queries will be slower for large datasets (load all files, filter in memory)
- No ACID transactions (implement optimistic locking if needed)
- Concurrency requires careful handling
- Consider migrating to a database if you need complex queries or high concurrency
