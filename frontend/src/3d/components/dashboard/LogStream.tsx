import { useState, useEffect, useRef } from 'react';
import { LogEntry, DecisionLog, PipelineStage } from '../../../hooks/useWebSocket';
import './LogStream.css';

/**
 * LogStream Component
 * 
 * Real-time log viewer with expandable decision logs.
 * Shows pipeline logs, decision reasoning, and stage-specific status.
 * 
 * Requirements: 2.3, 6.2, 6.3, 6.4
 */

export interface LogStreamProps {
  logs: LogEntry[];
  decisions: DecisionLog[];
  currentStage: PipelineStage | null;
}

type TabType = 'logs' | 'decisions';

export function LogStream({ logs, decisions }: LogStreamProps) {
  const [activeTab, setActiveTab] = useState<TabType>('logs');
  const [expandedDecisions, setExpandedDecisions] = useState<Set<number>>(new Set());
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, decisions, autoScroll]);

  // Detect manual scroll to disable auto-scroll
  const handleScroll = () => {
    if (!containerRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    
    if (isAtBottom !== autoScroll) {
      setAutoScroll(isAtBottom);
    }
  };

  const toggleDecision = (index: number) => {
    setExpandedDecisions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'error':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        );
      case 'warning':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        );
      case 'info':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
        );
      default:
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 11 12 14 22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
        );
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false 
    });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
  };

  return (
    <div className="log-stream">
      {/* Header with Tabs */}
      <div className="log-stream__header">
        <div className="log-stream__tabs">
          <button
            className={`log-stream__tab ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => setActiveTab('logs')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            Logs
            {logs.length > 0 && (
              <span className="log-stream__count">{logs.length}</span>
            )}
          </button>
          <button
            className={`log-stream__tab ${activeTab === 'decisions' ? 'active' : ''}`}
            onClick={() => setActiveTab('decisions')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
            Decisions
            {decisions.length > 0 && (
              <span className="log-stream__count">{decisions.length}</span>
            )}
          </button>
        </div>

        {/* Auto-scroll Toggle */}
        <button
          className={`log-stream__auto-scroll ${autoScroll ? 'active' : ''}`}
          onClick={() => setAutoScroll(!autoScroll)}
          title={autoScroll ? 'Auto-scroll enabled' : 'Auto-scroll disabled'}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="17 13 12 18 7 13" />
            <polyline points="17 6 12 11 7 6" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div 
        ref={containerRef}
        className="log-stream__content"
        onScroll={handleScroll}
      >
        {activeTab === 'logs' ? (
          <div className="log-stream__logs">
            {logs.length === 0 ? (
              <div className="log-stream__empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <p>No logs yet</p>
                <span>Logs will appear here as the pipeline runs</span>
              </div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className={`log-entry log-entry--${log.level}`}>
                  <div className="log-entry__icon">
                    {getLogIcon(log.level)}
                  </div>
                  <div className="log-entry__content">
                    <div className="log-entry__header">
                      <span className="log-entry__timestamp">
                        {formatTimestamp(log.timestamp)}
                      </span>
                      {log.stage_display && (
                        <span className="log-entry__stage">{log.stage_display}</span>
                      )}
                    </div>
                    <p className="log-entry__message">{log.message}</p>
                  </div>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        ) : (
          <div className="log-stream__decisions">
            {decisions.length === 0 ? (
              <div className="log-stream__empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 20h9" />
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                </svg>
                <p>No decisions yet</p>
                <span>AI decisions will appear here as they're made</span>
              </div>
            ) : (
              decisions.map((decision, index) => {
                const isExpanded = expandedDecisions.has(index);
                const confidenceColor = getConfidenceColor(decision.confidence);
                
                return (
                  <div 
                    key={index} 
                    className={`decision-entry ${isExpanded ? 'expanded' : ''}`}
                  >
                    <button
                      className="decision-entry__header"
                      onClick={() => toggleDecision(index)}
                    >
                      <div className="decision-entry__header-content">
                        <div className="decision-entry__title-row">
                          <span className="decision-entry__type">{decision.decision_type}</span>
                          <span className={`decision-entry__confidence decision-entry__confidence--${confidenceColor}`}>
                            {decision.confidence_percentage}% confidence
                          </span>
                        </div>
                        <p className="decision-entry__decision">{decision.decision}</p>
                        <div className="decision-entry__meta">
                          <span className="decision-entry__timestamp">
                            {formatTimestamp(decision.timestamp)}
                          </span>
                          <span className="decision-entry__stage">{decision.stage_display}</span>
                        </div>
                      </div>
                      <svg 
                        className="decision-entry__chevron"
                        width="20" 
                        height="20" 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor" 
                        strokeWidth="2"
                      >
                        <polyline points="6 9 12 15 18 9" />
                      </svg>
                    </button>
                    
                    {isExpanded && (
                      <div className="decision-entry__details">
                        <div className="decision-entry__reasoning">
                          <h4 className="decision-entry__reasoning-title">Reasoning</h4>
                          <p className="decision-entry__reasoning-text">{decision.reasoning}</p>
                        </div>
                        
                        {decision.metadata && Object.keys(decision.metadata).length > 0 && (
                          <div className="decision-entry__metadata">
                            <h4 className="decision-entry__metadata-title">Additional Details</h4>
                            <div className="decision-entry__metadata-grid">
                              {Object.entries(decision.metadata).map(([key, value]) => (
                                <div key={key} className="decision-entry__metadata-item">
                                  <span className="decision-entry__metadata-key">{key}</span>
                                  <span className="decision-entry__metadata-value">
                                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
            <div ref={logsEndRef} />
          </div>
        )}
      </div>
    </div>
  );
}
