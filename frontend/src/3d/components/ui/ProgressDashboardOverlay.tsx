import { useEffect } from 'react';
import { usePolling } from '../../../hooks/usePolling';
import { PipelineStages } from '../dashboard/PipelineStages';
import { LogStream } from '../dashboard/LogStream';
import './ProgressDashboardOverlay.css';

/**
 * ProgressDashboardOverlay Component
 * 
 * Progress dashboard for ML pipeline execution via REST API polling.
 * Shows pipeline stages, progress, logs, and decision logs.
 * Polls every 60 seconds for updates.
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
    error: pollingError,
    currentStage,
    progress,
    logs,
    decisions,
    cancelPipeline,
    reconnect,
  } = usePolling({
    projectId,
    pollingInterval: 60000, // Poll every 60 seconds (1 minute)
    onCompleted: (result) => {
      console.log('Pipeline completed:', result);
      onComplete?.();
    },
    onFailed: (error, stage) => {
      console.error('Pipeline failed:', error, 'at stage:', stage);
      onError?.(error);
    },
    onError: (error, details) => {
      console.error('Polling error:', error, details);
    },
  });

  // Notify parent of errors
  useEffect(() => {
    if (pollingError) {
      onError?.(pollingError);
    }
  }, [pollingError, onError]);

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
          
          {/* Polling Status */}
          <div className="progress-dashboard__status">
            <div className="status-badge status-badge--polling">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
              Auto-refresh
            </div>
          </div>
        </div>

        {/* Pipeline Stages */}
        <PipelineStages 
          currentStage={currentStage}
          progress={progress}
        />

        {/* Error Display */}
        {pollingError && (
          <div className="progress-dashboard__error">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <div>
              <p className="progress-dashboard__error-title">Update Error</p>
              <p className="progress-dashboard__error-message">{pollingError}</p>
            </div>
            <button 
              className="progress-dashboard__error-action"
              onClick={reconnect}
            >
              Retry Now
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
              disabled={true}
              title="Pipeline cancellation not yet implemented"
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
