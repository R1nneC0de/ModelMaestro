#!/bin/bash

# Deploy a trained AutoML model to Vertex AI Endpoint using gcloud CLI
# This is often more reliable than the Python API

set -e

# Configuration
PROJECT_ID="agentic-workflow-477603"
REGION="us-central1"
MODEL_ID="7575049075679035392"  # Latest trained model
MODEL_DISPLAY_NAME="model_churn_test_20251108_183410"
ENDPOINT_DISPLAY_NAME="churn_prediction_endpoint"

echo "================================"
echo "Deploying Model to Vertex AI"
echo "================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Model ID: $MODEL_ID"
echo ""

# Step 1: Create endpoint (if doesn't exist)
echo "Step 1: Creating endpoint..."
ENDPOINT_ID=$(gcloud ai endpoints create \
  --region=$REGION \
  --display-name=$ENDPOINT_DISPLAY_NAME \
  --project=$PROJECT_ID \
  --format="value(name)" 2>/dev/null || echo "")

if [ -z "$ENDPOINT_ID" ]; then
  echo "Endpoint might already exist, listing endpoints..."
  gcloud ai endpoints list --region=$REGION --project=$PROJECT_ID
  
  # Try to get existing endpoint
  ENDPOINT_ID=$(gcloud ai endpoints list \
    --region=$REGION \
    --project=$PROJECT_ID \
    --filter="displayName:$ENDPOINT_DISPLAY_NAME" \
    --format="value(name)" | head -1)
  
  if [ -z "$ENDPOINT_ID" ]; then
    echo "ERROR: Could not create or find endpoint"
    exit 1
  fi
  echo "Using existing endpoint: $ENDPOINT_ID"
else
  echo "Created new endpoint: $ENDPOINT_ID"
fi

# Extract just the endpoint ID number
ENDPOINT_NUM=$(echo $ENDPOINT_ID | grep -oE '[0-9]+$')
echo "Endpoint number: $ENDPOINT_NUM"

# Step 2: Deploy model to endpoint
echo ""
echo "Step 2: Deploying model to endpoint..."
echo "This will take 10-20 minutes..."
echo ""

gcloud ai endpoints deploy-model $ENDPOINT_NUM \
  --region=$REGION \
  --project=$PROJECT_ID \
  --model=$MODEL_ID \
  --display-name="${MODEL_DISPLAY_NAME}_deployment" \
  --machine-type=n1-standard-2 \
  --min-replica-count=1 \
  --max-replica-count=1 \
  --traffic-split=0=100

echo ""
echo "================================"
echo "Deployment Complete!"
echo "================================"
echo "Endpoint ID: $ENDPOINT_NUM"
echo "Full resource name: projects/$PROJECT_ID/locations/$REGION/endpoints/$ENDPOINT_NUM"
echo ""
echo "You can now make predictions using:"
echo "  python3 backend/test_prediction_api.py"
