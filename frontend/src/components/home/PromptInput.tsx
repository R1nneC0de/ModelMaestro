import React from 'react';
import {
  TextField,
  Box,
  Typography,
} from '@mui/material';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function PromptInput({ value, onChange }: PromptInputProps) {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(event.target.value);
  };

  return (
    <Box sx={{ mt: { xs: 2, sm: 3 } }}>
      <TextField
        fullWidth
        multiline
        rows={4}
        label="Training Instructions"
        placeholder="Describe what you want the model to learn... For example: 'Predict customer churn based on usage patterns' or 'Classify sentiment from product reviews'"
        value={value}
        onChange={handleChange}
        variant="outlined"
        sx={{
          '& .MuiOutlinedInput-root': {
            fontSize: { xs: '0.875rem', sm: '1rem' },
            '&:hover fieldset': {
              borderColor: 'primary.main',
            },
          },
          '& .MuiInputLabel-root': {
            fontSize: { xs: '0.875rem', sm: '1rem' }
          },
          '& .MuiOutlinedInput-input': {
            minHeight: { xs: '80px', sm: '96px' }
          }
        }}
      />
      <Typography 
        variant="caption" 
        color="text.secondary" 
        sx={{ 
          mt: 1, 
          display: 'block',
          fontSize: { xs: '0.7rem', sm: '0.75rem' },
          px: { xs: 0.5, sm: 0 }
        }}
      >
        Provide clear instructions about what you want the model to predict or classify
      </Typography>
    </Box>
  );
}
