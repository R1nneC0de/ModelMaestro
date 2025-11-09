/**
 * WebSocket hook for real-time pipeline updates.
 * 
 * Manages WebSocket connection lifecycle, reconnection logic,
 * and event handling for project progress updates.
 */

import { useEffect, useRef, useState, useCallback } from 'react';

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

export interface WebSocketEvent {
  event_type: string;
  project_id: string;
  timestamp: string;
  data: any;
}

export interface UseWebSocketOptions {
  projectId: string;
  onStageTransition?: (data: ProgressData) => void;
  onProgressUpdate?: (data: ProgressData) => void;
  onLog?: (log: LogEntry) => void;
  onDecision?: (decision: DecisionLog) => void;
  onApprovalRequired?: (data: any) => void;
  onCompleted?: (result: any) => void;
  onFailed?: (error: string, stage: string) => void;
  onError?: (error: string, details?: string) => void;
  autoReconnect?: boolean;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  isReconnecting: boolean;
  error: string | null;
  currentStage: PipelineStage | null;
  progress: number;
  logs: LogEntry[];
  decisions: DecisionLog[];
  sendMessage: (message: any) => void;
  cancelPipeline: () => void;
  reconnect: () => void;
  disconnect: () => void;
}

/**
 * Custom hook for managing WebSocket connection to pipeline updates.
 * 
 * Features:
 * - Automatic connection management
 * - Reconnection with exponential backoff
 * - Event handling and state management
 * - Heartbeat/ping-pong for connection health
 * 
 * @param options - WebSocket configuration options
 * @returns WebSocket state and control functions
 */
export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    projectId,
    onStageTransition,
    onProgressUpdate,
    onLog,
    onDecision,
    onApprovalRequired,
    onCompleted,
    onFailed,
    onError,
    autoReconnect = true,
    reconnectDelay = 3000,
    maxReconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<PipelineStage | null>(null);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [decisions, setDecisions] = useState<DecisionLog[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const pingIntervalRef = useRef<number | null>(null);
  const shouldReconnectRef = useRef(true);

  // Get WebSocket URL from environment
  const getWebSocketUrl = useCallback(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    // Remove /api/v1 suffix if present
    const baseUrl = apiUrl.replace(/\/api\/v1$/, '');
    
    // Determine protocol
    const isHttps = baseUrl.startsWith('https://');
    const wsProtocol = isHttps ? 'wss://' : 'ws://';
    
    // Remove http(s):// prefix
    const host = baseUrl.replace(/^https?:\/\//, '');
    
    const url = `${wsProtocol}${host}/api/v1/ws/projects/${projectId}/stream`;
    console.log('WebSocket URL:', url);
    
    return url;
  }, [projectId]);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketEvent = JSON.parse(event.data);
      const { event_type, data } = message;

      switch (event_type) {
        case 'connected':
        case 'initial_state':
          console.log('WebSocket connected:', message);
          setError(null);
          reconnectAttemptsRef.current = 0;
          break;

        case 'stage_transition':
          setCurrentStage(data.stage);
          setProgress(data.progress);
          onStageTransition?.(data);
          break;

        case 'progress_update':
          setCurrentStage(data.stage);
          setProgress(data.progress);
          onProgressUpdate?.(data);
          break;

        case 'log':
          const logEntry: LogEntry = {
            ...data,
            timestamp: message.timestamp,
          };
          setLogs(prev => [...prev, logEntry]);
          onLog?.(logEntry);
          break;

        case 'decision':
          const decisionEntry: DecisionLog = {
            ...data,
            timestamp: message.timestamp,
          };
          setDecisions(prev => [...prev, decisionEntry]);
          onDecision?.(decisionEntry);
          break;

        case 'approval_required':
          onApprovalRequired?.(data);
          break;

        case 'pipeline_completed':
          setCurrentStage('completed');
          setProgress(1);
          onCompleted?.(data.result);
          break;

        case 'pipeline_failed':
          setCurrentStage('failed');
          setError(data.error);
          onFailed?.(data.error, data.stage);
          break;

        case 'pipeline_cancelled':
          setCurrentStage('cancelled');
          break;

        case 'error':
          setError(data.error);
          onError?.(data.error, data.details);
          break;

        case 'ping':
          // Respond to server ping with pong
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'pong' }));
          }
          break;

        case 'pong':
          // Server responded to our ping
          console.log('Received pong from server');
          break;

        default:
          console.warn('Unknown WebSocket event type:', event_type);
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
      setError('Failed to parse server message');
    }
  }, [onStageTransition, onProgressUpdate, onLog, onDecision, onApprovalRequired, onCompleted, onFailed, onError]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const url = getWebSocketUrl();
      console.log('Connecting to WebSocket:', url);
      
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connection established');
        setIsConnected(true);
        setIsReconnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Start ping interval to keep connection alive
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000); // Ping every 30 seconds
      };

      ws.onmessage = handleMessage;

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        setIsConnected(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Attempt reconnection if enabled and not manually closed
        if (
          shouldReconnectRef.current &&
          autoReconnect &&
          reconnectAttemptsRef.current < maxReconnectAttempts &&
          event.code !== 1000 // 1000 = normal closure
        ) {
          setIsReconnecting(true);
          reconnectAttemptsRef.current += 1;
          
          const delay = reconnectDelay * Math.pow(2, reconnectAttemptsRef.current - 1);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('Maximum reconnection attempts reached');
          setIsReconnecting(false);
        }
      };
    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
      setIsConnected(false);
    }
  }, [getWebSocketUrl, handleMessage, autoReconnect, reconnectDelay, maxReconnectAttempts]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsReconnecting(false);
  }, []);

  // Manual reconnect
  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    reconnectAttemptsRef.current = 0;
    setError(null);
    connect();
  }, [connect, disconnect]);

  // Send message to server
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected, cannot send message');
    }
  }, []);

  // Cancel pipeline
  const cancelPipeline = useCallback(() => {
    sendMessage({ type: 'cancel' });
  }, [sendMessage]);

  // Connect on mount
  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    isReconnecting,
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
