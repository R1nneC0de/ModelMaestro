/**
 * Procedural galaxy generation utilities
 * Based on Galaxy2 algorithm with Gaussian distribution
 * Requirements: 17.1, 17.2
 */

import * as THREE from 'three';
import {
  StarFieldConfig,
  REGION_DISTRIBUTION,
  STAR_TYPE_DISTRIBUTION,
} from '../config/galaxyConfig';
import { getGalaxyColorByDistance } from '../config/colorPalette';

/**
 * Star data structure
 */
export interface StarData {
  position: THREE.Vector3;
  starType: number;        // Index into star type distribution
  size: number;            // Base size before distance scaling
  color: string;           // Color based on star type
  isHaze: boolean;         // Whether this is a haze particle
  distanceFromCenter: number;  // Distance from galaxy center (for color gradient)
  angle: number;           // Angle from center (for rotation animation)
  armIndex?: number;       // Which spiral arm this star belongs to (if any)
}

/**
 * Generate a random number from a Gaussian (normal) distribution
 * Uses Box-Muller transform for generating normally distributed random numbers
 * 
 * @param mean - Mean of the distribution
 * @param stdDev - Standard deviation of the distribution
 * @returns Random number from Gaussian distribution
 */
export function gaussianRandom(mean: number = 0, stdDev: number = 1): number {
  // Box-Muller transform
  const u1 = Math.random();
  const u2 = Math.random();
  
  const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  
  return z0 * stdDev + mean;
}

/**
 * Calculate spiral arm position
 * Generates points along a logarithmic spiral
 * 
 * @param armIndex - Which spiral arm (0 to numArms-1)
 * @param numArms - Total number of spiral arms
 * @param distance - Distance from center
 * @param angle - Angle offset for this point
 * @returns [x, y] coordinates for the spiral position
 */
export function spiral(
  armIndex: number,
  numArms: number,
  distance: number,
  angle: number
): [number, number] {
  // Base angle for this arm
  const armAngle = (armIndex * 2 * Math.PI) / numArms;
  
  // Logarithmic spiral: r = a * e^(b*theta)
  // We use a simplified version where the spiral tightness is controlled by distance
  const spiralTightness = 0.3;
  const theta = armAngle + (distance * spiralTightness) + angle;
  
  const x = distance * Math.cos(theta);
  const y = distance * Math.sin(theta);
  
  return [x, y];
}

/**
 * Generate a star in the core region
 * Core region: 25% of stars, dense center (Req 17.2)
 * 
 * @param config - Star field configuration
 * @returns Star data
 */
function generateCoreStar(config: StarFieldConfig): StarData {
  const x = gaussianRandom(0, config.coreXDist);
  const y = gaussianRandom(0, config.coreYDist);
  const z = gaussianRandom(0, config.galaxyThickness);
  
  return createStarData(x, y, z, false);
}

/**
 * Generate a star in the outer core region
 * Outer core region: 25% of stars, transition zone (Req 17.2)
 * 
 * @param config - Star field configuration
 * @returns Star data
 */
function generateOuterCoreStar(config: StarFieldConfig): StarData {
  const x = gaussianRandom(0, config.outerCoreXDist);
  const y = gaussianRandom(0, config.outerCoreYDist);
  const z = gaussianRandom(0, config.galaxyThickness);
  
  return createStarData(x, y, z, false);
}

/**
 * Generate a star in a spiral arm
 * Spiral arms: 50% of stars, distributed across arms (Req 17.2)
 * 
 * @param config - Star field configuration
 * @returns Star data
 */
function generateSpiralArmStar(config: StarFieldConfig): StarData {
  // Choose random arm
  const armIndex = Math.floor(Math.random() * config.numArms);
  
  // Random distance along arm
  const distance = Math.abs(gaussianRandom(config.armXMean, config.armXDist));
  
  // Random angle offset for variation
  const angleOffset = gaussianRandom(0, 0.5);
  
  // Get spiral position
  const [x, y] = spiral(armIndex, config.numArms, distance, angleOffset);
  
  // Add perpendicular variation to arm
  const perpOffset = gaussianRandom(0, config.armYDist);
  const perpAngle = Math.atan2(y, x) + Math.PI / 2;
  
  const finalX = x + perpOffset * Math.cos(perpAngle);
  const finalY = y + perpOffset * Math.sin(perpAngle);
  const z = gaussianRandom(0, config.galaxyThickness);
  
  return createStarData(finalX, finalY, z, false, armIndex);
}

/**
 * Generate a haze particle
 * Haze particles are larger, more transparent versions of stars
 * 
 * @param config - Star field configuration
 * @returns Star data marked as haze
 */
function generateHazeParticle(config: StarFieldConfig): StarData {
  // Haze particles use same distribution as stars
  const rand = Math.random();
  
  let star: StarData;
  if (rand < REGION_DISTRIBUTION.CORE) {
    star = generateCoreStar(config);
  } else if (rand < REGION_DISTRIBUTION.CORE + REGION_DISTRIBUTION.OUTER_CORE) {
    star = generateOuterCoreStar(config);
  } else {
    star = generateSpiralArmStar(config);
  }
  
  // Mark as haze and increase size
  star.isHaze = true;
  star.size *= 2.5; // Haze particles are larger
  
  return star;
}

/**
 * Create star data with random type and properties
 * 
 * @param x - X position
 * @param y - Y position
 * @param z - Z position
 * @param isHaze - Whether this is a haze particle
 * @param armIndex - Optional spiral arm index
 * @returns Complete star data
 */
function createStarData(x: number, y: number, z: number, isHaze: boolean, armIndex?: number): StarData {
  // Calculate distance from center for color gradient
  const distanceFromCenter = Math.sqrt(x * x + y * y);
  
  // Calculate angle from center for rotation animation
  const angle = Math.atan2(y, x);
  
  // Select star type based on distribution percentages
  const rand = Math.random() * 100;
  let cumulative = 0;
  let starType = 0;
  
  for (let i = 0; i < STAR_TYPE_DISTRIBUTION.percentages.length; i++) {
    cumulative += STAR_TYPE_DISTRIBUTION.percentages[i];
    if (rand <= cumulative) {
      starType = i;
      break;
    }
  }
  
  return {
    position: new THREE.Vector3(x, y, z),
    starType,
    size: STAR_TYPE_DISTRIBUTION.sizes[starType],
    color: STAR_TYPE_DISTRIBUTION.colors[starType],
    isHaze,
    distanceFromCenter,
    angle,
    armIndex,
  };
}

/**
 * Generate complete star field with procedural galaxy algorithm
 * Generates stars in three regions: core, outer core, and spiral arms (Req 17.1, 17.2)
 * 
 * @param config - Star field configuration
 * @returns Array of star data
 */
export function generateStarField(config: StarFieldConfig): StarData[] {
  const stars: StarData[] = [];
  
  // Calculate number of stars per region
  const numCoreStars = Math.floor(config.numStars * REGION_DISTRIBUTION.CORE);
  const numOuterCoreStars = Math.floor(config.numStars * REGION_DISTRIBUTION.OUTER_CORE);
  const numArmStars = config.numStars - numCoreStars - numOuterCoreStars;
  
  // Generate core stars (25%)
  for (let i = 0; i < numCoreStars; i++) {
    stars.push(generateCoreStar(config));
  }
  
  // Generate outer core stars (25%)
  for (let i = 0; i < numOuterCoreStars; i++) {
    stars.push(generateOuterCoreStar(config));
  }
  
  // Generate spiral arm stars (50%)
  for (let i = 0; i < numArmStars; i++) {
    stars.push(generateSpiralArmStar(config));
  }
  
  // Generate haze particles (50% of star count)
  const numHazeParticles = Math.floor(config.numStars * config.hazeRatio);
  for (let i = 0; i < numHazeParticles; i++) {
    stars.push(generateHazeParticle(config));
  }
  
  return stars;
}

/**
 * Calculate distance-based star scale
 * Stars appear smaller when farther from camera (Req 17.4)
 * 
 * @param starPosition - Position of the star
 * @param cameraPosition - Position of the camera
 * @param baseSize - Base size of the star
 * @param scaleFactor - Distance scaling factor
 * @returns Scaled size
 */
export function calculateStarScale(
  starPosition: THREE.Vector3,
  cameraPosition: THREE.Vector3,
  baseSize: number,
  scaleFactor: number = 0.001
): number {
  const distance = starPosition.distanceTo(cameraPosition);
  
  // Scale inversely with distance, but with a minimum size
  const scale = baseSize * (1 + distance * scaleFactor);
  
  return Math.max(scale, baseSize * 0.5);
}

/**
 * Apply galaxy gradient colors to stars based on distance from center
 * Warm orange/pink center → cool purple/blue edges (Req 17.3)
 * 
 * @param stars - Array of star data
 * @param maxDistance - Maximum distance for normalization (optional)
 * @returns Stars with updated gradient colors
 */
export function applyGalaxyGradient(stars: StarData[], maxDistance?: number): StarData[] {
  // Find max distance if not provided
  if (!maxDistance) {
    maxDistance = Math.max(...stars.map(s => s.distanceFromCenter));
  }
  
  return stars.map(star => {
    // Normalize distance to 0-1 range
    const distanceRatio = star.distanceFromCenter / maxDistance!;
    
    // Get gradient color based on distance
    const gradientColor = getGalaxyColorByDistance(distanceRatio);
    
    return {
      ...star,
      color: gradientColor,
    };
  });
}
