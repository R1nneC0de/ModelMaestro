import { useMemo } from 'react';

interface FormValidationOptions {
  file: File | null;
  prompt: string;
  isPending?: boolean;
}

interface FormValidationResult {
  isValid: boolean;
  isSubmitDisabled: boolean;
  errors: {
    file?: string;
    prompt?: string;
  };
}

export function useFormValidation({ 
  file, 
  prompt, 
  isPending = false 
}: FormValidationOptions): FormValidationResult {
  return useMemo(() => {
    const errors: FormValidationResult['errors'] = {};
    
    if (!file) {
      errors.file = 'Please select a file';
    }
    
    if (!prompt.trim()) {
      errors.prompt = 'Please provide training instructions';
    }
    
    const isValid = Object.keys(errors).length === 0;
    const isSubmitDisabled = !isValid || isPending;
    
    return {
      isValid,
      isSubmitDisabled,
      errors
    };
  }, [file, prompt, isPending]);
}
