import { useState } from 'react';
import { Grid, CircularProgress, Box, Typography } from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import { useHistory } from '../../hooks/useHistory';
import { HistoryCard } from './HistoryCard';
import { SessionDetail } from './SessionDetail';

export function HistoryList() {
  const { data: sessions, isLoading, error } = useHistory();
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="error">
          Failed to load training history
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Please try again later
        </Typography>
      </Box>
    );
  }
  
  if (!sessions || sessions.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <HistoryIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          No training history yet
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Start your first training session from the Home page
        </Typography>
      </Box>
    );
  }
  
  return (
    <>
      <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
        {sessions.map(session => (
          <Grid item xs={12} sm={12} md={6} lg={6} key={session.id}>
            <HistoryCard 
              session={session} 
              onClick={() => setSelectedSession(session.id)}
            />
          </Grid>
        ))}
      </Grid>
      {selectedSession && (
        <SessionDetail 
          sessionId={selectedSession}
          onClose={() => setSelectedSession(null)}
        />
      )}
    </>
  );
}
