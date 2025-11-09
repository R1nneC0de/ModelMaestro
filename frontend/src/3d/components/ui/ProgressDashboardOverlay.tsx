import { useEffect } from 'react';
import { useWebSocket } from '../../../hooks/useWebSocket';
import { PipelineStages } from '../dashboard/PipelineStages';
import { LogStream } from '../dashboard/LogStream';
import './ProgressDashboardOverlay.css';

/**
 * ProgressDashboardOverlay Component
 * 
 * Real-time progress dashboard for ML pipeline execution.
 * Shows pipeline stages, progress, logs, and decision logs.
 * 
 * Requirements: 2.1, 2.2, 2.3, 2.4, 6.2, 6.3, 6.4
 */

export interface ProgressDashboardOverlayProps {
  visible: boolean;
  projectId: string;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

export function ProgressDashboardOverlay({ 
  visible, 
  projectId,
  onComplete,
  onError 
}: ProgressDashboardOverlayProps) {
  const {
    isConnected,
    isReconnecting,
    error: wsError,
    currentStage,
    progress,
    logs,
    decisions,
    cancelPipeline,
    reconnect,
  } = useWebSocket({
    projectId,
    autoReconnect: true,
    onCompleted: (result) => {
      console.log('Pipeline completed:', result);
      onComplete?.();
    },
    onFailed: (error, stage) => {
      console.error('Pipeline failed:', error, 'at stage:', stage);
      onError?.(error);
    },
    onError: (error, details) => {
      console.error('WebSocket error:', error, details);
    },
  });

  // Notify parent of errors
  useEffect(() => {
    if (wsError) {
      onError?.(wsError);
    }
  }, [wsError, onError]);

  if (!visible) {
    return null;
  }

  return (
    <div className="progress-dashboard-overlay">
      <div className="progress-dashboard-overlay__panel">
        {/* Header */}
        <div className="progress-dashboard__header">
          <div className="progress-dashboard__title-section">
            <h2 className="progress-dashboard__title">Training Pipeline</h2>
            <p className="progress-dashboard__subtitle">Project: {projectId.slice(0, 8)}</p>
          </div>
          
          {/* Connection Status */}
          <div className="progress-dashboard__status">
            {isReconnecting ? (
              <div className="status-badge status-badge--reconnecting">
                <svg className="status-badge__spinner" width="14" height="14" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.25" />
                  <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" fill="none" strokeLinecap="round" />
                </svg>
                Reconnecting...
              </div>
            ) : isConnected ? (
              <div className="status-badge status-badge--connected">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="12" r="10" />
                </svg>
                Live
              </div>
            ) : (
              <div className="status-badge status-badge--disconnected">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="12" r="10" />
                </svg>
                Disconnected
              </div>
            )}
          </div>
        </div>

        {/* Pipeline Stages */}
        <PipelineStages 
          currentStage={currentStage}
          progress={progress}
        />

        {/* Error Display */}
        {wsError && (
          <div className="progress-dashboard__error">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <div>
              <p className="progress-dashboard__error-title">Connection Error</p>
              <p className="progress-dashboard__error-message">{wsError}</p>
            </div>
            <button 
              className="progress-dashboard__error-action"
              onClick={reconnect}
            >
              Retry
            </button>
          </div>
        )}

        {/* Log Stream */}
        <LogStream 
          logs={logs}
          decisions={decisions}
          currentStage={currentStage}
        />

        {/* Actions */}
        <div className="progress-dashboard__actions">
          {currentStage && !['completed', 'failed', 'cancelled'].includes(currentStage) && (
            <button
              className="progress-dashboard__cancel"
              onClick={cancelPipeline}
              disabled={!isConnected}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
              Cancel Pipeline
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
