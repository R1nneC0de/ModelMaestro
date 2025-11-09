import { useMutation } from '@tanstack/react-query';
import { trainingApi } from '../services/api';
import { TrainingSubmission } from '../types';

export function useTraining() {
  return useMutation({
    mutationFn: async ({ file, prompt }: TrainingSubmission) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('problemDescription', prompt);
      const response = await trainingApi.submit(formData);
      return response;
    },
    onSuccess: (data) => {
      console.log('Training started:', data);
    },
    onError: (error) => {
      console.error('Training failed:', error);
    }
  });
}
