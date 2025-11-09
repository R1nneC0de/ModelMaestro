import { Vector3 } from 'three';

/**
 * Configuration for navigation nodes in the galaxy scene
 * Each node represents a major platform section as a transparent circle with icon
 * Updated design: circles instead of 3D planet spheres
 */

export interface NavigationNodeConfig {
  id: string;
  type: 'create' | 'history' | 'info';
  
  // Display properties
  label: string;              // Main label (e.g., 'CREATE MODEL')
  subtitle: string;           // Subtitle text (e.g., 'PROGRAMMABLE')
  description: string;        // Hover description
  
  // Icon properties
  iconType: 'upload' | 'history' | 'info';  // Icon identifier
  
  // Position in 3D space
  position: Vector3;
  
  // Visual properties for circle
  circleColor: string;        // Circle border color (cyan, purple, amber)
  circleRadius: number;       // Radius of the circle
  glowIntensity: number;      // Glow effect intensity
  
  // Interaction properties
  clickable: boolean;
  hoverHighlight: boolean;
  
  // Camera positioning
  cameraDistance: number;     // Distance multiplier for camera positioning
}

/**
 * Configuration for the three main navigation nodes
 * Requirements: 6.1, 6.2, 6.3
 */
export const NAVIGATION_NODES: NavigationNodeConfig[] = [
  {
    id: 'create-model',
    type: 'create',
    
    // Display properties
    label: 'CREATE MODEL',
    subtitle: 'PROGRAMMABLE',
    description: 'Start a new training workflow',
    
    // Icon properties
    iconType: 'upload',
    
    // Position in 3D space (triangle formation - top)
    position: new Vector3(0, 200, 0),
    
    // Visual properties - purple circle (Req 6.1)
    circleColor: '#B24BF3',     // Vibrant purple
    circleRadius: 30,           // Circle size (reduced)
    glowIntensity: 1.2,
    
    // Interaction properties
    clickable: true,
    hoverHighlight: true,
    
    // Camera positioning
    cameraDistance: 4,
  },
  
  {
    id: 'past-models',
    type: 'history',
    
    // Display properties
    label: 'PAST MODELS',
    subtitle: 'SCENIUS',
    description: 'Browse your training history',
    
    // Icon properties
    iconType: 'history',
    
    // Position in 3D space (triangle formation - bottom right)
    position: new Vector3(173, -100, 0),
    
    // Visual properties - amber circle (Req 6.2)
    circleColor: '#FFB84D',     // Warm amber/gold
    circleRadius: 35,           // Slightly larger circle (reduced)
    glowIntensity: 1.0,
    
    // Interaction properties
    clickable: true,
    hoverHighlight: true,
    
    // Camera positioning
    cameraDistance: 5,
  },
  
  {
    id: 'info',
    type: 'info',
    
    // Display properties
    label: 'INFORMATION',
    subtitle: 'ABOUT',
    description: 'Learn about the platform',
    
    // Icon properties
    iconType: 'info',
    
    // Position in 3D space (triangle formation - bottom left)
    position: new Vector3(-173, -100, 0),
    
    // Visual properties - cyan circle (Req 6.3)
    circleColor: '#00D9FF',     // Cool cyan
    circleRadius: 28,           // Medium circle size (reduced)
    glowIntensity: 0.9,
    
    // Interaction properties
    clickable: true,
    hoverHighlight: true,
    
    // Camera positioning
    cameraDistance: 3.5,
  },
];

/**
 * Get navigation node configuration by ID
 */
export function getNavigationNodeById(id: string): NavigationNodeConfig | undefined {
  return NAVIGATION_NODES.find(node => node.id === id);
}

/**
 * Get navigation node configuration by type
 */
export function getNavigationNodeByType(type: 'create' | 'history' | 'info'): NavigationNodeConfig | undefined {
  return NAVIGATION_NODES.find(node => node.type === type);
}
