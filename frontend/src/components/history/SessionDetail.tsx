import { 
  Modal, 
  Box, 
  Typography, 
  IconButton, 
  Divider,
  Chip,
  CircularProgress,
  Paper,
  Grid
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useQuery } from '@tanstack/react-query';
import { historyApi } from '../../services/api';
import { TrainingSession } from '../../types';

interface SessionDetailProps {
  sessionId: string;
  onClose: () => void;
}

export function SessionDetail({ sessionId, onClose }: SessionDetailProps) {
  const { data: session, isLoading, error } = useQuery<TrainingSession>({
    queryKey: ['training-session', sessionId],
    queryFn: () => historyApi.getById(sessionId)
  });

  const statusColor = session ? {
    completed: '#34A853',
    failed: '#EA4335',
    training: '#FBBC04'
  }[session.status] : '#FBBC04';

  return (
    <Modal 
      open={true} 
      onClose={onClose}
      aria-labelledby="session-detail-title"
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: { xs: '95%', sm: '85%', md: 600 },
        maxWidth: '600px',
        maxHeight: { xs: '95vh', sm: '90vh' },
        overflow: 'auto',
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 24,
        p: { xs: 2, sm: 3, md: 4 }
      }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: { xs: 1.5, sm: 2 }
        }}>
          <Typography 
            id="session-detail-title" 
            variant="h5" 
            component="h2"
            sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }}
          >
            Training Session Details
          </Typography>
          <IconButton 
            onClick={onClose} 
            aria-label="close"
            sx={{ minWidth: '44px', minHeight: '44px' }}
          >
            <CloseIcon />
          </IconButton>
        </Box>

        <Divider sx={{ mb: { xs: 2, sm: 3 } }} />

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: { xs: 3, sm: 4 } }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Typography 
            color="error" 
            sx={{ 
              textAlign: 'center', 
              py: { xs: 3, sm: 4 },
              fontSize: { xs: '0.875rem', sm: '1rem' }
            }}
          >
            Failed to load session details
          </Typography>
        )}

        {session && (
          <Box>
            <Paper sx={{ p: { xs: 1.5, sm: 2 }, mb: { xs: 1.5, sm: 2 }, bgcolor: 'background.default' }}>
              <Grid container spacing={{ xs: 1.5, sm: 2 }}>
                <Grid item xs={12}>
                  <Typography 
                    variant="subtitle2" 
                    color="text.secondary"
                    sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                  >
                    Dataset Name
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      fontWeight: 500,
                      fontSize: { xs: '0.875rem', sm: '1rem' },
                      wordBreak: 'break-word'
                    }}
                  >
                    {session.datasetName}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography 
                    variant="subtitle2" 
                    color="text.secondary"
                    sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                  >
                    Status
                  </Typography>
                  <Chip 
                    label={session.status} 
                    size="small"
                    sx={{ 
                      bgcolor: statusColor, 
                      color: 'white',
                      textTransform: 'capitalize',
                      mt: 0.5,
                      height: { xs: '24px', sm: '28px' },
                      fontSize: { xs: '0.75rem', sm: '0.8125rem' }
                    }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography 
                    variant="subtitle2" 
                    color="text.secondary"
                    sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                  >
                    Timestamp
                  </Typography>
                  <Typography 
                    variant="body1"
                    sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                  >
                    {new Date(session.timestamp).toLocaleString()}
                  </Typography>
                </Grid>

                {session.prompt && (
                  <Grid item xs={12}>
                    <Typography 
                      variant="subtitle2" 
                      color="text.secondary"
                      sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                    >
                      Training Prompt
                    </Typography>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        fontSize: { xs: '0.875rem', sm: '1rem' },
                        wordBreak: 'break-word'
                      }}
                    >
                      {session.prompt}
                    </Typography>
                  </Grid>
                )}

                {session.modelId && (
                  <Grid item xs={12}>
                    <Typography 
                      variant="subtitle2" 
                      color="text.secondary"
                      sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                    >
                      Model ID
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontFamily: 'monospace',
                        fontSize: { xs: '0.75rem', sm: '0.8125rem' },
                        wordBreak: 'break-all'
                      }}
                    >
                      {session.modelId}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Paper>

            {session.metrics && (
              <Paper sx={{ p: { xs: 1.5, sm: 2 }, bgcolor: 'background.default' }}>
                <Typography 
                  variant="h6" 
                  gutterBottom
                  sx={{ fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' } }}
                >
                  Model Metrics
                </Typography>
                <Grid container spacing={{ xs: 1.5, sm: 2 }}>
                  <Grid item xs={6} sm={4}>
                    <Typography 
                      variant="subtitle2" 
                      color="text.secondary"
                      sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                    >
                      Accuracy
                    </Typography>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        color: '#34A853',
                        fontSize: { xs: '1.125rem', sm: '1.25rem' }
                      }}
                    >
                      {(session.metrics.accuracy * 100).toFixed(1)}%
                    </Typography>
                  </Grid>
                  {session.metrics.precision && (
                    <Grid item xs={6} sm={4}>
                      <Typography 
                        variant="subtitle2" 
                        color="text.secondary"
                        sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                      >
                        Precision
                      </Typography>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          color: '#4285F4',
                          fontSize: { xs: '1.125rem', sm: '1.25rem' }
                        }}
                      >
                        {(session.metrics.precision * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                  )}
                  {session.metrics.recall && (
                    <Grid item xs={6} sm={4}>
                      <Typography 
                        variant="subtitle2" 
                        color="text.secondary"
                        sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                      >
                        Recall
                      </Typography>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          color: '#FBBC04',
                          fontSize: { xs: '1.125rem', sm: '1.25rem' }
                        }}
                      >
                        {(session.metrics.recall * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Paper>
            )}
          </Box>
        )}
      </Box>
    </Modal>
  );
}
