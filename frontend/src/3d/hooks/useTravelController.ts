import { useCallback, useRef, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import { Vector3 } from 'three';
import * as TWEEN from '@tweenjs/tween.js';
import type { OrbitControls } from 'three-stdlib';
import { useNavigationStore } from '../store/navigationStore';
import { getNavigationNodeById } from '../config/navigationNodes';
import {
  calculateDestinationCoordinates,
  calculateTakeoffPosition,
  getOverviewPosition,
  getOverviewTarget,
} from '../utils/cameraCalculations';

/**
 * Travel controller hook for camera navigation
 * Implements two-phase camera animation (takeoff + approach)
 * Based on Galaxy1 TravelController architecture
 * 
 * Requirements: 2.3, 3.1, 3.2, 3.3, 3.4, 15.1, 15.2, 15.3, 15.4, 15.5
 */

export interface TravelState {
  isTransitioning: boolean;
  currentTarget: string | null;
  phase: 'idle' | 'takeoff' | 'traveling' | 'landing' | 'focused';
}

export interface TravelControllerReturn {
  travelTo: (targetId: string) => Promise<void>;
  returnToOverview: () => Promise<void>;
  state: TravelState;
}

/**
 * Custom event types for travel lifecycle
 */
export const TRAVEL_EVENTS = {
  START: 'travel:start',
  TAKEOFF_COMPLETE: 'travel:takeoff-complete',
  APPROACH_COMPLETE: 'travel:approach-complete',
  COMPLETE: 'travel:complete',
  RETURN_START: 'travel:return-start',
  RETURN_COMPLETE: 'travel:return-complete',
} as const;

/**
 * Dispatch custom travel event
 */
function dispatchTravelEvent(eventType: string, detail?: any) {
  const event = new CustomEvent(eventType, { detail });
  window.dispatchEvent(event);
}

export function useTravelController(): TravelControllerReturn {
  const { camera, controls } = useThree();
  const orbitControls = controls as OrbitControls | undefined;
  const navigationStore = useNavigationStore();
  
  // Create a TWEEN Group for managing tweens (only once)
  const tweenGroupRef = useRef<TWEEN.Group>();
  if (!tweenGroupRef.current) {
    tweenGroupRef.current = new TWEEN.Group();
  }
  
  // Refs to track active tweens
  const activeTweensRef = useRef<TWEEN.Tween<any>[]>([]);
  const animationFrameRef = useRef<number>();
  
  /**
   * Clean up active tweens
   */
  const cleanupTweens = useCallback(() => {
    activeTweensRef.current.forEach(tween => {
      tween.stop();
    });
    activeTweensRef.current = [];
  }, []);
  
  /**
   * Animation loop for TWEEN.js
   */
  const animate = useCallback(function animateLoop(time?: number) {
    if (tweenGroupRef.current) {
      tweenGroupRef.current.update(time);
    }
    animationFrameRef.current = requestAnimationFrame(animateLoop);
  }, []);
  
  /**
   * Start animation loop if not already running
   */
  const startAnimationLoop = useCallback(() => {
    if (!animationFrameRef.current) {
      animationFrameRef.current = requestAnimationFrame(animate);
    }
  }, [animate]);
  
  /**
   * Travel to a target body with two-phase animation
   * Phase 1: Takeoff (3 seconds) - rise vertically while tracking target
   * Phase 2: Approach (5 seconds) - fly to calculated destination
   * 
   * Requirements: 2.3, 3.1, 3.2, 3.3, 3.4, 15.1, 15.2, 15.3, 15.4, 15.5
   */
  const travelTo = useCallback(async (targetId: string): Promise<void> => {
    // Prevent navigation during transitions
    if (navigationStore.isTransitioning) {
      console.warn('Navigation already in progress. Current phase:', navigationStore.transitionPhase);
      console.warn('Forcing reset to allow navigation...');
      // Force reset if stuck
      navigationStore.setIsTransitioning(false);
      navigationStore.setTransitionPhase('idle');
      // Continue with navigation
    }
    
    console.log('Starting travel to:', targetId);
    
    // Get target body configuration
    const targetBody = getNavigationNodeById(targetId);
    if (!targetBody) {
      console.error(`Target body not found: ${targetId}`);
      return;
    }
    
    // Clean up any existing tweens
    cleanupTweens();
    
    // Start travel in navigation store
    navigationStore.startTravel(targetId);
    
    // Dispatch travel start event
    dispatchTravelEvent(TRAVEL_EVENTS.START, { targetId });
    
    // Store current camera position
    const startPosition = camera.position.clone();
    
    // Calculate positions
    const takeoffPosition = calculateTakeoffPosition(startPosition, targetBody);
    const finalPosition = calculateDestinationCoordinates(targetBody);
    const targetPosition = targetBody.position.clone();
    
    // Store initial distances for progress calculation
    const takeoffDistance = startPosition.distanceTo(takeoffPosition);
    
    return new Promise<void>((resolve) => {
      // ===== PHASE 1: TAKEOFF (3 seconds) =====
      // Rise vertically while starting to track the target
      
      navigationStore.setTransitionPhase('takeoff');
      
      // Create plain object for tweening (TWEEN.js works better with plain objects)
      const tweenStart = { x: startPosition.x, y: startPosition.y, z: startPosition.z };
      
      const takeoffTween = new TWEEN.Tween(tweenStart, tweenGroupRef.current)
        .to({
          x: takeoffPosition.x,
          y: takeoffPosition.y,
          z: takeoffPosition.z,
        }, 3000) // 3 seconds
        .easing(TWEEN.Easing.Cubic.InOut)
        .onUpdate((position) => {
          console.log('Takeoff onUpdate called, position:', position);
          
          // Update camera position from tweened values
          camera.position.set(position.x, position.y, position.z);
          
          // Debug: Log position every 30 frames (roughly once per second at 60fps)
          if (Math.random() < 0.05) {
            console.log('Takeoff position:', camera.position.toArray());
          }
          
          // Update camera target to track the body
          if (orbitControls?.target) {
            orbitControls.target.copy(targetPosition);
          }
          
          // Update lookAt
          camera.lookAt(targetPosition);
          
          // Calculate progress based on distance
          const currentDistance = camera.position.distanceTo(takeoffPosition);
          const progress = Math.max(0, Math.min(1, 1 - (currentDistance / takeoffDistance)));
          navigationStore.setTransitionProgress(progress * 0.375); // 0 to 0.375 for takeoff phase
        })
        .onComplete(() => {
          // Remove takeoff tween from active list
          const index = activeTweensRef.current.indexOf(takeoffTween);
          if (index > -1) {
            activeTweensRef.current.splice(index, 1);
          }
          
          // Takeoff complete, start approach phase
          navigationStore.setTransitionPhase('traveling');
          dispatchTravelEvent(TRAVEL_EVENTS.TAKEOFF_COMPLETE, { targetId });
          
          // ===== PHASE 2: APPROACH (5 seconds) =====
          // Fly to calculated destination
          
          const approachStartPosition = takeoffPosition.clone();
          const approachDistance = approachStartPosition.distanceTo(finalPosition);
          
          // Dispatch event to enable distance-based highlight scaling (Req 16.2, 16.3)
          dispatchTravelEvent('travel:approach-start', { 
            targetId,
            targetPosition: targetPosition.toArray(),
          });
          
          // Create plain object for tweening
          const approachStart = { x: takeoffPosition.x, y: takeoffPosition.y, z: takeoffPosition.z };
          
          const approachTween = new TWEEN.Tween(approachStart, tweenGroupRef.current)
            .to({
              x: finalPosition.x,
              y: finalPosition.y,
              z: finalPosition.z,
            }, 5000) // 5 seconds
            .easing(TWEEN.Easing.Cubic.InOut)
            .onUpdate((position) => {
              // Update camera position from tweened values
              camera.position.set(position.x, position.y, position.z);
              
              // Recalculate destination if body is orbiting (future enhancement)
              // For now, keep target fixed
              
              // Update camera target
              if (orbitControls?.target) {
                orbitControls.target.copy(targetPosition);
              }
              
              // Update lookAt
              camera.lookAt(targetPosition);
              
              // Calculate progress based on distance
              const currentDistance = camera.position.distanceTo(finalPosition);
              const progress = Math.max(0, Math.min(1, 1 - (currentDistance / approachDistance)));
              navigationStore.setTransitionProgress(0.375 + (progress * 0.625)); // 0.375 to 1.0 for approach phase
            })
            .onComplete(() => {
              // Remove approach tween from active list
              const index = activeTweensRef.current.indexOf(approachTween);
              if (index > -1) {
                activeTweensRef.current.splice(index, 1);
              }
              
              // Approach complete
              navigationStore.setTransitionPhase('landing');
              dispatchTravelEvent(TRAVEL_EVENTS.APPROACH_COMPLETE, { targetId });
              
              // Dispatch event to start color transition (Req 16.4)
              dispatchTravelEvent('travel:arrival', { targetId });
              
              // Final camera state update
              navigationStore.setCameraState({
                position: finalPosition,
                target: targetPosition,
                lookAt: targetPosition,
              });
              
              // Complete travel
              navigationStore.completeTravel();
              dispatchTravelEvent(TRAVEL_EVENTS.COMPLETE, { targetId });
              
              resolve();
            })
            .start();
          
          activeTweensRef.current.push(approachTween);
        });
      
      // Start animation loop BEFORE starting the tween
      startAnimationLoop();
      
      // Start the tween with current time
      const now = performance.now();
      takeoffTween.start(now);
      activeTweensRef.current.push(takeoffTween);
    });
  }, [camera, orbitControls, navigationStore, cleanupTweens, startAnimationLoop]);
  
  /**
   * Return to overview position
   * Animate camera back to [0, 500, 500]
   * Duration: 4 seconds with Cubic.InOut easing
   * 
   * Requirements: 3.5
   */
  const returnToOverview = useCallback(async (): Promise<void> => {
    // Prevent if already transitioning
    if (navigationStore.isTransitioning && navigationStore.transitionPhase !== 'focused') {
      console.warn('Navigation already in progress');
      return;
    }
    
    // Clean up any existing tweens
    cleanupTweens();
    
    // Start return in navigation store
    navigationStore.returnToOverview();
    
    // Dispatch return start event
    dispatchTravelEvent(TRAVEL_EVENTS.RETURN_START);
    
    // Store current camera position
    const startPosition = camera.position.clone();
    const startTarget = orbitControls?.target?.clone() || new Vector3(0, 0, 0);
    
    // Calculate overview positions
    const overviewPosition = getOverviewPosition();
    const overviewTarget = getOverviewTarget();
    
    // Store initial distance for progress calculation
    const returnDistance = startPosition.distanceTo(overviewPosition);
    
    return new Promise<void>((resolve) => {
      // Create plain object for tweening
      const returnStart = { x: startPosition.x, y: startPosition.y, z: startPosition.z };
      
      // Animate camera back to overview
      const returnTween = new TWEEN.Tween(returnStart, tweenGroupRef.current)
        .to({
          x: overviewPosition.x,
          y: overviewPosition.y,
          z: overviewPosition.z,
        }, 4000) // 4 seconds
        .easing(TWEEN.Easing.Cubic.InOut)
        .onUpdate((position) => {
          // Update camera position from tweened values
          camera.position.set(position.x, position.y, position.z);
          
          // Calculate progress based on distance
          const currentDistance = camera.position.distanceTo(overviewPosition);
          const progressValue = Math.max(0, Math.min(1, 1 - (currentDistance / returnDistance)));
          
          // Interpolate target
          const currentTarget = new Vector3().lerpVectors(
            startTarget,
            overviewTarget,
            progressValue
          );
          
          if (orbitControls?.target) {
            orbitControls.target.copy(currentTarget);
          }
          
          // Update lookAt
          camera.lookAt(currentTarget);
          
          // Update progress
          navigationStore.setTransitionProgress(progressValue);
        })
        .onComplete(() => {
          // Remove return tween from active list
          const index = activeTweensRef.current.indexOf(returnTween);
          if (index > -1) {
            activeTweensRef.current.splice(index, 1);
          }
          
          // Return complete
          navigationStore.setTransitionPhase('idle');
          navigationStore.setIsTransitioning(false);
          navigationStore.setFocusedBodyId(null);
          navigationStore.setInteractionEnabled(true);
          
          // Final camera state update
          navigationStore.setCameraState({
            position: overviewPosition,
            target: overviewTarget,
            lookAt: overviewTarget,
          });
          
          dispatchTravelEvent(TRAVEL_EVENTS.RETURN_COMPLETE);
          
          resolve();
        })
        .start();
      
      activeTweensRef.current.push(returnTween);
      
      // Start animation loop
      startAnimationLoop();
    });
  }, [camera, orbitControls, navigationStore, cleanupTweens, startAnimationLoop]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupTweens();
    };
  }, [cleanupTweens]);
  
  // Return controller interface
  return {
    travelTo,
    returnToOverview,
    state: {
      isTransitioning: navigationStore.isTransitioning,
      currentTarget: navigationStore.focusedBodyId,
      phase: navigationStore.transitionPhase,
    },
  };
}
