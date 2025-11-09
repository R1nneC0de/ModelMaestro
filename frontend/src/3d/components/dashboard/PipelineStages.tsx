import React from 'react';
import { PipelineStage } from '../../../hooks/useWebSocket';
import './PipelineStages.css';

/**
 * PipelineStages Component
 * 
 * Visual representation of ML pipeline stages with progress indicators.
 * Shows current stage, progress percentage, and estimated time remaining.
 * 
 * Requirements: 2.2, 2.3, 2.4
 */

export interface PipelineStagesProps {
  currentStage: PipelineStage | null;
  progress: number;
  estimatedTimeRemaining?: number;
}

interface StageConfig {
  id: PipelineStage;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const STAGES: StageConfig[] = [
  {
    id: 'analyzing',
    label: 'Problem Analysis',
    description: 'Understanding your data and prediction goal',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </svg>
    ),
  },
  {
    id: 'processing',
    label: 'Data Processing',
    description: 'Cleaning and preparing your dataset',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
        <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
        <line x1="12" y1="22.08" x2="12" y2="12" />
      </svg>
    ),
  },
  {
    id: 'labeling',
    label: 'Data Labeling',
    description: 'Handling unlabeled data if needed',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
        <line x1="7" y1="7" x2="7.01" y2="7" />
      </svg>
    ),
  },
  {
    id: 'model_selection',
    label: 'Model Selection',
    description: 'Choosing the best algorithm',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
      </svg>
    ),
  },
  {
    id: 'training',
    label: 'Model Training',
    description: 'Training your ML model',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v6m0 6v6" />
        <path d="m4.93 4.93 4.24 4.24m5.66 5.66 4.24 4.24" />
        <path d="M1 12h6m6 0h6" />
        <path d="m4.93 19.07 4.24-4.24m5.66-5.66 4.24-4.24" />
      </svg>
    ),
  },
  {
    id: 'evaluation',
    label: 'Model Evaluation',
    description: 'Testing model performance',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    id: 'deployment',
    label: 'Model Deployment',
    description: 'Deploying to production',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
    ),
  },
];

const getStageStatus = (
  stageId: PipelineStage,
  currentStage: PipelineStage | null
): 'completed' | 'active' | 'pending' | 'failed' => {
  if (!currentStage) return 'pending';
  
  if (currentStage === 'failed') {
    const currentIndex = STAGES.findIndex(s => s.id === currentStage);
    const stageIndex = STAGES.findIndex(s => s.id === stageId);
    if (stageIndex === currentIndex) return 'failed';
    if (stageIndex < currentIndex) return 'completed';
    return 'pending';
  }
  
  if (currentStage === 'completed') {
    return 'completed';
  }
  
  const currentIndex = STAGES.findIndex(s => s.id === currentStage);
  const stageIndex = STAGES.findIndex(s => s.id === stageId);
  
  if (stageIndex < currentIndex) return 'completed';
  if (stageIndex === currentIndex) return 'active';
  return 'pending';
};

const formatTimeRemaining = (seconds: number): string => {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m`;
  }
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
};

export function PipelineStages({ 
  currentStage, 
  progress,
  estimatedTimeRemaining 
}: PipelineStagesProps) {
  const progressPercentage = Math.round(progress * 100);
  
  return (
    <div className="pipeline-stages">
      {/* Progress Bar */}
      <div className="pipeline-stages__progress-section">
        <div className="pipeline-stages__progress-header">
          <div className="pipeline-stages__progress-info">
            <span className="pipeline-stages__progress-label">Overall Progress</span>
            <span className="pipeline-stages__progress-percentage">{progressPercentage}%</span>
          </div>
          {estimatedTimeRemaining !== undefined && estimatedTimeRemaining > 0 && (
            <span className="pipeline-stages__time-remaining">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              {formatTimeRemaining(estimatedTimeRemaining)} remaining
            </span>
          )}
        </div>
        
        <div className="pipeline-stages__progress-bar">
          <div 
            className="pipeline-stages__progress-fill"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Stage List */}
      <div className="pipeline-stages__list">
        {STAGES.map((stage, index) => {
          const status = getStageStatus(stage.id, currentStage);
          const isActive = status === 'active';
          
          return (
            <div 
              key={stage.id}
              className={`pipeline-stage pipeline-stage--${status}`}
            >
              {/* Connector Line */}
              {index > 0 && (
                <div className="pipeline-stage__connector" />
              )}
              
              {/* Stage Icon */}
              <div className="pipeline-stage__icon-wrapper">
                <div className="pipeline-stage__icon">
                  {status === 'completed' ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : status === 'failed' ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  ) : (
                    stage.icon
                  )}
                </div>
                {isActive && (
                  <div className="pipeline-stage__pulse" />
                )}
              </div>
              
              {/* Stage Content */}
              <div className="pipeline-stage__content">
                <div className="pipeline-stage__header">
                  <h3 className="pipeline-stage__label">{stage.label}</h3>
                  {isActive && (
                    <span className="pipeline-stage__badge">In Progress</span>
                  )}
                </div>
                <p className="pipeline-stage__description">{stage.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
