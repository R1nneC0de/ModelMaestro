import { useQuery } from '@tanstack/react-query';
import { historyApi } from '../services/api';
import { TrainingSession } from '../types';

interface HistoryResponse {
  sessions: TrainingSession[];
  total: number;
  page: number;
  pageSize: number;
}

// Task 3.1: Fetch projects from backend with pagination support
export function useHistory(page: number = 1, pageSize: number = 50) {
  return useQuery<HistoryResponse>({
    queryKey: ['training-history', page, pageSize],
    queryFn: () => historyApi.getAll(page, pageSize),
    refetchInterval: 30000, // Refetch every 30 seconds to catch status updates
    select: (data) => ({
      sessions: data.sessions,
      total: data.total,
      page: data.page,
      pageSize: data.pageSize
    })
  });
}
