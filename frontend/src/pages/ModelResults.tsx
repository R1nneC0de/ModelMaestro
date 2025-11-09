import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Container,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Button,
  Tabs,
  Tab,
  Divider,
  Chip,
  Stack
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { modelApi } from '../services/api';
import { ModelInfo } from '../types';
import MetricsDisplay from '../components/results/MetricsDisplay';
import APIDisplay from '../components/results/APIDisplay';
import CodeExamples from '../components/results/CodeExamples';
import PredictionTester from '../components/results/PredictionTester';

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
      id={`model-results-tabpanel-${index}`}
      aria-labelledby={`model-results-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

/**
 * ModelResults Page Component
 * 
 * Displays comprehensive model results including:
 * - Model metadata and status
 * - Performance metrics visualization
 * - Download and API access options
 * - Code examples for integration
 * - Interactive prediction testing
 */
export default function ModelResults() {
  const { modelId } = useParams<{ modelId: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);

  // Fetch model data
  const {
    data: modelData,
    isLoading,
    error,
    refetch
  } = useQuery<ModelInfo>({
    queryKey: ['model', modelId],
    queryFn: () => modelApi.getModel(modelId!),
    enabled: !!modelId,
    retry: 2,
    staleTime: 30000 // 30 seconds
  });

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleBack = () => {
    navigate(-1);
  };

  const handleDownload = async () => {
    if (!modelId) return;
    
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
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={() => refetch()}>
              Retry
            </Button>
          }
        >
          Failed to load model results: {error instanceof Error ? error.message : 'Unknown error'}
        </Alert>
        <Box mt={2}>
          <Button startIcon={<ArrowBackIcon />} onClick={handleBack}>
            Go Back
          </Button>
        </Box>
      </Container>
    );
  }

  if (!modelData) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">Model not found</Alert>
        <Box mt={2}>
          <Button startIcon={<ArrowBackIcon />} onClick={handleBack}>
            Go Back
          </Button>
        </Box>
      </Container>
    );
  }

  const isAccepted = modelData.report?.decision === 'ACCEPT';

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mb: 2 }}
        >
          Back
        </Button>
        
        <Paper sx={{ p: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center" mb={2}>
            <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
              Model Results
            </Typography>
            {isAccepted ? (
              <Chip
                icon={<CheckCircleIcon />}
                label="Accepted"
                color="success"
                size="medium"
              />
            ) : (
              <Chip
                icon={<ErrorIcon />}
                label="Rejected"
                color="error"
                size="medium"
              />
            )}
          </Stack>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            Model ID: {modelData.id}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Architecture: {modelData.architecture}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Created: {new Date(modelData.created_at).toLocaleString()}
          </Typography>

          {modelData.report && (
            <Box mt={2}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body1" paragraph>
                {modelData.report.summary}
              </Typography>
              {modelData.report.reasoning && (
                <Typography variant="body2" color="text.secondary">
                  {modelData.report.reasoning}
                </Typography>
              )}
            </Box>
          )}

          <Box mt={3}>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
              disabled={!modelData.artifact_path}
            >
              Download Model
            </Button>
          </Box>
        </Paper>
      </Box>

      {/* Tabs */}
      <Paper>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="model results tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Metrics" id="model-results-tab-0" />
          <Tab label="API & Integration" id="model-results-tab-1" />
          <Tab label="Code Examples" id="model-results-tab-2" />
          <Tab label="Test Predictions" id="model-results-tab-3" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          <Box px={3}>
            <MetricsDisplay
              metrics={modelData.metrics}
              architecture={modelData.architecture}
              report={modelData.report}
            />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <Box px={3}>
            <APIDisplay
              modelId={modelData.id}
              endpointUrl={modelData.endpoint_url}
              artifactPath={modelData.artifact_path}
            />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Box px={3}>
            <CodeExamples
              modelId={modelData.id}
              endpointUrl={modelData.endpoint_url}
              architecture={modelData.architecture}
            />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Box px={3}>
            <PredictionTester
              modelId={modelData.id}
              endpointUrl={modelData.endpoint_url}
              architecture={modelData.architecture}
            />
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
}
