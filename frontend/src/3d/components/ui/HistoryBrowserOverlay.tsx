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
  const { data: sessions, isLoading, error, refetch } = useHistory();
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

  return (
    <div className="history-browser-overlay">
      <div className="history-browser-overlay__header">
        <h2 id="overlay-title" className="history-browser-overlay__title">
          Past Models
        </h2>
        <p className="history-browser-overlay__subtitle">
          Browse your training history and view model performance
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
      {!isLoading && !error && (!sessions || sessions.length === 0) && (
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
      {!isLoading && !error && sessions && sessions.length > 0 && (
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
  const statusColors = {
    training: '#FBBC04',
    completed: '#34A853',
    failed: '#EA4335',
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
        </span>
      </div>

      <p className="session-card__prompt">{session.prompt}</p>

      <div className="session-card__footer">
        <span className="session-card__date">{formatDate(session.timestamp)}</span>
        {session.metrics && (
          <span className="session-card__accuracy">
            Accuracy: {(session.metrics.accuracy * 100).toFixed(1)}%
          </span>
        )}
      </div>

      {session.status === 'training' && (
        <div className="session-card__progress">
          <div className="session-card__progress-bar" />
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
        </div>
      )}

      {session && (
        <div className="session-detail__content">
          <h2 className="session-detail__title">{session.datasetName}</h2>
          <p className="session-detail__prompt">{session.prompt}</p>

          {session.metrics && (
            <div className="session-detail__metrics">
              <h3>Performance Metrics</h3>
              <div className="session-detail__metrics-grid">
                <div className="session-detail__metric">
                  <span className="session-detail__metric-label">Accuracy</span>
                  <span className="session-detail__metric-value">
                    {(session.metrics.accuracy * 100).toFixed(2)}%
                  </span>
                </div>
                {session.metrics.precision !== undefined && (
                  <div className="session-detail__metric">
                    <span className="session-detail__metric-label">Precision</span>
                    <span className="session-detail__metric-value">
                      {(session.metrics.precision * 100).toFixed(2)}%
                    </span>
                  </div>
                )}
                {session.metrics.recall !== undefined && (
                  <div className="session-detail__metric">
                    <span className="session-detail__metric-label">Recall</span>
                    <span className="session-detail__metric-value">
                      {(session.metrics.recall * 100).toFixed(2)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {session.modelId && (
            <div className="session-detail__actions">
              <button className="session-detail__button session-detail__button--primary">
                Download Model
              </button>
              <button className="session-detail__button session-detail__button--secondary">
                View Full Report
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
