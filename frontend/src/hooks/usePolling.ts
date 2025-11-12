/**
 * Polling hook for pipeline progress updates.
 * 
 * Polls the REST API every 60 seconds to get pipeline status.
 * Replaces WebSocket with simpler, more reliable polling approach.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import axios from 'axios';

export type PipelineStage = 
  | 'analyzing' 
  | 'processing' 
  | 'labeling' 
  | 'model_selection' 
  | 'training' 
  | 'evaluation' 
  | 'deployment' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

export type LogLevel = 'debug' | 'info' | 'warning' | 'error';

export interface LogEntry {
  level: LogLevel;
  message: string;
  stage?: string;
  stage_display?: string;
  timestamp: string;
}

export interface DecisionLog {
  stage: string;
  stage_display: string;
  decision_type: string;
  decision: string;
  reasoning: string;
  confidence: number;
  confidence_percentage: number;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface ProgressData {
  stage: PipelineStage;
  progress: number;
  progress_percentage: number;
  stage_display: string;
  message?: string;
  estimated_time_remaining?: number;
  estimated_time_display?: string;
}

export interface UsePollingOptions {
  projectId: string;
  onStageTransition?: (data: ProgressData) => void;
  onProgressUpdate?: (data: ProgressData) => void;
  onLog?: (log: LogEntry) => void;
  onDecision?: (decision: DecisionLog) => void;
  onCompleted?: (result: any) => void;
  onFailed?: (error: string, stage: string) => void;
  onError?: (error: string, details?: string) => void;
  pollingInterval?: number; // milliseconds, default 60000 (1 minute)
}

export interface UsePollingReturn {
  isConnected: boolean; // Always true for polling (for compatibility)
  isReconnecting: boolean; // Always false for polling
  error: string | null;
  currentStage: PipelineStage | null;
  progress: number;
  logs: LogEntry[];
  decisions: DecisionLog[];
  sendMessage: (message: any) => void; // No-op for polling
  cancelPipeline: () => void;
  reconnect: () => void; // Triggers immediate poll
  disconnect: () => void;
}

/**
 * Custom hook for polling pipeline progress via REST API.
 * 
 * Polls /api/v1/projects/{projectId}/progress every 60 seconds.
 * 
 * @param options - Polling configuration options
 * @returns Polling state and control functions
 */
export function usePolling(options: UsePollingOptions): UsePollingReturn {
  const {
    projectId,
    onStageTransition,
    onProgressUpdate,
    onLog,
    onDecision,
    onCompleted,
    onFailed,
    onError,
    pollingInterval = 60000, // 1 minute default
  } = options;

  const [error, setError] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<PipelineStage | null>(null);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [decisions, setDecisions] = useState<DecisionLog[]>([]);
  const [isPolling, setIsPolling] = useState(true);

  const intervalRef = useRef<number | null>(null);
  const previousStageRef = useRef<PipelineStage | null>(null);
  const completedRef = useRef(false);

  // Get API URL from environment
  const getApiUrl = useCallback(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    return `${apiUrl}/projects/${projectId}/progress`;
  }, [projectId]);

  // Fetch progress from API
  const fetchProgress = useCallback(async () => {
    try {
      const url = getApiUrl();
      const response = await axios.get(url);
      const data = response.data;

      // Update state
      const newStage = data.stage as PipelineStage;
      setCurrentStage(newStage);
      setProgress(data.progress || 0);
      setError(data.error || null);

      // Update logs (append new ones)
      if (data.logs && Array.isArray(data.logs)) {
        setLogs(prev => {
          const existingTimestamps = new Set(prev.map(l => l.timestamp));
          const newLogs = data.logs.filter((log: LogEntry) => !existingTimestamps.has(log.timestamp));
          if (newLogs.length > 0) {
            newLogs.forEach((log: LogEntry) => onLog?.(log));
            return [...prev, ...newLogs];
          }
          return prev;
        });
      }

      // Update decisions (append new ones)
      if (data.decisions && Array.isArray(data.decisions)) {
        setDecisions(prev => {
          const existingTimestamps = new Set(prev.map(d => d.timestamp));
          const newDecisions = data.decisions.filter((dec: DecisionLog) => !existingTimestamps.has(dec.timestamp));
          if (newDecisions.length > 0) {
            newDecisions.forEach((dec: DecisionLog) => onDecision?.(dec));
            return [...prev, ...newDecisions];
          }
          return prev;
        });
      }

      // Check for stage transition
      if (previousStageRef.current !== newStage) {
        previousStageRef.current = newStage;
        onStageTransition?.({
          stage: newStage,
          progress: data.progress || 0,
          progress_percentage: Math.round((data.progress || 0) * 100),
          stage_display: data.stage_display || newStage.replace(/_/g, ' '),
        });
      }

      // Trigger progress update
      onProgressUpdate?.({
        stage: newStage,
        progress: data.progress || 0,
        progress_percentage: Math.round((data.progress || 0) * 100),
        stage_display: data.stage_display || newStage.replace(/_/g, ' '),
      });

      // Check for completion
      if (newStage === 'completed' && !completedRef.current) {
        completedRef.current = true;
        setIsPolling(false);
        onCompleted?.(data);
      }

      // Check for failure
      if (newStage === 'failed' && !completedRef.current) {
        completedRef.current = true;
        setIsPolling(false);
        onFailed?.(data.error || 'Pipeline failed', newStage);
      }

      // Clear error on successful fetch
      setError(null);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch progress';
      setError(errorMessage);
      onError?.(errorMessage);
      console.error('Polling error:', err);
    }
  }, [getApiUrl, onStageTransition, onProgressUpdate, onLog, onDecision, onCompleted, onFailed, onError]);

  // Start polling
  useEffect(() => {
    if (!isPolling) return;

    // Fetch immediately on mount
    fetchProgress();

    // Set up polling interval
    intervalRef.current = window.setInterval(() => {
      fetchProgress();
    }, pollingInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isPolling, pollingInterval, fetchProgress]);

  // Cancel pipeline (no-op for now, would need API endpoint)
  const cancelPipeline = useCallback(() => {
    console.warn('Cancel pipeline not implemented for polling');
    // Could implement: POST /api/v1/projects/{projectId}/cancel
  }, []);

  // Reconnect (trigger immediate poll)
  const reconnect = useCallback(() => {
    setError(null);
    completedRef.current = false;
    setIsPolling(true);
    fetchProgress();
  }, [fetchProgress]);

  // Disconnect (stop polling)
  const disconnect = useCallback(() => {
    setIsPolling(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Send message (no-op for polling)
  const sendMessage = useCallback(() => {
    console.warn('sendMessage not supported for polling');
  }, []);

  return {
    isConnected: true, // Always "connected" for polling
    isReconnecting: false, // Never reconnecting for polling
    error,
    currentStage,
    progress,
    logs,
    decisions,
    sendMessage,
    cancelPipeline,
    reconnect,
    disconnect,
  };
}
