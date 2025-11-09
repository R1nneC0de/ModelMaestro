import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { trainingApi } from '../services/api';
import { TrainingProgress } from '../types';

interface UseTrainingProgressOptions {
  projectId: string | null;
  enabled?: boolean;
  refetchInterval?: number;
}

export function useTrainingProgress({
  projectId,
  enabled = true,
  refetchInterval = 2000, // Poll every 2 seconds
}: UseTrainingProgressOptions) {
  const [progress, setProgress] = useState<TrainingProgress | null>(null);

  const { data, error, isLoading } = useQuery({
    queryKey: ['training-progress', projectId],
    queryFn: async () => {
      if (!projectId) return null;
      return trainingApi.getProgress(projectId);
    },
    enabled: enabled && !!projectId,
    refetchInterval: (query) => {
      // Stop polling if training is complete or failed
      const data = query.state.data as any;
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return refetchInterval;
    },
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  useEffect(() => {
    if (data) {
      // Map API response to TrainingProgress format
      if (data.status === 'training' || data.status === 'in_progress') {
        setProgress({
          stage: data.stage || 'analyzing',
          progress: data.progress || 0,
          message: data.message || 'Processing...',
        });
      } else {
        // Training completed or failed
        setProgress(null);
      }
    }
  }, [data]);

  return {
    progress,
    error: error as Error | null,
    isLoading,
    isComplete: data?.status === 'completed',
    isFailed: data?.status === 'failed',
    projectData: data,
  };
}


