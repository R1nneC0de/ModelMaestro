import { Card, CardContent, Box, Typography, Chip } from '@mui/material';
import { TrainingSession } from '../../types';

interface HistoryCardProps {
  session: TrainingSession;
  onClick: () => void;
}

export function HistoryCard({ session, onClick }: HistoryCardProps) {
  const statusColor = {
    completed: '#34A853',
    failed: '#EA4335',
    training: '#FBBC04'
  }[session.status];
  
  return (
    <Card 
      onClick={onClick} 
      sx={{ 
        cursor: 'pointer', 
        '&:hover': { boxShadow: 6 },
        transition: 'box-shadow 0.3s ease',
        minHeight: { xs: 'auto', sm: '180px' }
      }}
    >
      <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          mb: { xs: 1.5, sm: 2 },
          flexDirection: { xs: 'column', sm: 'row' },
          gap: { xs: 1, sm: 0 },
          alignItems: { xs: 'flex-start', sm: 'center' }
        }}>
          <Typography 
            variant="h6" 
            sx={{ 
              maxWidth: { xs: '100%', sm: '70%' },
              fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {session.datasetName}
          </Typography>
          <Chip 
            label={session.status} 
            size="small"
            sx={{ 
              bgcolor: statusColor, 
              color: 'white',
              textTransform: 'capitalize',
              height: { xs: '24px', sm: '28px' },
              fontSize: { xs: '0.75rem', sm: '0.8125rem' }
            }}
          />
        </Box>
        <Typography 
          color="text.secondary" 
          variant="body2"
          sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
        >
          {new Date(session.timestamp).toLocaleString()}
        </Typography>
        {session.metrics && (
          <Box sx={{ mt: { xs: 1.5, sm: 2 } }}>
            <Typography 
              variant="body2"
              sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
            >
              Accuracy: {(session.metrics.accuracy * 100).toFixed(1)}%
            </Typography>
            {session.metrics.precision && (
              <Typography 
                variant="body2"
                sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
              >
                Precision: {(session.metrics.precision * 100).toFixed(1)}%
              </Typography>
            )}
            {session.metrics.recall && (
              <Typography 
                variant="body2"
                sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
              >
                Recall: {(session.metrics.recall * 100).toFixed(1)}%
              </Typography>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
