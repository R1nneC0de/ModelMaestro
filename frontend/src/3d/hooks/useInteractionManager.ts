import { useEffect, useRef, useCallback, useState } from 'react';
import { Raycaster, Vector2, Camera, Object3D, Intersection } from 'three';

/**
 * useInteractionManager Hook
 * Manages raycasting and user input detection for celestial bodies
 * 
 * Requirements:
 * - 2.1: Highlight objects on hover within 100ms
 * - 2.2: Display UI overlay with section name on hover
 * - 2.3: Initiate camera flight on click
 * - 3.5: Prevent navigation during transitions
 * - 15.4: Support touch input for mobile devices
 */

export interface InteractionManagerConfig {
  camera: Camera | null;
  domElement: HTMLElement | null;
  interactiveObjects: Object3D[];
  enabled?: boolean;
  hoverDebounceMs?: number;
}

export interface InteractionManagerReturn {
  hoveredObjectId: string | null;
  clickedObjectId: string | null;
  isHovering: boolean;
  clearHover: () => void;
  clearClick: () => void;
}

/**
 * Custom hook for managing raycasting and user interactions
 * 
 * Features:
 * - Mouse and touch input detection
 * - Raycasting for object intersection
 * - Hover event emission with debouncing (100ms)
 * - Click event emission
 * - Enabled/disabled state management
 */
export function useInteractionManager({
  camera,
  domElement,
  interactiveObjects,
  enabled = true,
  hoverDebounceMs = 100,
}: InteractionManagerConfig): InteractionManagerReturn {
  const raycasterRef = useRef<Raycaster>(new Raycaster());
  const mouseRef = useRef<Vector2>(new Vector2());
  const hoverTimeoutRef = useRef<number | null>(null);
  const lastHoveredRef = useRef<string | null>(null);
  
  const [hoveredObjectId, setHoveredObjectId] = useState<string | null>(null);
  const [clickedObjectId, setClickedObjectId] = useState<string | null>(null);
  const [isHovering, setIsHovering] = useState(false);

  /**
   * Convert screen coordinates to normalized device coordinates (-1 to +1)
   */
  const updateMousePosition = useCallback((clientX: number, clientY: number) => {
    if (!domElement) return;
    
    const rect = domElement.getBoundingClientRect();
    mouseRef.current.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  }, [domElement]);

  /**
   * Perform raycasting to detect intersections with interactive objects
   */
  const performRaycast = useCallback((): Intersection | null => {
    if (!camera || !enabled || interactiveObjects.length === 0) {
      return null;
    }

    // Update raycaster with current camera and mouse position
    raycasterRef.current.setFromCamera(mouseRef.current, camera);

    // Check for intersections with interactive objects
    const intersections = raycasterRef.current.intersectObjects(interactiveObjects, true);

    // Return the closest intersection
    return intersections.length > 0 ? intersections[0] : null;
  }, [camera, enabled, interactiveObjects]);

  /**
   * Get the ID from an intersected object
   * Traverses up the object hierarchy to find the root interactive object
   */
  const getObjectId = useCallback((object: Object3D): string | null => {
    let current: Object3D | null = object;
    
    while (current) {
      // Check if this object has a userData.id
      if (current.userData && current.userData.id) {
        return current.userData.id;
      }
      
      // Check if this object has a name that matches our celestial body IDs
      if (current.name && (
        current.name === 'create-model' ||
        current.name === 'past-models' ||
        current.name === 'info'
      )) {
        return current.name;
      }
      
      current = current.parent;
    }
    
    return null;
  }, []);

  /**
   * Handle mouse move events for hover detection
   */
  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!enabled) return;

    updateMousePosition(event.clientX, event.clientY);

    // Clear existing hover timeout
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }

    // Debounce hover detection (Req 2.1: 100ms threshold)
    hoverTimeoutRef.current = setTimeout(() => {
      const intersection = performRaycast();
      
      if (intersection) {
        const objectId = getObjectId(intersection.object);
        
        if (objectId && objectId !== lastHoveredRef.current) {
          // New object hovered
          lastHoveredRef.current = objectId;
          setHoveredObjectId(objectId);
          setIsHovering(true);
        }
      } else {
        // No object hovered
        if (lastHoveredRef.current !== null) {
          lastHoveredRef.current = null;
          setHoveredObjectId(null);
          setIsHovering(false);
        }
      }
    }, hoverDebounceMs);
  }, [enabled, updateMousePosition, performRaycast, getObjectId, hoverDebounceMs]);

  /**
   * Handle click events for object selection
   */
  const handleClick = useCallback((event: MouseEvent) => {
    if (!enabled) return;

    updateMousePosition(event.clientX, event.clientY);
    
    const intersection = performRaycast();
    
    if (intersection) {
      const objectId = getObjectId(intersection.object);
      
      if (objectId) {
        setClickedObjectId(objectId);
        
        // Clear clicked state after a short delay to allow consumers to react
        setTimeout(() => {
          setClickedObjectId(null);
        }, 100);
      }
    }
  }, [enabled, updateMousePosition, performRaycast, getObjectId]);

  /**
   * Handle touch start events for mobile devices (Req 15.4)
   */
  const handleTouchStart = useCallback((event: TouchEvent) => {
    if (!enabled || event.touches.length === 0) return;

    const touch = event.touches[0];
    updateMousePosition(touch.clientX, touch.clientY);
    
    const intersection = performRaycast();
    
    if (intersection) {
      const objectId = getObjectId(intersection.object);
      
      if (objectId) {
        // Set hover state for touch
        setHoveredObjectId(objectId);
        setIsHovering(true);
      }
    }
  }, [enabled, updateMousePosition, performRaycast, getObjectId]);

  /**
   * Handle touch end events for mobile devices
   */
  const handleTouchEnd = useCallback((_event: TouchEvent) => {
    if (!enabled) return;

    // If we have a hovered object, treat touch end as a click
    if (hoveredObjectId) {
      setClickedObjectId(hoveredObjectId);
      
      // Clear states
      setTimeout(() => {
        setClickedObjectId(null);
        setHoveredObjectId(null);
        setIsHovering(false);
      }, 100);
    }
  }, [enabled, hoveredObjectId]);

  /**
   * Clear hover state manually
   */
  const clearHover = useCallback(() => {
    lastHoveredRef.current = null;
    setHoveredObjectId(null);
    setIsHovering(false);
    
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
      hoverTimeoutRef.current = null;
    }
  }, []);

  /**
   * Clear click state manually
   */
  const clearClick = useCallback(() => {
    setClickedObjectId(null);
  }, []);

  /**
   * Set up event listeners
   */
  useEffect(() => {
    if (!domElement) return;

    // Add mouse event listeners
    domElement.addEventListener('mousemove', handleMouseMove);
    domElement.addEventListener('click', handleClick);
    
    // Add touch event listeners for mobile (Req 15.4)
    domElement.addEventListener('touchstart', handleTouchStart);
    domElement.addEventListener('touchend', handleTouchEnd);

    return () => {
      // Clean up event listeners
      domElement.removeEventListener('mousemove', handleMouseMove);
      domElement.removeEventListener('click', handleClick);
      domElement.removeEventListener('touchstart', handleTouchStart);
      domElement.removeEventListener('touchend', handleTouchEnd);
      
      // Clear any pending timeouts
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, [domElement, handleMouseMove, handleClick, handleTouchStart, handleTouchEnd]);

  /**
   * Clear hover state when disabled
   */
  useEffect(() => {
    if (!enabled) {
      clearHover();
    }
  }, [enabled, clearHover]);

  return {
    hoveredObjectId,
    clickedObjectId,
    isHovering,
    clearHover,
    clearClick,
  };
}

export default useInteractionManager;
