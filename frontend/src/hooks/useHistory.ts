import { useQuery } from '@tanstack/react-query';
import { historyApi } from '../services/api';
import { TrainingSession } from '../types';

export function useHistory() {
  return useQuery<TrainingSession[]>({
    queryKey: ['training-history'],
    queryFn: historyApi.getAll,
    refetchInterval: 30000 // Refetch every 30 seconds
  });
}
