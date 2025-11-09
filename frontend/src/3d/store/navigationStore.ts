import { create } from 'zustand';
import { Vector3 } from 'three';

/**
 * Navigation state types
 * Requirements: 3.5, 15.4
 */

export type NavigationView = 'overview' | 'focused';
export type TransitionPhase = 'idle' | 'takeoff' | 'traveling' | 'landing' | 'focused';

export interface CameraState {
  position: Vector3;
  target: Vector3;
  lookAt: Vector3;
}

export interface NavigationState {
  // Current state
  currentView: NavigationView;
  focusedBodyId: string | null;
  
  // Transition state
  isTransitioning: boolean;
  transitionPhase: TransitionPhase;
  transitionProgress: number;  // 0 to 1
  
  // Camera state
  cameraPosition: Vector3;
  cameraTarget: Vector3;
  cameraLookAt: Vector3;
  
  // Interaction state
  hoveredBodyId: string | null;
  interactionEnabled: boolean;
  
  // History
  navigationHistory: string[];  // Stack of visited body IDs
  
  // Training visualization state (Req 11.2, 11.3, 11.4)
  showUploadAnimation: boolean;
  currentProjectId: string | null;
  isTraining: boolean;
  trainingProgress: number;  // 0 to 1
  showCompletionAnimation: boolean;
  
  // Actions
  setCurrentView: (view: NavigationView) => void;
  setFocusedBodyId: (id: string | null) => void;
  setIsTransitioning: (transitioning: boolean) => void;
  setTransitionPhase: (phase: TransitionPhase) => void;
  setTransitionProgress: (progress: number) => void;
  setCameraState: (state: Partial<CameraState>) => void;
  setHoveredBodyId: (id: string | null) => void;
  setInteractionEnabled: (enabled: boolean) => void;
  addToHistory: (id: string) => void;
  clearHistory: () => void;
  
  // Training visualization actions
  triggerUploadAnimation: () => void;
  startTrainingVisualization: (projectId: string) => void;
  updateTrainingProgress: (progress: number) => void;
  completeTrainingVisualization: () => void;
  
  // Composite actions
  startTravel: (targetId: string) => void;
  completeTravel: () => void;
  returnToOverview: () => void;
}

/**
 * Navigation store using Zustand
 * Manages all navigation state including camera position, transitions, and interaction
 * Requirements: 3.5, 15.4
 */
export const useNavigationStore = create<NavigationState>((set, get) => ({
  // Initial state - overview position
  currentView: 'overview',
  focusedBodyId: null,
  
  // Transition state
  isTransitioning: false,
  transitionPhase: 'idle',
  transitionProgress: 0,
  
  // Camera state - default overview position [0, 500, 500]
  cameraPosition: new Vector3(0, 500, 500),
  cameraTarget: new Vector3(0, 0, 0),
  cameraLookAt: new Vector3(0, 0, 0),
  
  // Interaction state
  hoveredBodyId: null,
  interactionEnabled: true,
  
  // History
  navigationHistory: [],
  
  // Training visualization state
  showUploadAnimation: false,
  currentProjectId: null,
  isTraining: false,
  trainingProgress: 0,
  showCompletionAnimation: false,
  
  // Basic setters
  setCurrentView: (view) => set({ currentView: view }),
  
  setFocusedBodyId: (id) => set({ focusedBodyId: id }),
  
  setIsTransitioning: (transitioning) => set({ isTransitioning: transitioning }),
  
  setTransitionPhase: (phase) => set({ transitionPhase: phase }),
  
  setTransitionProgress: (progress) => set({ transitionProgress: progress }),
  
  setCameraState: (state) => set((prev) => ({
    cameraPosition: state.position ?? prev.cameraPosition,
    cameraTarget: state.target ?? prev.cameraTarget,
    cameraLookAt: state.lookAt ?? prev.cameraLookAt,
  })),
  
  setHoveredBodyId: (id) => set({ hoveredBodyId: id }),
  
  setInteractionEnabled: (enabled) => set({ interactionEnabled: enabled }),
  
  addToHistory: (id) => set((state) => ({
    navigationHistory: [...state.navigationHistory, id],
  })),
  
  clearHistory: () => set({ navigationHistory: [] }),
  
  // Training visualization actions
  
  /**
   * Trigger upload animation (Req 11.2)
   */
  triggerUploadAnimation: () => {
    set({ showUploadAnimation: true });
    // Auto-hide after animation completes (2 seconds + buffer)
    setTimeout(() => {
      set({ showUploadAnimation: false });
    }, 2500);
  },
  
  /**
   * Start training visualization (Req 11.3)
   */
  startTrainingVisualization: (projectId) => {
    set({
      currentProjectId: projectId,
      isTraining: true,
      trainingProgress: 0,
    });
  },
  
  /**
   * Update training progress (Req 11.3)
   */
  updateTrainingProgress: (progress) => {
    set({ trainingProgress: progress });
  },
  
  /**
   * Complete training visualization (Req 11.4)
   */
  completeTrainingVisualization: () => {
    set({
      isTraining: false,
      trainingProgress: 1,
      showCompletionAnimation: true,
    });
    // Auto-hide completion animation after it plays
    setTimeout(() => {
      set({ showCompletionAnimation: false });
    }, 5000);
  },
  
  // Composite actions
  
  /**
   * Start travel to a target body
   * Disables interaction and sets up transition state
   */
  startTravel: (targetId) => {
    const state = get();
    
    // Don't start if already transitioning
    if (state.isTransitioning) {
      return;
    }
    
    set({
      isTransitioning: true,
      transitionPhase: 'takeoff',
      transitionProgress: 0,
      focusedBodyId: targetId,
      interactionEnabled: false,
      currentView: 'focused',
    });
    
    // Add to history
    get().addToHistory(targetId);
  },
  
  /**
   * Complete travel transition
   * Re-enables interaction and sets final state
   */
  completeTravel: () => {
    set({
      isTransitioning: false,
      transitionPhase: 'focused',
      transitionProgress: 1,
      interactionEnabled: true,
    });
  },
  
  /**
   * Return to overview state
   * Clears focused body and resets camera
   */
  returnToOverview: () => {
    set({
      currentView: 'overview',
      focusedBodyId: null,
      isTransitioning: true,
      transitionPhase: 'traveling',
      transitionProgress: 0,
      interactionEnabled: false,
      // Camera will be reset by the travel controller
    });
  },
}));

/**
 * Selector hooks for common state access patterns
 */

export const useIsTransitioning = () => useNavigationStore((state) => state.isTransitioning);
export const useFocusedBodyId = () => useNavigationStore((state) => state.focusedBodyId);
export const useCurrentView = () => useNavigationStore((state) => state.currentView);
export const useInteractionEnabled = () => useNavigationStore((state) => state.interactionEnabled);
export const useTransitionPhase = () => useNavigationStore((state) => state.transitionPhase);
export const useCameraState = () => useNavigationStore((state) => ({
  position: state.cameraPosition,
  target: state.cameraTarget,
  lookAt: state.cameraLookAt,
}));
