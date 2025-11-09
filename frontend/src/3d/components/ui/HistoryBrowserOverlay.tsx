import { useState } from 'react';
import { useHistory } from '../../../hooks/useHistory';
import { useSessionDetail } from '../../../hooks/useSessionDetail';
import { TrainingSession } from '../../../types';
import './HistoryBrowserOverlay.css';

/**
 * HistoryBrowserOverlay Component
 * 
 * Embedded in Past Models section overlay.
 * Displays scrollable list of training sessions with detail view.
 * 
 * Requirements: 12.1, 12.2, 12.5, 14.3
 */

export interface HistoryBrowserOverlayProps {
  visible: boolean;
}

export function HistoryBrowserOverlay({ visible }: HistoryBrowserOverlayProps) {
  // Task 3.1: Fetch projects from backend with pagination
  const { data, isLoading, error, refetch } = useHistory();
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  if (!visible) {
    return null;
  }

  const handleSessionClick = (sessionId: string) => {
    setSelectedSessionId(sessionId);
  };

  const handleBackToList = () => {
    setSelectedSessionId(null);
  };

  // Show detail view if a session is selected
  if (selectedSessionId) {
    return (
      <SessionDetailView
        sessionId={selectedSessionId}
        onBack={handleBackToList}
      />
    );
  }

  // Extract sessions from response
  const sessions = data?.sessions || [];
  const total = data?.total || 0;

  return (
    <div className="history-browser-overlay">
      <div className="history-browser-overlay__header">
        <h2 id="overlay-title" className="history-browser-overlay__title">
          Past Models
        </h2>
        <p className="history-browser-overlay__subtitle">
          Browse your training history and view model performance {total > 0 && `(${total} total)`}
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="history-browser-overlay__loading">
          <div className="history-browser-overlay__spinner" />
          <p>Loading training history...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="history-browser-overlay__error">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h3>Failed to load training history</h3>
          <p>{(error as Error)?.message || 'Please try again later'}</p>
          <button onClick={() => refetch()} className="history-browser-overlay__retry">
            Retry
          </button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && sessions.length === 0 && (
        <div className="history-browser-overlay__empty">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          <h3>No training history yet</h3>
          <p>Start your first training session from the Create Model section</p>
        </div>
      )}

      {/* Session List */}
      {!isLoading && !error && sessions.length > 0 && (
        <div className="history-browser-overlay__list">
          {sessions.map((session, index) => (
            <SessionCard
              key={session.id}
              session={session}
              index={index}
              onClick={() => handleSessionClick(session.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * SessionCard Component
 * Displays a single training session in the list
 */
interface SessionCardProps {
  session: TrainingSession;
  index: number;
  onClick: () => void;
}

function SessionCard({ session, index, onClick }: SessionCardProps) {
  // Task 3.2: Map ProjectStatus to visual indicators
  // training=yellow, completed=green, failed=red
  const statusColors = {
    training: '#FBBC04', // Yellow
    completed: '#34A853', // Green
    failed: '#EA4335', // Red
  };

  const statusLabels = {
    training: 'Training',
    completed: 'Completed',
    failed: 'Failed',
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Task 3.2: Display progress percentage
  const progress = (session as any).progress || 0;

  return (
    <div
      className="session-card"
      onClick={onClick}
      style={{
        animationDelay: `${index * 0.05}s`,
      }}
    >
      <div className="session-card__header">
        <h3 className="session-card__title">{session.datasetName}</h3>
        <span
          className="session-card__status"
          style={{ color: statusColors[session.status] }}
        >
          {statusLabels[session.status]}
          {session.status === 'training' && progress > 0 && ` (${progress}%)`}
        </span>
      </div>

      <p className="session-card__prompt">{session.prompt}</p>

      <div className="session-card__footer">
        <span className="session-card__date">{formatDate(session.timestamp)}</span>
        {session.metrics && session.metrics.accuracy !== undefined && (
          <span className="session-card__accuracy">
            Accuracy: {(session.metrics.accuracy * 100).toFixed(1)}%
          </span>
        )}
      </div>

      {/* Task 3.2: Show progress bar for training sessions */}
      {session.status === 'training' && progress > 0 && (
        <div className="session-card__progress">
          <div 
            className="session-card__progress-bar" 
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
}

/**
 * SessionDetailView Component
 * Displays detailed information about a selected session
 */
interface SessionDetailViewProps {
  sessionId: string;
  onBack: () => void;
}

function SessionDetailView({ sessionId, onBack }: SessionDetailViewProps) {
  const { data: session, isLoading, error } = useSessionDetail(sessionId);

  return (
    <div className="session-detail">
      <div className="session-detail__header">
        <button onClick={onBack} className="session-detail__back">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          Back to List
        </button>
      </div>

      {isLoading && (
        <div className="session-detail__loading">
          <div className="history-browser-overlay__spinner" />
          <p>Loading session details...</p>
        </div>
      )}

      {error && (
        <div className="session-detail__error">
          <p>Failed to load session details</p>
          <p className="session-detail__error-message">
            {(error as Error)?.message || 'Please try again later'}
          </p>
        </div>
      )}

      {session && (
        <div className="session-detail__content">
          <h2 className="session-detail__title">{session.datasetName}</h2>
          <p className="session-detail__prompt">{session.prompt}</p>

          {/* Task 3.3: Show metrics and evaluation report */}
          {session.metrics && (
            <div className="session-detail__metrics">
              <h3>Performance Metrics</h3>
              <div className="session-detail__metrics-grid">
                {Object.entries(session.metrics).map(([key, value]) => (
                  <div key={key} className="session-detail__metric">
                    <span className="session-detail__metric-label">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span className="session-detail__metric-value">
                      {typeof value === 'number' 
                        ? (value < 1 ? `${(value * 100).toFixed(2)}%` : value.toFixed(4))
                        : value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Task 3.3: Display evaluation report if available */}
          {(session as any).report && (
            <div className="session-detail__report">
              <h3>Evaluation Report</h3>
              <div className="session-detail__report-content">
                <p><strong>Decision:</strong> {(session as any).report.decision}</p>
                <p><strong>Reasoning:</strong> {(session as any).report.reasoning}</p>
                {(session as any).report.recommendations && (
                  <div>
                    <strong>Recommendations:</strong>
                    <ul>
                      {(session as any).report.recommendations.map((rec: string, idx: number) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Task 3.3: Display prediction endpoint if available */}
          {(session as any).predictionEndpoint && (
            <div className="session-detail__endpoint">
              <h3>Prediction API</h3>
              <div className="session-detail__endpoint-content">
                <code>{(session as any).predictionEndpoint}</code>
                <button 
                  className="session-detail__copy-button"
                  onClick={() => navigator.clipboard.writeText((session as any).predictionEndpoint)}
                >
                  Copy
                </button>
              </div>
            </div>
          )}

          {session.modelId && (
            <div className="session-detail__actions">
              <button 
                className="session-detail__button session-detail__button--primary"
                onClick={() => window.location.href = `/models/${session.modelId}`}
              >
                View Full Report
              </button>
              {(session as any).predictionEndpoint && (
                <button 
                  className="session-detail__button session-detail__button--secondary"
                  onClick={() => window.location.href = `/models/${session.modelId}/predict`}
                >
                  Test Predictions
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
