/**
 * File validation utilities for upload component
 */

export interface FileValidationResult {
  isValid: boolean;
  error?: string;
}

const ALLOWED_EXTENSIONS = ['.csv', '.json', '.xlsx', '.xls'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

/**
 * Validates file format based on extension
 */
export function validateFileFormat(file: File): FileValidationResult {
  const fileName = file.name.toLowerCase();
  const hasValidExtension = ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext));
  
  if (!hasValidExtension) {
    return {
      isValid: false,
      error: `Invalid file format. Please upload a CSV, JSON, or Excel file.`
    };
  }
  
  return { isValid: true };
}

/**
 * Validates file size
 */
export function validateFileSize(file: File): FileValidationResult {
  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = (MAX_FILE_SIZE / (1024 * 1024)).toFixed(0);
    return {
      isValid: false,
      error: `File size exceeds ${sizeMB}MB limit. Please upload a smaller file.`
    };
  }
  
  if (file.size === 0) {
    return {
      isValid: false,
      error: 'File is empty. Please upload a valid file.'
    };
  }
  
  return { isValid: true };
}

/**
 * Validates file completely (format and size)
 */
export function validateFile(file: File): FileValidationResult {
  const formatValidation = validateFileFormat(file);
  if (!formatValidation.isValid) {
    return formatValidation;
  }
  
  const sizeValidation = validateFileSize(file);
  if (!sizeValidation.isValid) {
    return sizeValidation;
  }
  
  return { isValid: true };
}

/**
 * Formats file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
