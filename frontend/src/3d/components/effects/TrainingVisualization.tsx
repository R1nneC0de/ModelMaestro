import React, { useMemo, useEffect, useState } from 'react';
import * as THREE from 'three';
import { DataUploadAnimation } from './DataUploadAnimation';
import { TrainingProgressEffect } from './TrainingProgressEffect';
import { ConnectionPath } from './ConnectionPath';
import { ModelMoon } from './ModelMoon';
import { useNavigationStore } from '../../store/navigationStore';
import { useTrainingProgress } from '../../../hooks/useTrainingProgress';
import { NAVIGATION_NODES } from '../../config/navigationNodes';

/**
 * TrainingVisualization Component
 * 
 * Manages all training-related visual effects:
 * - Data upload particle animation (Task 12.1)
 * - Training progress visualization (Task 12.2)
 * - Training completion animation (Task 12.3)
 * 
 * Requirements: 11.2, 11.3, 11.4, 12.3
 */

export const TrainingVisualization: React.FC = () => {
  const { 
    showUploadAnimation,
    currentProjectId,
    isTraining,
    showCompletionAnimation,
    updateTrainingProgress,
    completeTrainingVisualization,
  } = useNavigationStore();
  
  // Track completed models (moons)
  const [completedModels, setCompletedModels] = useState<string[]>([]);
  
  // Monitor training progress (Req 11.3, 14.2)
  const { 
    progress: trainingProgressData, 
    isComplete,
    projectData,
  } = useTrainingProgress({
    projectId: currentProjectId,
    enabled: isTraining && !!currentProjectId,
  });
  
  // Find Create Model and Past Models node positions
  const createModelNode = useMemo(() => {
    return NAVIGATION_NODES.find(node => node.id === 'create-model');
  }, []);
  
  const pastModelsNode = useMemo(() => {
    return NAVIGATION_NODES.find(node => node.id === 'past-models');
  }, []);
  
  // Calculate upload start position (from screen center, slightly above)
  const uploadStartPosition = useMemo(() => {
    // Position in front of camera, slightly to the left and up
    // This simulates particles coming from the upload UI area
    return new THREE.Vector3(-100, 600, 400);
  }, []);
  
  // Create Model node end position
  const uploadEndPosition = useMemo(() => {
    if (!createModelNode) return new THREE.Vector3(0, 0, 0);
    return createModelNode.position.clone();
  }, [createModelNode]);
  
  // Update training progress in store when it changes (Req 11.3)
  useEffect(() => {
    if (trainingProgressData && trainingProgressData.progress !== undefined) {
      // Convert progress (0-100) to normalized value (0-1)
      const normalizedProgress = trainingProgressData.progress / 100;
      updateTrainingProgress(normalizedProgress);
    }
  }, [trainingProgressData, updateTrainingProgress]);
  
  // Handle training completion (Req 11.4)
  useEffect(() => {
    if (isComplete && isTraining && currentProjectId) {
      completeTrainingVisualization();
      // Add completed model to the list (will create a new moon)
      setCompletedModels(prev => [...prev, currentProjectId]);
    }
  }, [isComplete, isTraining, currentProjectId, completeTrainingVisualization]);
  
  // Calculate current training progress (0-1)
  const currentProgress = useMemo(() => {
    if (!trainingProgressData) return 0;
    return trainingProgressData.progress / 100;
  }, [trainingProgressData]);
  
  const handleUploadAnimationComplete = () => {
    console.log('Upload animation completed');
  };
  
  const handleConnectionComplete = () => {
    console.log('Connection animation completed');
  };
  
  return (
    <>
      {/* Data Upload Animation (Task 12.1) */}
      {showUploadAnimation && (
        <DataUploadAnimation
          startPosition={uploadStartPosition}
          endPosition={uploadEndPosition}
          onComplete={handleUploadAnimationComplete}
          particleCount={50}
        />
      )}
      
      {/* Training Progress Visualization (Task 12.2) */}
      {isTraining && createModelNode && (
        <TrainingProgressEffect
          nodePosition={createModelNode.position}
          nodeRadius={createModelNode.circleRadius}
          progress={currentProgress}
          isActive={isTraining}
        />
      )}
      
      {/* Training Completion Animation (Task 12.3) */}
      {showCompletionAnimation && createModelNode && pastModelsNode && (
        <ConnectionPath
          startPosition={createModelNode.position}
          endPosition={pastModelsNode.position}
          color="#4DD0E1"
          opacity={0.4}
          particleCount={100}
          animationDuration={3.0}
          onComplete={handleConnectionComplete}
        />
      )}
      
      {/* Model Moons - one for each completed training (Task 12.3) */}
      {pastModelsNode && completedModels.map((modelId, index) => (
        <ModelMoon
          key={modelId}
          parentPosition={pastModelsNode.position}
          orbitRadius={pastModelsNode.circleRadius * 2}
          orbitSpeed={0.0003}
          size={3}
          color="#FFB84D"
          index={index}
        />
      ))}
    </>
  );
};
