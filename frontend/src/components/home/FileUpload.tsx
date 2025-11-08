import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import CloseIcon from '@mui/icons-material/Close';
import { validateFile, formatFileSize } from '../../utils/validators';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export function FileUpload({ onFileSelect, selectedFile }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileValidation = (file: File): boolean => {
    const validation = validateFile(file);
    
    if (!validation.isValid) {
      setValidationError(validation.error || 'Invalid file');
      return false;
    }
    
    setValidationError(null);
    return true;
  };

  const handleFileSelection = (file: File) => {
    if (handleFileValidation(file)) {
      onFileSelect(file);
    } else {
      onFileSelect(null);
    }
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    onFileSelect(null);
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Box>
      <Paper
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        sx={{
          p: { xs: 2, sm: 3, md: 4 },
          border: '2px dashed',
          borderColor: isDragging ? 'primary.main' : 'grey.300',
          bgcolor: isDragging ? 'action.hover' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          minHeight: { xs: '180px', sm: '200px' },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
          },
        }}
        onClick={handleBrowseClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          hidden
          accept=".csv,.json,.xlsx,.xls"
          onChange={handleFileInputChange}
        />
        
        <Box>
          <CloudUploadIcon 
            sx={{ 
              fontSize: { xs: 48, sm: 60 }, 
              color: isDragging ? 'primary.main' : 'grey.400',
              mb: { xs: 1, sm: 2 }
            }} 
          />
          
          <Typography 
            variant="h6" 
            gutterBottom
            sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
          >
            {isDragging ? 'Drop your file here' : 'Upload Dataset'}
          </Typography>
          
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ 
              mb: { xs: 1, sm: 2 },
              fontSize: { xs: '0.8125rem', sm: '0.875rem' },
              px: { xs: 1, sm: 0 }
            }}
          >
            Drag & drop your dataset or click to browse
          </Typography>
          
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ 
              fontSize: { xs: '0.7rem', sm: '0.75rem' },
              px: { xs: 1, sm: 0 },
              display: 'block'
            }}
          >
            Supported formats: CSV, JSON, Excel (.xlsx, .xls) • Max size: 50MB
          </Typography>
        </Box>
      </Paper>

      {validationError && (
        <Alert 
          severity="error" 
          sx={{ 
            mt: 2,
            fontSize: { xs: '0.8125rem', sm: '0.875rem' }
          }}
        >
          {validationError}
        </Alert>
      )}

      {selectedFile && !validationError && (
        <Paper
          sx={{
            mt: 2,
            p: { xs: 1.5, sm: 2 },
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            bgcolor: 'rgba(52, 168, 83, 0.1)',
            flexDirection: { xs: 'column', sm: 'row' },
            gap: { xs: 1, sm: 0 }
          }}
        >
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1,
            width: { xs: '100%', sm: 'auto' }
          }}>
            <InsertDriveFileIcon sx={{ color: 'primary.main' }} />
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography 
                variant="body2" 
                fontWeight="medium"
                sx={{ 
                  fontSize: { xs: '0.8125rem', sm: '0.875rem' },
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
              >
                {selectedFile.name}
              </Typography>
              <Typography 
                variant="caption" 
                color="text.secondary"
                sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
              >
                {formatFileSize(selectedFile.size)}
              </Typography>
            </Box>
          </Box>
          
          <Button
            size="small"
            startIcon={<CloseIcon />}
            onClick={(e) => {
              e.stopPropagation();
              handleRemoveFile();
            }}
            sx={{ 
              color: 'text.secondary',
              minHeight: '36px',
              width: { xs: '100%', sm: 'auto' }
            }}
          >
            Remove
          </Button>
        </Paper>
      )}
    </Box>
  );
}
