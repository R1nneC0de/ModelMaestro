import { Vector3 } from 'three';
import { NavigationNodeConfig } from '../config/navigationNodes';

/**
 * Camera calculation utilities for navigation system
 * Requirements: 15.3
 */

/**
 * Quadrant enumeration for offset direction
 */
enum Quadrant {
  FIRST = 1,   // x > 0, y > 0
  SECOND = 2,  // x < 0, y > 0
  THIRD = 3,   // x < 0, y < 0
  FOURTH = 4,  // x > 0, y < 0
}

/**
 * Determine which quadrant a point is in based on x and y coordinates
 */
function getQuadrant(x: number, y: number): Quadrant {
  if (x >= 0 && y >= 0) return Quadrant.FIRST;
  if (x < 0 && y >= 0) return Quadrant.SECOND;
  if (x < 0 && y < 0) return Quadrant.THIRD;
  return Quadrant.FOURTH;
}

/**
 * Apply offset based on quadrant
 * Offsets camera away from center in the direction of the quadrant
 */
function applyQuadrantOffset(
  x: number,
  y: number,
  offset: number,
  quadrant: Quadrant
): [number, number] {
  switch (quadrant) {
    case Quadrant.FIRST:
      // Move further positive in both directions
      return [x + offset, y + offset];
    
    case Quadrant.SECOND:
      // Move further negative X, positive Y
      return [x - offset, y + offset];
    
    case Quadrant.THIRD:
      // Move further negative in both directions
      return [x - offset, y - offset];
    
    case Quadrant.FOURTH:
      // Move further positive X, negative Y
      return [x + offset, y - offset];
    
    default:
      return [x, y];
  }
}

/**
 * Calculate destination coordinates for camera based on target body
 * 
 * The camera is positioned at an offset from the body based on:
 * - Body size (scale/radius): Larger bodies need more distance
 * - Quadrant: Camera moves away from center in the body's direction
 * - Body type: Different types have different Z offsets
 * 
 * Requirements: 15.3
 * 
 * @param targetBody - The navigation node to focus on
 * @returns Vector3 position for the camera
 */
export function calculateDestinationCoordinates(
  targetBody: NavigationNodeConfig
): Vector3 {
  const x = targetBody.position.x;
  const y = targetBody.position.y;
  const z = targetBody.position.z;
  
  // Determine quadrant for offset direction
  const quadrant = getQuadrant(x, y);
  
  // Calculate offset based on body size
  // Use circleRadius as the "scale" for navigation nodes
  // Larger bodies need more distance for comfortable viewing
  const bodySize = targetBody.circleRadius;
  const offset = bodySize > 50 
    ? bodySize * 3   // Large bodies: 3x distance (reduced from 6x)
    : bodySize * 2;  // Smaller bodies: 2x distance (reduced from 3x)
  
  // Apply offset based on quadrant
  // This positions the camera away from the center in the body's direction
  const [offsetX, offsetY] = applyQuadrantOffset(x, y, offset, quadrant);
  
  // Z offset based on body type
  // Info nodes get higher camera position for better overview
  // Other nodes get closer for more intimate view
  let offsetZ: number;
  
  switch (targetBody.type) {
    case 'info':
      // Info node: Higher camera position (20x body size, reduced from 50x)
      offsetZ = z + (bodySize * 20);
      break;
    
    case 'create':
    case 'history':
    default:
      // Create/History nodes: Much closer camera position (10x body size, reduced from 25x)
      offsetZ = z + (bodySize * 10);
      break;
  }
  
  return new Vector3(offsetX, offsetY, offsetZ);
}

/**
 * Calculate takeoff height for the first phase of camera travel
 * Camera rises vertically before approaching the target
 * 
 * @param currentPosition - Current camera position
 * @param targetBody - Target navigation node
 * @returns Height to add to current Z position
 */
export function calculateTakeoffHeight(
  currentPosition: Vector3,
  targetBody: NavigationNodeConfig
): number {
  // Base takeoff height
  const baseTakeoffHeight = 700;
  
  // Additional height based on distance to target
  const distance = currentPosition.distanceTo(targetBody.position);
  const additionalHeight = Math.min(distance * 0.2, 300);
  
  return baseTakeoffHeight + additionalHeight;
}

/**
 * Calculate intermediate position for takeoff phase
 * Camera rises vertically while starting to track the target
 * 
 * @param currentPosition - Current camera position
 * @param targetBody - Target navigation node
 * @returns Vector3 position for end of takeoff phase
 */
export function calculateTakeoffPosition(
  currentPosition: Vector3,
  targetBody: NavigationNodeConfig
): Vector3 {
  const takeoffHeight = calculateTakeoffHeight(currentPosition, targetBody);
  
  return new Vector3(
    currentPosition.x,
    currentPosition.y,
    currentPosition.z + takeoffHeight
  );
}

/**
 * Calculate overview camera position
 * Default position when not focused on any body
 * Matches the initial camera position from renderConfig
 * 
 * @returns Vector3 position for overview state
 */
export function getOverviewPosition(): Vector3 {
  return new Vector3(0, -350, 350);
}

/**
 * Calculate overview camera target
 * Default target when not focused on any body
 * 
 * @returns Vector3 target for overview state
 */
export function getOverviewTarget(): Vector3 {
  return new Vector3(0, 0, 0);
}

/**
 * Interpolate between two Vector3 positions
 * 
 * @param start - Start position
 * @param end - End position
 * @param t - Interpolation factor (0 to 1)
 * @returns Interpolated Vector3 position
 */
export function lerpVector3(start: Vector3, end: Vector3, t: number): Vector3 {
  return new Vector3(
    start.x + (end.x - start.x) * t,
    start.y + (end.y - start.y) * t,
    start.z + (end.z - start.z) * t
  );
}

/**
 * Calculate distance-based scale for highlight geometry
 * Highlight scales based on camera distance during approach
 * 
 * @param cameraPosition - Current camera position
 * @param targetPosition - Target body position
 * @returns Scale factor for highlight (1.1% of distance)
 */
export function calculateHighlightScale(
  cameraPosition: Vector3,
  targetPosition: Vector3
): number {
  const distance = cameraPosition.distanceTo(targetPosition);
  return distance * 0.011; // 1.1% of distance
}
