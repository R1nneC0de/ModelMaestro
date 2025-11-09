import { useQuery } from '@tanstack/react-query';
import { historyApi } from '../services/api';
import { TrainingSession } from '../types';

export function useSessionDetail(sessionId: string | null) {
  return useQuery<TrainingSession>({
    queryKey: ['session-detail', sessionId],
    queryFn: () => historyApi.getById(sessionId!),
    enabled: !!sessionId,
    staleTime: 10000 // Consider data fresh for 10 seconds
  });
}
