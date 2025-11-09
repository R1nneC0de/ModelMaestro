// TypeScript interfaces for the application

export interface TrainingSession {
  id: string;
  datasetName: string;
  prompt: string;
  status: 'training' | 'completed' | 'failed';
  timestamp: string;
  metrics?: {
    accuracy: number;
    precision?: number;
    recall?: number;
  };
  modelId?: string;
}

export interface TrainingSubmission {
  file: File;
  prompt: string;
}

export interface TrainingProgress {
  stage: 'analyzing' | 'processing' | 'training' | 'evaluating';
  progress: number;
  message: string;
}

export interface ModelMetrics {
  [key: string]: number;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  roc_auc?: number;
  rmse?: number;
  mae?: number;
  r2?: number;
}

export interface ModelInfo {
  id: string;
  project_id: string;
  architecture: string;
  vertex_job_id?: string;
  endpoint_url?: string;
  artifact_path?: string;
  metrics: ModelMetrics;
  hyperparameters: Record<string, any>;
  created_at: string;
  report?: {
    summary: string;
    decision: 'ACCEPT' | 'REJECT';
    reasoning: string;
    recommendations?: string[];
  };
}

export interface ModelResults {
  modelId: string;
  downloadUrl: string;
  apiEndpoint?: string;
  metrics: ModelMetrics;
  model?: ModelInfo;
}

export interface PredictionRequest {
  instances: Array<Record<string, any>>;
  parameters?: Record<string, any>;
}

export interface PredictionResponse {
  predictions: Array<Record<string, any>>;
  model_id: string;
  endpoint_id?: string;
  deployed_model_id?: string;
}
