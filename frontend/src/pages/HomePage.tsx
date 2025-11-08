import { useState } from 'react';
import { Box, Typography, Button, Alert, CircularProgress } from '@mui/material';
import { FileUpload } from '../components/home/FileUpload';
import { PromptInput } from '../components/home/PromptInput';
import { useTraining } from '../hooks/useTraining';

export function HomePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [prompt, setPrompt] = useState('');
  const { mutate: submitTraining, isPending, isError, isSuccess, error } = useTraining();

  const handleSubmit = () => {
    if (selectedFile && prompt) {
      submitTraining({ file: selectedFile, prompt });
    }
  };

  const isSubmitDisabled = !selectedFile || !prompt.trim() || isPending;

  return (
    <Box sx={{ 
      maxWidth: { xs: '100%', sm: '600px', md: '800px' },
      mx: 'auto'
    }}>
      <Typography 
        variant="h4" 
        gutterBottom
        sx={{
          fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' },
          mb: { xs: 2, sm: 3 }
        }}
      >
        Start Model Training
      </Typography>
      
      <Box sx={{ mt: { xs: 2, sm: 3 } }}>
        <FileUpload 
          onFileSelect={setSelectedFile} 
          selectedFile={selectedFile} 
        />
      </Box>

      <PromptInput value={prompt} onChange={setPrompt} />

      <Box sx={{ mt: { xs: 2, sm: 3 } }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          fullWidth
          sx={{ 
            py: { xs: 1.5, sm: 1.75 },
            fontSize: { xs: '1rem', sm: '1.1rem' },
            fontWeight: 500,
            minHeight: '48px'
          }}
        >
          {isPending ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1, color: 'white' }} />
              Starting Training...
            </>
          ) : (
            'Start Training'
          )}
        </Button>
      </Box>

      {isError && (
        <Alert 
          severity="error" 
          sx={{ 
            mt: { xs: 2, sm: 3 },
            fontSize: { xs: '0.875rem', sm: '1rem' }
          }}
        >
          Failed to start training: {error instanceof Error ? error.message : 'Unknown error occurred'}
        </Alert>
      )}

      {isSuccess && (
        <Alert 
          severity="success" 
          sx={{ 
            mt: { xs: 2, sm: 3 },
            fontSize: { xs: '0.875rem', sm: '1rem' }
          }}
        >
          Training started successfully! Your model is now being trained.
        </Alert>
      )}
    </Box>
  );
}
