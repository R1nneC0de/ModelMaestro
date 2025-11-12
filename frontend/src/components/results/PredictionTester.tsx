import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Grid,
  IconButton
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Clear as ClearIcon,
  Add as AddIcon,
  Remove as RemoveIcon
} from '@mui/icons-material';
import { modelApi } from '../../services/api';
import { PredictionRequest, PredictionResponse } from '../../types';

interface PredictionTesterProps {
  modelId: string;
  endpointUrl?: string;
  architecture: string;
}

interface FeatureInput {
  name: string;
  value: string;
}

/**
 * PredictionTester Component
 * 
 * Interactive interface for testing model predictions:
 * - Dynamic feature input fields
 * - Real-time prediction execution
 * - Result visualization
 * - Support for multiple instances
 * - Error handling and validation
 */
export default function PredictionTester({ modelId, endpointUrl, architecture }: PredictionTesterProps) {
  const [features, setFeatures] = useState<FeatureInput[]>([
    { name: '', value: '' }
  ]);
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isClassification = architecture.toLowerCase().includes('classification') || 
                          architecture.toLowerCase().includes('clf');

  const handleAddFeature = () => {
    setFeatures([...features, { name: '', value: '' }]);
  };

  const handleRemoveFeature = (index: number) => {
    if (features.length > 1) {
      setFeatures(features.filter((_, i) => i !== index));
    }
  };

  const handleFeatureChange = (index: number, field: 'name' | 'value', value: string) => {
    const newFeatures = [...features];
    newFeatures[index][field] = value;
    setFeatures(newFeatures);
  };

  const handleClear = () => {
    setFeatures([{ name: '', value: '' }]);
    setPrediction(null);
    setError(null);
  };

  const handlePredict = async () => {
    // Validate inputs
    const validFeatures = features.filter(f => f.name.trim() && f.value.trim());
    
    if (validFeatures.length === 0) {
      setError('Please add at least one feature with name and value');
      return;
    }

    // Build instance object
    const instance: Record<string, any> = {};
    validFeatures.forEach(feature => {
      // Try to parse as number, otherwise keep as string
      const numValue = parseFloat(feature.value);
      instance[feature.name] = isNaN(numValue) ? feature.value : numValue;
    });

    const request: PredictionRequest = {
      instances: [instance]
    };

    setPredicting(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await modelApi.predict(modelId, request);
      setPrediction(result);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(err instanceof Error ? err.message : 'Prediction failed');
    } finally {
      setPredicting(false);
    }
  };

  const loadSampleData = () => {
    // Load sample data based on architecture
    if (isClassification) {
      setFeatures([
        { name: 'tenure', value: '12' },
        { name: 'monthly_charges', value: '50.5' },
        { name: 'total_charges', value: '606.0' },
        { name: 'contract', value: 'Month-to-month' }
      ]);
    } else {
      setFeatures([
        { name: 'feature1', value: '1.5' },
        { name: 'feature2', value: '2.3' },
        { name: 'feature3', value: '0.8' }
      ]);
    }
  };

  return (
    <Box>
      <Stack spacing={2} mb={3}>
        <Typography variant="h6">
          Test Model Predictions
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter feature values to test the model's predictions in real-time.
          Add or remove features as needed to match your data schema.
        </Typography>
      </Stack>

      {!endpointUrl && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Model is not deployed to an endpoint. Deploy the model first to test predictions.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1" fontWeight="bold">
                Input Features
              </Typography>
              <Stack direction="row" spacing={1}>
                <Button
                  size="small"
                  onClick={loadSampleData}
                  variant="outlined"
                >
                  Load Sample
                </Button>
                <Button
                  size="small"
                  onClick={handleClear}
                  startIcon={<ClearIcon />}
                  variant="outlined"
                >
                  Clear
                </Button>
              </Stack>
            </Stack>

            <Stack spacing={2}>
              {features.map((feature, index) => (
                <Stack key={index} direction="row" spacing={1} alignItems="center">
                  <TextField
                    label="Feature Name"
                    value={feature.name}
                    onChange={(e) => handleFeatureChange(index, 'name', e.target.value)}
                    size="small"
                    fullWidth
                    placeholder="e.g., age, income"
                  />
                  <TextField
                    label="Value"
                    value={feature.value}
                    onChange={(e) => handleFeatureChange(index, 'value', e.target.value)}
                    size="small"
                    fullWidth
                    placeholder="e.g., 25, high"
                  />
                  <IconButton
                    onClick={() => handleRemoveFeature(index)}
                    disabled={features.length === 1}
                    size="small"
                  >
                    <RemoveIcon />
                  </IconButton>
                </Stack>
              ))}

              <Button
                startIcon={<AddIcon />}
                onClick={handleAddFeature}
                variant="outlined"
                fullWidth
              >
                Add Feature
              </Button>
            </Stack>

            <Divider sx={{ my: 3 }} />

            <Button
              variant="contained"
              startIcon={predicting ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              onClick={handlePredict}
              disabled={predicting || !endpointUrl}
              fullWidth
              size="large"
            >
              {predicting ? 'Predicting...' : 'Run Prediction'}
            </Button>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, minHeight: '400px' }}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Prediction Results
            </Typography>

            {!prediction && !error && (
              <Box
                display="flex"
                alignItems="center"
                justifyContent="center"
                minHeight="300px"
              >
                <Typography variant="body2" color="text.secondary">
                  Results will appear here after running a prediction
                </Typography>
              </Box>
            )}

            {prediction && prediction.predictions && prediction.predictions.length > 0 && (
              <Box>
                {prediction.predictions.map((pred, idx) => (
                  <Box key={idx} mb={3}>
                    <Stack spacing={3}>
                      {/* Classification Results */}
                      {pred.classes && pred.scores && (
                        <Box>
                          {/* Main Prediction Card */}
                          <Paper
                            elevation={0}
                            sx={{
                              p: 3,
                              mb: 3,
                              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                              color: 'white',
                              borderRadius: 3
                            }}
                          >
                            <Typography variant="overline" sx={{ opacity: 0.9, letterSpacing: 1 }}>
                              Prediction Result
                            </Typography>
                            <Typography variant="h3" fontWeight="bold" sx={{ my: 1 }}>
                              {pred.predicted_class || pred.classes[0]}
                            </Typography>
                            <Stack direction="row" spacing={2} alignItems="center">
                              <Typography variant="h5" sx={{ opacity: 0.95 }}>
                                {((pred.confidence || pred.scores[0]) * 100).toFixed(1)}%
                              </Typography>
                              <Chip
                                label="Confidence"
                                size="small"
                                sx={{
                                  bgcolor: 'rgba(255,255,255,0.2)',
                                  color: 'white',
                                  fontWeight: 'bold'
                                }}
                              />
                            </Stack>
                          </Paper>

                          {/* Probability Distribution */}
                          <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mb: 2 }}>
                            Probability Distribution
                          </Typography>
                          <Stack spacing={2}>
                            {pred.classes.map((cls: string, i: number) => {
                              const score = pred.scores[i];
                              const isTopPrediction = i === 0 || score === Math.max(...pred.scores);
                              
                              return (
                                <Paper
                                  key={i}
                                  elevation={isTopPrediction ? 2 : 0}
                                  sx={{
                                    p: 2,
                                    bgcolor: isTopPrediction ? 'primary.50' : 'grey.50',
                                    border: isTopPrediction ? '2px solid' : '1px solid',
                                    borderColor: isTopPrediction ? 'primary.main' : 'grey.200',
                                    borderRadius: 2,
                                    transition: 'all 0.2s ease'
                                  }}
                                >
                                  <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                                    <Stack direction="row" spacing={1} alignItems="center">
                                      <Typography
                                        variant="body1"
                                        fontWeight={isTopPrediction ? 'bold' : 'medium'}
                                      >
                                        {cls}
                                      </Typography>
                                      {isTopPrediction && (
                                        <Chip
                                          label="Predicted"
                                          size="small"
                                          color="primary"
                                          sx={{ height: 20, fontSize: '0.7rem' }}
                                        />
                                      )}
                                    </Stack>
                                    <Typography
                                      variant="h6"
                                      fontWeight="bold"
                                      color={isTopPrediction ? 'primary.main' : 'text.secondary'}
                                    >
                                      {(score * 100).toFixed(1)}%
                                    </Typography>
                                  </Stack>
                                  <Box
                                    sx={{
                                      width: '100%',
                                      height: 12,
                                      bgcolor: 'grey.200',
                                      borderRadius: 2,
                                      overflow: 'hidden',
                                      position: 'relative'
                                    }}
                                  >
                                    <Box
                                      sx={{
                                        width: `${score * 100}%`,
                                        height: '100%',
                                        background: isTopPrediction
                                          ? 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)'
                                          : 'linear-gradient(90deg, #a8b3cf 0%, #c8d0e7 100%)',
                                        transition: 'width 0.5s ease',
                                        boxShadow: isTopPrediction ? '0 2px 8px rgba(102, 126, 234, 0.4)' : 'none'
                                      }}
                                    />
                                  </Box>
                                </Paper>
                              );
                            })}
                          </Stack>
                        </Box>
                      )}

                      {/* Regression Results */}
                      {pred.value !== undefined && (
                        <Paper
                          elevation={0}
                          sx={{
                            p: 3,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            color: 'white',
                            borderRadius: 3
                          }}
                        >
                          <Typography variant="overline" sx={{ opacity: 0.9, letterSpacing: 1 }}>
                            Predicted Value
                          </Typography>
                          <Typography variant="h3" fontWeight="bold" sx={{ mt: 1 }}>
                            {typeof pred.value === 'number' ? pred.value.toFixed(4) : pred.value}
                          </Typography>
                        </Paper>
                      )}

                      {/* Raw Prediction Data - Collapsible */}
                      <Box>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          Technical Details
                        </Typography>
                        <Paper
                          sx={{
                            p: 2,
                            bgcolor: 'grey.900',
                            color: 'grey.100',
                            maxHeight: '150px',
                            overflow: 'auto',
                            borderRadius: 2,
                            fontFamily: 'monospace'
                          }}
                        >
                          <pre style={{ margin: 0, fontSize: '0.7rem', lineHeight: 1.4 }}>
                            {JSON.stringify(pred, null, 2)}
                          </pre>
                        </Paper>
                      </Box>
                    </Stack>
                  </Box>
                ))}

                {/* Metadata Footer */}
                <Divider sx={{ my: 3 }} />
                <Stack spacing={0.5}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="caption" color="text.secondary" fontWeight="bold">
                      Model ID:
                    </Typography>
                    <Typography variant="caption" color="text.primary">
                      {prediction.model_id}
                    </Typography>
                  </Stack>
                  {prediction.endpoint_id && (
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="caption" color="text.secondary" fontWeight="bold">
                        Endpoint ID:
                      </Typography>
                      <Typography variant="caption" color="text.primary">
                        {prediction.endpoint_id}
                      </Typography>
                    </Stack>
                  )}
                </Stack>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Usage Tips */}
      <Paper sx={{ p: 2, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2" gutterBottom>
          Usage Tips
        </Typography>
        <Typography variant="body2" color="text.secondary" component="div">
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>Feature names should match the column names used during training</li>
            <li>Numeric values will be automatically parsed as numbers</li>
            <li>String values will be kept as text (useful for categorical features)</li>
            <li>Use "Load Sample" to populate with example data</li>
            <li>The model expects features in the same format as the training data</li>
          </ul>
        </Typography>
      </Paper>
    </Box>
  );
}
