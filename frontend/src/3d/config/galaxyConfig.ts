/**
 * Configuration for procedural galaxy generation
 * Based on Galaxy2 algorithm with Gaussian distribution
 * Requirements: 17.1, 17.2
 */

export interface StarFieldConfig {
  numStars: number;          // Total number of stars to generate
  coreXDist: number;         // Core region X distribution (standard deviation)
  coreYDist: number;         // Core region Y distribution (standard deviation)
  outerCoreXDist: number;    // Outer core X distribution
  outerCoreYDist: number;    // Outer core Y distribution
  armXDist: number;          // Spiral arm X distribution
  armYDist: number;          // Spiral arm Y distribution
  armXMean: number;          // Spiral arm X mean offset
  armYMean: number;          // Spiral arm Y mean offset
  numArms: number;           // Number of spiral arms
  galaxyThickness: number;   // Z-axis thickness
  hazeRatio: number;         // Ratio of haze particles to stars (0-1)
}

/**
 * Star type distribution configuration
 * Defines colors, sizes, and percentages for different star types
 */
export interface StarTypeDistribution {
  colors: string[];          // Array of star colors by type (hex)
  sizes: number[];           // Array of base sizes by type
  percentages: number[];     // Distribution percentages (must sum to 100)
}

/**
 * Default star field configuration
 * Generates 15000 stars with spiral galaxy structure (Req 17.1)
 */
export const DEFAULT_STAR_FIELD_CONFIG: StarFieldConfig = {
  numStars: 15000,           // 15000 stars for dense, impressive galaxy
  
  // Core region (25% of stars) - dense center (Req 17.2)
  coreXDist: 40,             // Tighter core for more definition
  coreYDist: 40,
  
  // Outer core region (25% of stars) - transition zone (Req 17.2)
  outerCoreXDist: 120,       // Wider transition
  outerCoreYDist: 120,
  
  // Spiral arms (50% of stars) - distributed across arms (Req 17.2)
  armXDist: 180,             // Longer, more pronounced arms
  armYDist: 25,              // Tighter arm width for definition
  armXMean: 250,             // Arms extend further out
  armYMean: 0,
  
  // Galaxy structure
  numArms: 4,                // Four spiral arms
  galaxyThickness: 30,       // More 3D depth (increased from 20)
  hazeRatio: 0.5,            // 50% haze particles relative to stars
};

/**
 * Star type distribution
 * Defines visual variety in the star field
 */
export const STAR_TYPE_DISTRIBUTION: StarTypeDistribution = {
  // Star colors from hot (blue-white) to cool (red-orange)
  colors: [
    '#FFFFFF',  // White - hottest stars
    '#B3D9FF',  // Blue-white
    '#FFFFFF',  // White
    '#FFE0B3',  // Yellow-white
    '#FFB84D',  // Orange
    '#FF8A00',  // Red-orange - coolest stars
  ],
  
  // Base sizes (will be scaled by distance)
  sizes: [
    1.2,   // Large hot stars
    1.0,   // Medium stars
    0.8,   // Small stars
    0.9,   // Medium-small stars
    1.1,   // Medium-large stars
    0.7,   // Small cool stars
  ],
  
  // Distribution percentages (must sum to 100)
  percentages: [
    10,    // 10% white hot stars
    20,    // 20% blue-white stars
    30,    // 30% white stars (most common)
    20,    // 20% yellow-white stars
    15,    // 15% orange stars
    5,     // 5% red-orange stars
  ],
};

/**
 * Performance-based star field configurations
 */
export const STAR_FIELD_PRESETS = {
  HIGH: {
    ...DEFAULT_STAR_FIELD_CONFIG,
    numStars: 15000,
    hazeRatio: 0.5,
  },
  
  MEDIUM: {
    ...DEFAULT_STAR_FIELD_CONFIG,
    numStars: 8000,
    hazeRatio: 0.3,
  },
  
  LOW: {
    ...DEFAULT_STAR_FIELD_CONFIG,
    numStars: 4000,
    hazeRatio: 0.2,
  },
  
  MOBILE: {
    ...DEFAULT_STAR_FIELD_CONFIG,
    numStars: 2000,
    hazeRatio: 0.1,
  },
};

/**
 * Region distribution percentages
 * Defines how stars are distributed across galaxy regions
 */
export const REGION_DISTRIBUTION = {
  CORE: 0.25,           // 25% in core region
  OUTER_CORE: 0.25,     // 25% in outer core region
  SPIRAL_ARMS: 0.50,    // 50% in spiral arms
};

/**
 * Get star field configuration based on quality level
 */
export function getStarFieldConfig(quality: 'high' | 'medium' | 'low' | 'mobile'): StarFieldConfig {
  switch (quality) {
    case 'high':
      return STAR_FIELD_PRESETS.HIGH;
    case 'medium':
      return STAR_FIELD_PRESETS.MEDIUM;
    case 'low':
      return STAR_FIELD_PRESETS.LOW;
    case 'mobile':
      return STAR_FIELD_PRESETS.MOBILE;
    default:
      return DEFAULT_STAR_FIELD_CONFIG;
  }
}
