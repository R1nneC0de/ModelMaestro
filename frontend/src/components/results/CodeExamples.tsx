import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Snackbar,
  Alert,
  Stack
} from '@mui/material';
import {
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

interface CodeExamplesProps {
  modelId: string;
  endpointUrl?: string;
  architecture: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`code-tabpanel-${index}`}
      aria-labelledby={`code-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

interface CodeBlockProps {
  code: string;
}

function CodeBlock({ code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <Box sx={{ position: 'relative' }}>
      <Paper
        sx={{
          p: 2,
          bgcolor: 'grey.900',
          color: 'grey.100',
          fontFamily: 'monospace',
          fontSize: '0.875rem',
          overflow: 'auto',
          maxHeight: '500px'
        }}
      >
        <IconButton
          onClick={handleCopy}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            color: 'grey.400',
            '&:hover': { color: 'grey.100' }
          }}
          size="small"
        >
          {copied ? <CheckCircleIcon /> : <ContentCopyIcon />}
        </IconButton>
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {code}
        </pre>
      </Paper>
      <Snackbar
        open={copied}
        autoHideDuration={2000}
        onClose={() => setCopied(false)}
        message="Code copied to clipboard"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
}

/**
 * CodeExamples Component
 * 
 * Provides ready-to-use code examples for model integration:
 * - Python example using Google Cloud AI Platform SDK
 * - JavaScript/Node.js example
 * - REST API curl example
 * - Includes syntax highlighting and copy-to-clipboard
 */
export default function CodeExamples({ modelId, endpointUrl }: CodeExamplesProps) {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Generate Python example
  const pythonExample = `# Install required packages
# pip install google-cloud-aiplatform

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

# Initialize Vertex AI
aiplatform.init(
    project="YOUR_PROJECT_ID",
    location="YOUR_LOCATION"
)

# Get the endpoint
endpoint = aiplatform.Endpoint(
    endpoint_name="${endpointUrl || 'YOUR_ENDPOINT_URL'}"
)

# Prepare your input data
# Example for tabular data:
instances = [
    {
        "feature1": 1.0,
        "feature2": "value",
        "feature3": 3
    }
]

# Make prediction
predictions = endpoint.predict(instances=instances)

# Process results
for prediction in predictions.predictions:
    print(f"Prediction: {prediction}")
    if 'classes' in prediction:
        print(f"Predicted class: {prediction['classes'][0]}")
        print(f"Confidence: {prediction['scores'][0]}")
    else:
        print(f"Predicted value: {prediction['value']}")

# Batch prediction example
batch_prediction_job = aiplatform.BatchPredictionJob.create(
    job_display_name="batch_prediction_${modelId}",
    model_name="${modelId}",
    instances_format="csv",
    predictions_format="jsonl",
    gcs_source="gs://your-bucket/input.csv",
    gcs_destination_prefix="gs://your-bucket/output/"
)

# Wait for completion
batch_prediction_job.wait()
print(f"Batch prediction completed: {batch_prediction_job.resource_name}")
`;

  // Generate JavaScript example
  const javascriptExample = `// Install required packages
// npm install @google-cloud/aiplatform

const aiplatform = require('@google-cloud/aiplatform');
const { PredictionServiceClient } = aiplatform.v1;

// Initialize client
const client = new PredictionServiceClient({
  apiEndpoint: 'YOUR_LOCATION-aiplatform.googleapis.com'
});

// Prepare prediction request
const endpoint = '${endpointUrl || 'YOUR_ENDPOINT_URL'}';

const instances = [
  {
    feature1: 1.0,
    feature2: 'value',
    feature3: 3
  }
];

// Convert instances to protobuf Value format
const instancesValue = instances.map(instance => {
  return { structValue: { fields: instance } };
});

// Make prediction
async function predict() {
  try {
    const [response] = await client.predict({
      endpoint: endpoint,
      instances: instancesValue
    });

    console.log('Predictions:');
    for (const prediction of response.predictions) {
      console.log(JSON.stringify(prediction, null, 2));
    }

    return response.predictions;
  } catch (error) {
    console.error('Prediction failed:', error);
    throw error;
  }
}

// Execute prediction
predict()
  .then(predictions => {
    console.log('Success!');
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Using fetch API (browser/Node.js with node-fetch)
async function predictWithFetch() {
  const response = await fetch('${endpointUrl || 'YOUR_ENDPOINT_URL'}:predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
    },
    body: JSON.stringify({
      instances: instances
    })
  });

  const data = await response.json();
  console.log('Predictions:', data.predictions);
  return data;
}
`;

  // Generate REST API example
  const restExample = `# Using curl to make predictions

# Set your variables
PROJECT_ID="YOUR_PROJECT_ID"
LOCATION="YOUR_LOCATION"
ENDPOINT_ID="${modelId}"
ACCESS_TOKEN=$(gcloud auth print-access-token)

# Prepare input data (save as input.json)
cat > input.json << EOF
{
  "instances": [
    {
      "feature1": 1.0,
      "feature2": "value",
      "feature3": 3
    }
  ]
}
EOF

# Make prediction request
curl -X POST \\
  -H "Authorization: Bearer \${ACCESS_TOKEN}" \\
  -H "Content-Type: application/json" \\
  "${endpointUrl || 'https://YOUR_LOCATION-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/endpoints/YOUR_ENDPOINT_ID'}:predict" \\
  -d @input.json

# Example response:
# {
#   "predictions": [
#     {
#       "classes": ["No", "Yes"],
#       "scores": [0.7, 0.3],
#       "predicted_class": "No",
#       "confidence": 0.7
#     }
#   ],
#   "deployedModelId": "1234567890",
#   "model": "projects/.../models/${modelId}"
# }

# Batch prediction using REST API
cat > batch_request.json << EOF
{
  "inputConfig": {
    "instancesFormat": "csv",
    "gcsSource": {
      "uris": ["gs://your-bucket/input.csv"]
    }
  },
  "outputConfig": {
    "predictionsFormat": "jsonl",
    "gcsDestination": {
      "outputUriPrefix": "gs://your-bucket/output/"
    }
  }
}
EOF

curl -X POST \\
  -H "Authorization: Bearer \${ACCESS_TOKEN}" \\
  -H "Content-Type: application/json" \\
  "https://\${LOCATION}-aiplatform.googleapis.com/v1/projects/\${PROJECT_ID}/locations/\${LOCATION}/batchPredictionJobs" \\
  -d @batch_request.json
`;

  return (
    <Box>
      <Stack spacing={2} mb={3}>
        <Typography variant="h6">
          Integration Code Examples
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Use these examples to integrate the trained model into your application. 
          Replace placeholder values with your actual project configuration.
        </Typography>
      </Stack>

      {!endpointUrl && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Model is not deployed to an endpoint. These examples show the general pattern,
          but you'll need to deploy the model first or use the downloaded artifacts for local inference.
        </Alert>
      )}

      <Paper>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="code examples tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Python" id="code-tab-0" />
          <Tab label="JavaScript" id="code-tab-1" />
          <Tab label="REST API" id="code-tab-2" />
        </Tabs>

        <Box px={3}>
          <TabPanel value={activeTab} index={0}>
            <Typography variant="subtitle2" gutterBottom>
              Python Example using Google Cloud AI Platform SDK
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              This example shows how to make predictions using the Python SDK. 
              Install the required package and authenticate with your Google Cloud credentials.
            </Typography>
            <CodeBlock code={pythonExample} />
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <Typography variant="subtitle2" gutterBottom>
              JavaScript/Node.js Example
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Use this example for Node.js applications or browser-based implementations.
              Requires authentication with Google Cloud credentials.
            </Typography>
            <CodeBlock code={javascriptExample} />
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <Typography variant="subtitle2" gutterBottom>
              REST API Example using curl
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Direct REST API calls using curl. This approach works with any programming language
              that can make HTTP requests.
            </Typography>
            <CodeBlock code={restExample} />
          </TabPanel>
        </Box>
      </Paper>

      {/* Additional Resources */}
      <Paper sx={{ p: 2, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2" gutterBottom>
          Additional Resources
        </Typography>
        <Typography variant="body2" color="text.secondary" component="div">
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>
              <a 
                href="https://cloud.google.com/vertex-ai/docs/predictions/get-predictions" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                Vertex AI Prediction Documentation
              </a>
            </li>
            <li>
              <a 
                href="https://cloud.google.com/vertex-ai/docs/reference/rest" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                Vertex AI REST API Reference
              </a>
            </li>
            <li>
              <a 
                href="https://cloud.google.com/python/docs/reference/aiplatform/latest" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                Python SDK Documentation
              </a>
            </li>
          </ul>
        </Typography>
      </Paper>
    </Box>
  );
}
