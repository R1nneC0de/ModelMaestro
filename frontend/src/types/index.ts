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

export interface ModelResults {
  modelId: string;
  downloadUrl: string;
  apiEndpoint?: string;
  metrics: {
    accuracy: number;
    [key: string]: number;
  };
}
