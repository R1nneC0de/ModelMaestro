import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  Alert,
  Snackbar,
  IconButton,
  Chip,
  Divider,
  LinearProgress
} from '@mui/material';
import {
  ContentCopy as ContentCopyIcon,
  Download as DownloadIcon,
  CheckCircle as CheckCircleIcon,
  Link as LinkIcon
} from '@mui/icons-material';
import { modelApi } from '../../services/api';

interface APIDisplayProps {
  modelId: string;
  endpointUrl?: string;
  artifactPath?: string;
}

/**
 * APIDisplay Component
 * 
 * Displays API endpoint information and model download functionality:
 * - API endpoint URL with copy-to-clipboard
 * - Model artifact download with progress
 * - Connection status indicators
 * - Usage instructions
 */
export default function APIDisplay({ modelId, endpointUrl, artifactPath }: APIDisplayProps) {
  const [copySuccess, setCopySuccess] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleCopyEndpoint = async () => {
    if (!endpointUrl) return;
    
    try {
      await navigator.clipboard.writeText(endpointUrl);
      setCopySuccess(true);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleCopyModelId = async () => {
    try {
      await navigator.clipboard.writeText(modelId);
      setCopySuccess(true);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = async () => {
    setDownloading(true);
    setDownloadError(null);

    try {
      const blob = await modelApi.downloadModel(modelId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `model_${modelId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      setDownloadError(err instanceof Error ? err.message : 'Download failed');
    } finally {
      setDownloading(false);
    }
  };

  const handleCloseCopySnackbar = () => {
    setCopySuccess(false);
  };

  return (
    <Box>
      {/* Model Download Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" mb={2}>
          <DownloadIcon color="primary" />
          <Typography variant="h6">
            Download Model Artifacts
          </Typography>
        </Stack>

        <Typography variant="body2" color="text.secondary" paragraph>
          Download the trained model artifacts for local deployment or integration into your application.
          The download includes the model file, preprocessing artifacts, and metadata.
        </Typography>

        {artifactPath ? (
          <Box>
            <Stack direction="row" spacing={2} alignItems="center" mb={2}>
              <Chip
                icon={<CheckCircleIcon />}
                label="Artifacts Available"
                color="success"
                size="small"
              />
              <Typography variant="caption" color="text.secondary">
                {artifactPath}
              </Typography>
            </Stack>

            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
              disabled={downloading}
              fullWidth
            >
              {downloading ? 'Downloading...' : 'Download Model Package'}
            </Button>

            {downloading && (
              <Box mt={2}>
                <LinearProgress />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Preparing download...
                </Typography>
              </Box>
            )}

            {downloadError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {downloadError}
              </Alert>
            )}
          </Box>
        ) : (
          <Alert severity="warning">
            Model artifacts are not available for download. The model may still be training or deployment failed.
          </Alert>
        )}
      </Paper>

      <Divider sx={{ my: 3 }} />

      {/* API Endpoint Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" mb={2}>
          <LinkIcon color="primary" />
          <Typography variant="h6">
            API Endpoint
          </Typography>
        </Stack>

        <Typography variant="body2" color="text.secondary" paragraph>
          Use this endpoint to make real-time predictions via REST API. The endpoint is hosted on
          Google Cloud Vertex AI and provides low-latency inference.
        </Typography>

        {endpointUrl ? (
          <Box>
            <Stack direction="row" spacing={2} alignItems="center" mb={2}>
              <Chip
                icon={<CheckCircleIcon />}
                label="Endpoint Active"
                color="success"
                size="small"
              />
            </Stack>

            <TextField
              fullWidth
              value={endpointUrl}
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <IconButton onClick={handleCopyEndpoint} edge="end">
                    <ContentCopyIcon />
                  </IconButton>
                )
              }}
              sx={{ mb: 2 }}
            />

            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Note:</strong> This endpoint requires authentication with Google Cloud credentials.
                See the code examples tab for implementation details.
              </Typography>
            </Alert>
          </Box>
        ) : (
          <Alert severity="warning">
            Model is not deployed to an API endpoint. You can still download the model artifacts
            for local deployment.
          </Alert>
        )}
      </Paper>

      {/* Model ID Section */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Model Identifier
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          Use this ID to reference the model in API calls and tracking systems.
        </Typography>

        <TextField
          fullWidth
          value={modelId}
          InputProps={{
            readOnly: true,
            endAdornment: (
              <IconButton onClick={handleCopyModelId} edge="end">
                <ContentCopyIcon />
              </IconButton>
            )
          }}
        />
      </Paper>

      {/* Copy Success Snackbar */}
      <Snackbar
        open={copySuccess}
        autoHideDuration={2000}
        onClose={handleCloseCopySnackbar}
        message="Copied to clipboard"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
}
