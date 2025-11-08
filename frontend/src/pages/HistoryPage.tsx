import { Box, Typography } from '@mui/material';
import { HistoryList } from '../components/history/HistoryList';

export function HistoryPage() {
  return (
    <Box>
      <Typography 
        variant="h4" 
        gutterBottom 
        sx={{ 
          mb: { xs: 2, sm: 3, md: 4 },
          fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' }
        }}
      >
        Training History
      </Typography>
      <HistoryList />
    </Box>
  );
}
