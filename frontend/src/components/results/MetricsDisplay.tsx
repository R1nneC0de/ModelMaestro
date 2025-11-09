import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Chip,
  Stack,
  Divider
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { ModelMetrics } from '../../types';

interface MetricsDisplayProps {
  metrics: ModelMetrics;
  architecture: string;
  report?: {
    decision: 'ACCEPT' | 'REJECT';
    reasoning?: string;
    recommendations?: string[];
  };
}

interface MetricCardProps {
  name: string;
  value: number;
  description?: string;
  threshold?: number;
  higherIsBetter?: boolean;
}

/**
 * MetricCard Component
 * 
 * Displays a single metric with visual indicators
 */
function MetricCard({ name, value, description, threshold, higherIsBetter = true }: MetricCardProps) {
  const percentage = value * 100;
  const meetsThreshold = threshold !== undefined
    ? (higherIsBetter ? value >= threshold : value <= threshold)
    : true;

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Stack spacing={1}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="subtitle2" color="text.secondary">
            {name}
          </Typography>
          {threshold !== undefined && (
            meetsThreshold ? (
              <TrendingUpIcon color="success" fontSize="small" />
            ) : (
              <TrendingDownIcon color="error" fontSize="small" />
            )
          )}
        </Stack>

        <Typography variant="h4" component="div">
          {value.toFixed(4)}
        </Typography>

        {threshold !== undefined && (
          <Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(percentage, 100)}
              color={meetsThreshold ? 'success' : 'error'}
              sx={{ height: 8, borderRadius: 1 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              Threshold: {threshold.toFixed(4)}
            </Typography>
          </Box>
        )}

        {description && (
          <Typography variant="caption" color="text.secondary">
            {description}
          </Typography>
        )}
      </Stack>
    </Paper>
  );
}

/**
 * MetricsDisplay Component
 * 
 * Comprehensive visualization of model performance metrics including:
 * - Key metric cards with visual indicators
 * - Detailed metrics table
 * - Threshold comparisons
 * - Performance recommendations
 */
export default function MetricsDisplay({ metrics, architecture, report }: MetricsDisplayProps) {
  // Determine problem type from architecture
  const isClassification = architecture.toLowerCase().includes('classification') || 
                          architecture.toLowerCase().includes('clf');
  const isRegression = architecture.toLowerCase().includes('regression') || 
                      architecture.toLowerCase().includes('reg');

  // Define metric configurations based on problem type
  const getMetricConfig = () => {
    if (isClassification) {
      return [
        {
          key: 'roc_auc',
          name: 'ROC AUC',
          description: 'Area under the ROC curve',
          threshold: 0.70,
          higherIsBetter: true
        },
        {
          key: 'accuracy',
          name: 'Accuracy',
          description: 'Overall prediction accuracy',
          threshold: 0.60,
          higherIsBetter: true
        },
        {
          key: 'precision',
          name: 'Precision',
          description: 'Positive predictive value',
          threshold: 0.50,
          higherIsBetter: true
        },
        {
          key: 'recall',
          name: 'Recall',
          description: 'True positive rate',
          threshold: 0.50,
          higherIsBetter: true
        },
        {
          key: 'f1_score',
          name: 'F1 Score',
          description: 'Harmonic mean of precision and recall',
          threshold: 0.60,
          higherIsBetter: true
        }
      ];
    } else if (isRegression) {
      return [
        {
          key: 'rmse',
          name: 'RMSE',
          description: 'Root mean squared error',
          higherIsBetter: false
        },
        {
          key: 'mae',
          name: 'MAE',
          description: 'Mean absolute error',
          higherIsBetter: false
        },
        {
          key: 'r2',
          name: 'R² Score',
          description: 'Coefficient of determination',
          threshold: 0.10,
          higherIsBetter: true
        },
        {
          key: 'mse',
          name: 'MSE',
          description: 'Mean squared error',
          higherIsBetter: false
        }
      ];
    }
    return [];
  };

  const metricConfigs = getMetricConfig();
  
  // Get primary metrics for cards
  const primaryMetrics = metricConfigs.slice(0, 4);
  
  // Get all metrics for table
  const allMetricEntries = Object.entries(metrics).map(([key, value]) => ({
    key,
    name: key.replace(/_/g, ' ').toUpperCase(),
    value
  }));

  return (
    <Box>
      {/* Key Metrics Cards */}
      <Typography variant="h6" gutterBottom>
        Key Performance Metrics
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {primaryMetrics.map((config) => {
          const value = metrics[config.key];
          if (value === undefined) return null;
          
          return (
            <Grid item xs={12} sm={6} md={3} key={config.key}>
              <MetricCard
                name={config.name}
                value={value}
                description={config.description}
                threshold={config.threshold}
                higherIsBetter={config.higherIsBetter}
              />
            </Grid>
          );
        })}
      </Grid>

      {/* Decision Summary */}
      {report && (
        <Paper sx={{ p: 2, mb: 4, bgcolor: report.decision === 'ACCEPT' ? 'success.light' : 'error.light' }}>
          <Stack direction="row" spacing={2} alignItems="center" mb={1}>
            <Chip
              label={report.decision}
              color={report.decision === 'ACCEPT' ? 'success' : 'error'}
              size="small"
            />
            <Typography variant="subtitle1" fontWeight="bold">
              Model Evaluation Decision
            </Typography>
          </Stack>
          
          {report.reasoning && (
            <Typography variant="body2" paragraph>
              {report.reasoning}
            </Typography>
          )}

          {report.recommendations && report.recommendations.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Recommendations:
              </Typography>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {report.recommendations.map((rec, idx) => (
                  <li key={idx}>
                    <Typography variant="body2">{rec}</Typography>
                  </li>
                ))}
              </ul>
            </Box>
          )}
        </Paper>
      )}

      <Divider sx={{ my: 3 }} />

      {/* Detailed Metrics Table */}
      <Typography variant="h6" gutterBottom>
        All Metrics
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Metric</strong></TableCell>
              <TableCell align="right"><strong>Value</strong></TableCell>
              <TableCell><strong>Description</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {allMetricEntries.map((metric) => {
              const config = metricConfigs.find(c => c.key === metric.key);
              
              return (
                <TableRow key={metric.key} hover>
                  <TableCell component="th" scope="row">
                    {metric.name}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="medium">
                      {metric.value.toFixed(4)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {config?.description || '-'}
                    </Typography>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Metric Interpretation Guide */}
      <Paper sx={{ p: 2, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2" gutterBottom>
          Metric Interpretation Guide
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {isClassification && (
            <>
              <strong>Classification Metrics:</strong> Higher values indicate better performance. 
              ROC AUC measures the model's ability to distinguish between classes. 
              Precision indicates how many predicted positives are actually positive. 
              Recall measures how many actual positives were correctly identified.
            </>
          )}
          {isRegression && (
            <>
              <strong>Regression Metrics:</strong> For RMSE and MAE, lower values indicate better performance. 
              R² Score ranges from 0 to 1, with higher values indicating better fit. 
              An R² of 0.10 means the model explains 10% of the variance in the target variable.
            </>
          )}
        </Typography>
      </Paper>
    </Box>
  );
}
