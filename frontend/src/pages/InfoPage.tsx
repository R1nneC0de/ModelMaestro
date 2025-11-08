import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SpeedIcon from '@mui/icons-material/Speed';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import StorageIcon from '@mui/icons-material/Storage';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

export function InfoPage() {
  return (
    <Box>
      <Typography 
        variant="h4" 
        gutterBottom 
        sx={{ 
          fontWeight: 600, 
          mb: { xs: 2, sm: 3 },
          fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' }
        }}
      >
        About the Platform
      </Typography>

      {/* Platform Description */}
      <Paper sx={{ p: { xs: 2, sm: 3, md: 4 }, mb: { xs: 2, sm: 3 } }}>
        <Typography 
          variant="h6" 
          gutterBottom 
          sx={{ 
            fontWeight: 600, 
            color: 'primary.main',
            fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
          }}
        >
          What is this?
        </Typography>
        <Typography 
          paragraph 
          sx={{ 
            fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }, 
            lineHeight: 1.7 
          }}
        >
          An AI-powered platform that automatically trains machine learning models from your data. 
          Just upload your dataset and describe what you want to learn - our intelligent agent 
          handles everything from data analysis to model selection and training.
        </Typography>
        <Typography 
          sx={{ 
            fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }, 
            lineHeight: 1.7 
          }}
        >
          Built with Google Cloud Vertex AI and powered by advanced AI reasoning, this platform 
          makes machine learning accessible to everyone, regardless of technical expertise.
        </Typography>
      </Paper>

      {/* Usage Instructions */}
      <Paper sx={{ p: { xs: 2, sm: 3, md: 4 }, mb: { xs: 2, sm: 3 } }}>
        <Typography 
          variant="h6" 
          gutterBottom 
          sx={{ 
            fontWeight: 600, 
            color: 'primary.main',
            fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
          }}
        >
          How to Use
        </Typography>
        <List>
          <ListItem sx={{ py: { xs: 1, sm: 1.5 }, px: { xs: 0, sm: 2 } }}>
            <ListItemIcon sx={{ minWidth: { xs: 40, sm: 56 } }}>
              <CheckCircleIcon sx={{ color: 'success.main', fontSize: { xs: 24, sm: 28 } }} />
            </ListItemIcon>
            <ListItemText 
              primary="Upload your dataset" 
              secondary="Supports CSV, JSON, and Excel formats. Simply drag and drop or click to browse."
              primaryTypographyProps={{ 
                fontWeight: 500, 
                fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
              }}
              secondaryTypographyProps={{ 
                fontSize: { xs: '0.8125rem', sm: '0.875rem' }
              }}
            />
          </ListItem>
          <ListItem sx={{ py: { xs: 1, sm: 1.5 }, px: { xs: 0, sm: 2 } }}>
            <ListItemIcon sx={{ minWidth: { xs: 40, sm: 56 } }}>
              <CheckCircleIcon sx={{ color: 'success.main', fontSize: { xs: 24, sm: 28 } }} />
            </ListItemIcon>
            <ListItemText 
              primary="Describe what you want the model to predict" 
              secondary="Use natural language to explain your goal. For example: 'Predict customer churn' or 'Classify product categories'."
              primaryTypographyProps={{ 
                fontWeight: 500, 
                fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
              }}
              secondaryTypographyProps={{ 
                fontSize: { xs: '0.8125rem', sm: '0.875rem' }
              }}
            />
          </ListItem>
          <ListItem sx={{ py: { xs: 1, sm: 1.5 }, px: { xs: 0, sm: 2 } }}>
            <ListItemIcon sx={{ minWidth: { xs: 40, sm: 56 } }}>
              <CheckCircleIcon sx={{ color: 'success.main', fontSize: { xs: 24, sm: 28 } }} />
            </ListItemIcon>
            <ListItemText 
              primary="Click 'Start Training' and watch the magic happen" 
              secondary="Our AI agent analyzes your data, selects the best model, and trains it automatically. Track progress in real-time."
              primaryTypographyProps={{ 
                fontWeight: 500, 
                fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
              }}
              secondaryTypographyProps={{ 
                fontSize: { xs: '0.8125rem', sm: '0.875rem' }
              }}
            />
          </ListItem>
          <ListItem sx={{ py: { xs: 1, sm: 1.5 }, px: { xs: 0, sm: 2 } }}>
            <ListItemIcon sx={{ minWidth: { xs: 40, sm: 56 } }}>
              <CheckCircleIcon sx={{ color: 'success.main', fontSize: { xs: 24, sm: 28 } }} />
            </ListItemIcon>
            <ListItemText 
              primary="Review results and download your trained model" 
              secondary="Get detailed performance metrics, visualizations, and a ready-to-use model for predictions."
              primaryTypographyProps={{ 
                fontWeight: 500, 
                fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
              }}
              secondaryTypographyProps={{ 
                fontSize: { xs: '0.8125rem', sm: '0.875rem' }
              }}
            />
          </ListItem>
        </List>
      </Paper>

      {/* Features Section */}
      <Paper sx={{ p: { xs: 2, sm: 3, md: 4 }, mb: { xs: 2, sm: 3 } }}>
        <Typography 
          variant="h6" 
          gutterBottom 
          sx={{ 
            fontWeight: 600, 
            color: 'primary.main', 
            mb: { xs: 2, sm: 3 },
            fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
          }}
        >
          Key Features
        </Typography>
        <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
          <Grid item xs={12} sm={6} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 1.5, sm: 2 } }}>
              <AutoAwesomeIcon sx={{ color: '#4285F4', fontSize: { xs: 28, sm: 32 }, mt: 0.5 }} />
              <Box>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600, 
                    mb: 0.5,
                    fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
                  }}
                >
                  Automatic Model Selection
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  AI agent analyzes your data and selects the optimal algorithm
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 1.5, sm: 2 } }}>
              <SpeedIcon sx={{ color: '#FBBC04', fontSize: { xs: 28, sm: 32 }, mt: 0.5 }} />
              <Box>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600, 
                    mb: 0.5,
                    fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
                  }}
                >
                  Fast Training
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Powered by Google Cloud Vertex AI for rapid model training
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 1.5, sm: 2 } }}>
              <SmartToyIcon sx={{ color: '#EA4335', fontSize: { xs: 28, sm: 32 }, mt: 0.5 }} />
              <Box>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600, 
                    mb: 0.5,
                    fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
                  }}
                >
                  AI-Powered Reasoning
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Intelligent decision-making at every step of the pipeline
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 1.5, sm: 2 } }}>
              <StorageIcon sx={{ color: '#34A853', fontSize: { xs: 28, sm: 32 }, mt: 0.5 }} />
              <Box>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600, 
                    mb: 0.5,
                    fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
                  }}
                >
                  Automatic Data Processing
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Handles cleaning, feature engineering, and preprocessing
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 1.5, sm: 2 } }}>
              <AssessmentIcon sx={{ color: '#4285F4', fontSize: { xs: 28, sm: 32 }, mt: 0.5 }} />
              <Box>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600, 
                    mb: 0.5,
                    fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
                  }}
                >
                  Detailed Analytics
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Comprehensive metrics and visualizations for model performance
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 1.5, sm: 2 } }}>
              <TrendingUpIcon sx={{ color: '#FBBC04', fontSize: { xs: 28, sm: 32 }, mt: 0.5 }} />
              <Box>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600, 
                    mb: 0.5,
                    fontSize: { xs: '0.875rem', sm: '0.9375rem', md: '1rem' }
                  }}
                >
                  Production Ready
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Deploy models directly to Vertex AI endpoints for predictions
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Use Case Examples */}
      <Paper sx={{ p: { xs: 2, sm: 3, md: 4 } }}>
        <Typography 
          variant="h6" 
          gutterBottom 
          sx={{ 
            fontWeight: 600, 
            color: 'primary.main', 
            mb: { xs: 2, sm: 3 },
            fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
          }}
        >
          Use Case Examples
        </Typography>
        <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
              <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    color: '#4285F4', 
                    fontWeight: 600,
                    fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
                  }}
                >
                  Customer Churn Prediction
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  paragraph
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Upload customer data with features like usage patterns, demographics, and support tickets. 
                  The platform identifies customers likely to churn and provides insights into key factors.
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontWeight: 500, 
                    color: 'success.main',
                    fontSize: { xs: '0.7rem', sm: '0.75rem' }
                  }}
                >
                  ✓ Classification • ✓ Feature Importance • ✓ Actionable Insights
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
              <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    color: '#34A853', 
                    fontWeight: 600,
                    fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
                  }}
                >
                  Sales Forecasting
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  paragraph
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Predict future sales based on historical data, seasonality, and market trends. 
                  Get accurate forecasts to optimize inventory and resource planning.
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontWeight: 500, 
                    color: 'success.main',
                    fontSize: { xs: '0.7rem', sm: '0.75rem' }
                  }}
                >
                  ✓ Regression • ✓ Time Series • ✓ Trend Analysis
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
              <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    color: '#FBBC04', 
                    fontWeight: 600,
                    fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
                  }}
                >
                  Product Categorization
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  paragraph
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Automatically classify products into categories based on descriptions, attributes, and images. 
                  Perfect for e-commerce catalog management and organization.
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontWeight: 500, 
                    color: 'success.main',
                    fontSize: { xs: '0.7rem', sm: '0.75rem' }
                  }}
                >
                  ✓ Multi-class Classification • ✓ Text Analysis • ✓ Automated Tagging
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
              <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    color: '#EA4335', 
                    fontWeight: 600,
                    fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
                  }}
                >
                  Fraud Detection
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  paragraph
                  sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                >
                  Identify fraudulent transactions or activities by analyzing patterns in transaction data. 
                  Protect your business with real-time anomaly detection.
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontWeight: 500, 
                    color: 'success.main',
                    fontSize: { xs: '0.7rem', sm: '0.75rem' }
                  }}
                >
                  ✓ Anomaly Detection • ✓ Binary Classification • ✓ Risk Scoring
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
