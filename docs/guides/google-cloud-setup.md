# Google Cloud Project Setup Guide

This guide walks you through setting up the required Google Cloud services for the Agentic Model Training Platform.

## Prerequisites

- Google Cloud account
- `gcloud` CLI installed and configured
- Billing enabled on your GCP project

## Step 1: Create a Google Cloud Project

```bash
# Create a new project
gcloud projects create YOUR_PROJECT_ID --name="Agentic Model Training Platform"

# Set the project as default
gcloud config set project YOUR_PROJECT_ID

# Link billing account (replace BILLING_ACCOUNT_ID)
gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

## Step 2: Enable Required APIs

```bash
# Enable all required Google Cloud APIs
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  run.googleapis.com \
  generativelanguage.googleapis.com \
  logging.googleapis.com \
  cloudresourcemanager.googleapis.com
```

## Step 3: Create a Service Account

```bash
# Create service account
gcloud iam service-accounts create agentic-platform-sa \
  --display-name="Agentic Platform Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:agentic-platform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:agentic-platform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:agentic-platform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

# Create and download service account key
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=agentic-platform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Move the key to the credentials directory
mkdir -p gcp-credentials
mv gcp-key.json gcp-credentials/
```

## Step 4: Create Cloud Storage Bucket

```bash
# Create bucket for data storage
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://YOUR_BUCKET_NAME

# Set lifecycle policy for automatic cleanup
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://YOUR_BUCKET_NAME
```

## Step 5: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key to your `.env` file

## Step 6: Configure Environment Variables

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Update the following variables:
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GCS_BUCKET_NAME`: Your Cloud Storage bucket name
- `GEMINI_API_KEY`: Your Gemini API key

## Step 7: Verify Setup

Test your configuration:

```bash
# Test GCS access
gsutil ls gs://YOUR_BUCKET_NAME

# Test service account permissions
gcloud auth activate-service-account --key-file=gcp-credentials/gcp-key.json
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

## Security Best Practices

1. **Never commit credentials**: Add `gcp-credentials/` and `.env` to `.gitignore`
2. **Rotate keys regularly**: Rotate service account keys every 90 days
3. **Use least privilege**: Only grant necessary IAM roles
4. **Enable audit logging**: Monitor API usage and access patterns
5. **Set up billing alerts**: Prevent unexpected costs

## Cost Optimization

- Set budget alerts in GCP Console
- Use Vertex AI training budget limits
- Enable automatic data cleanup (lifecycle policies)
- Monitor API usage regularly

## Troubleshooting

### Authentication Errors
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Check service account has required permissions
- Ensure APIs are enabled

### Storage Errors
- Verify bucket exists and is accessible
- Check service account has `storage.admin` role
- Ensure bucket is in the correct region

### Vertex AI Errors
- Verify `aiplatform.googleapis.com` is enabled
- Check quota limits in GCP Console
- Ensure service account has `aiplatform.user` role

## Next Steps

After completing this setup:
1. Run database migrations: `alembic upgrade head`
2. Start the development environment: `docker-compose up`
3. Access the application at `http://localhost:3000`
