import React, { useState, useRef, useEffect } from 'react';
import { validateFile, formatFileSize } from '../../../utils/validators';
import { useTraining } from '../../../hooks/useTraining';
import { useNavigationStore } from '../../store/navigationStore';
import './FileUploadOverlay.css';

/**
 * FileUploadOverlay Component
 * 
 * Embedded in Create Model section overlay.
 * Reuses existing file validation logic and integrates with backend API.
 * 
 * Requirements: 11.1, 11.5, 14.1
 */

export interface FileUploadOverlayProps {
  visible: boolean;
}

export function FileUploadOverlay({ visible }: FileUploadOverlayProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [prompt, setPrompt] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { mutate: startTraining, isPending, isSuccess, error, data } = useTraining();
  const { triggerUploadAnimation, startTrainingVisualization } = useNavigationStore();
  
  // Trigger upload animation and training visualization on success (Req 11.2, 11.3)
  useEffect(() => {
    if (isSuccess && data) {
      // Trigger upload particle animation (Req 11.2)
      triggerUploadAnimation();
      
      // Start training visualization if we have a project ID (Req 11.3)
      if (data.projectId) {
        startTrainingVisualization(data.projectId);
      }
    }
  }, [isSuccess, data, triggerUploadAnimation, startTrainingVisualization]);

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
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
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
    setSelectedFile(null);
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile || !prompt.trim()) {
      setValidationError('Please select a file and provide a description');
      return;
    }

    startTraining({ file: selectedFile, prompt: prompt.trim() });
  };

  if (!visible) {
    return null;
  }

  return (
    <div className="file-upload-overlay">
      <form onSubmit={handleSubmit} className="file-upload-overlay__panel">
        {/* Unified Glass Panel */}
        <div
          className={`upload-panel ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".csv,.json,.xlsx,.xls"
            onChange={handleFileInputChange}
            disabled={isPending}
          />
          
          {/* File Section */}
          <div className="upload-panel__file-section" onClick={handleBrowseClick}>
            {!selectedFile ? (
              <>
                <svg className="upload-panel__icon" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <p className="upload-panel__text">
                  {isDragging ? 'Drop your dataset here' : 'Drop file or click to upload'}
                </p>
                <p className="upload-panel__hint">CSV, JSON, Excel • Max 50MB</p>
              </>
            ) : (
              <div className="upload-panel__file-display">
                <svg className="upload-panel__file-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                  <polyline points="13 2 13 9 20 9" />
                </svg>
                <div className="upload-panel__file-details">
                  <p className="upload-panel__file-name">{selectedFile.name}</p>
                  <p className="upload-panel__file-size">{formatFileSize(selectedFile.size)}</p>
                </div>
                <button
                  type="button"
                  className="upload-panel__remove"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveFile();
                  }}
                  disabled={isPending}
                  aria-label="Remove file"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="upload-panel__divider" />

          {/* Prompt Section */}
          <div className="upload-panel__prompt-section">
            <textarea
              id="prompt-input"
              className="upload-panel__textarea"
              placeholder="What do you want to predict? (e.g., customer churn, sales forecast, fraud detection)"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              disabled={isPending}
              required
            />
          </div>

          {/* Status Messages */}
          {(validationError || error) && (
            <div className="upload-panel__message upload-panel__message--error" role="alert">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>{validationError || (error as Error)?.message || 'An error occurred'}</span>
            </div>
          )}

          {isSuccess && (
            <div className="upload-panel__message upload-panel__message--success" role="status">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
              <span>Training started! Check Past Models for progress.</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="upload-panel__submit"
            disabled={!selectedFile || !prompt.trim() || isPending}
          >
            {isPending ? (
              <>
                <svg className="upload-panel__spinner" width="20" height="20" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.25" />
                  <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" fill="none" strokeLinecap="round" />
                </svg>
                Training...
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                Start Training
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
