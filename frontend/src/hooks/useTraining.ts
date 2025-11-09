import { useMutation } from '@tanstack/react-query';
import { trainingApi } from '../services/api';
import { TrainingSubmission } from '../types';

export function useTraining() {
  return useMutation({
    mutationFn: async ({ file, prompt }: TrainingSubmission) => {
      // Task 2.1: Two-step upload process
      // Step 1: Upload file to /data/upload endpoint
      // Step 2: Create project with dataset_id
      const response = await trainingApi.submitTwoStep(file, prompt);
      
      // Return project data with projectId for downstream components
      return {
        projectId: response.id,
        status: response.status,
        datasetId: response.dataset_id,
        ...response
      };
    },
    onSuccess: (data) => {
      console.log('Training started:', data);
      console.log('Project ID:', data.projectId);
    },
    onError: (error) => {
      console.error('Training failed:', error);
    }
  });
}
