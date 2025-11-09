/**
 * Rendering pipeline configuration
 * Defines layers, bloom settings, and visual effects
 * Requirements: 4.1, 18.1, 18.2
 */

/**
 * Rendering layer constants
 * Used for multi-layer composition (Req 18.1)
 */
export const LAYERS = {
  BASE: 0,      // Normal geometry, UI elements
  BLOOM: 1,     // Stars, glowing elements, particles (Req 18.2)
  OVERLAY: 2,   // UI overlays, text, controls
} as const;

export type LayerType = typeof LAYERS[keyof typeof LAYERS];

/**
 * Bloom effect configuration
 * Applied to BLOOM_LAYER objects (Req 4.1, 18.2)
 */
export interface BloomConfig {
  strength: number;      // Bloom intensity (0-3)
  threshold: number;     // Luminance threshold (0-1)
  radius: number;        // Bloom spread radius (0-1)
  exposure: number;      // Scene exposure (0-2)
}

/**
 * Default bloom configuration
 * Optimized for celestial glow effects (Req 4.1)
 */
export const DEFAULT_BLOOM_CONFIG: BloomConfig = {
  strength: 1.5,         // Medium-high intensity for visible glow
  threshold: 0.4,        // Only bright objects bloom
  radius: 0,             // Tight bloom, no spread
  exposure: 1.0,         // Standard exposure
};

/**
 * Star rendering configuration
 */
export interface StarRenderConfig {
  minSize: number;       // Minimum star size
  maxSize: number;       // Maximum star size
  sizeAttenuation: boolean;  // Scale with distance
  distanceScaleFactor: number;  // Distance-based scaling multiplier
}

/**
 * Default star rendering settings
 */
export const DEFAULT_STAR_CONFIG: StarRenderConfig = {
  minSize: 2.0,          // Larger minimum size for visibility
  maxSize: 6.0,          // Larger maximum size for dramatic effect
  sizeAttenuation: true,
  distanceScaleFactor: 0.0015,  // More pronounced distance scaling for 3D depth
};

/**
 * Haze particle configuration
 */
export interface HazeConfig {
  opacity: number;       // Base opacity (0-1)
  size: number;          // Particle size
  blending: 'additive' | 'normal';
}

/**
 * Default haze settings
 */
export const DEFAULT_HAZE_CONFIG: HazeConfig = {
  opacity: 0.5,          // More visible atmospheric effect
  size: 10.0,            // Much larger for nebulous look
  blending: 'additive',  // Additive blending for glow
};

/**
 * Post-processing effect configuration
 */
export interface PostProcessingConfig {
  bloom: BloomConfig;
  vignette?: {
    offset: number;      // Inner radius (0-1)
    darkness: number;    // Outer darkness (0-1)
  };
  filmGrain?: {
    intensity: number;   // Grain strength (0-1)
    animated: boolean;   // Animate grain pattern
  };
  chromaticAberration?: {
    offset: number;      // RGB channel separation
    radialModulation: boolean;  // Stronger at edges
  };
}

/**
 * Default post-processing configuration
 */
export const DEFAULT_POST_PROCESSING: PostProcessingConfig = {
  bloom: DEFAULT_BLOOM_CONFIG,
  vignette: {
    offset: 0.3,
    darkness: 0.8,
  },
  filmGrain: {
    intensity: 0.15,
    animated: true,
  },
  chromaticAberration: {
    offset: 0.002,
    radialModulation: true,
  },
};

/**
 * Quality-based rendering configurations
 */
export const RENDER_PRESETS = {
  HIGH: {
    bloom: DEFAULT_BLOOM_CONFIG,
    stars: DEFAULT_STAR_CONFIG,
    haze: DEFAULT_HAZE_CONFIG,
    postProcessing: DEFAULT_POST_PROCESSING,
    shadows: true,
    antialias: true,
  },
  
  MEDIUM: {
    bloom: {
      ...DEFAULT_BLOOM_CONFIG,
      strength: 1.2,  // Slightly reduced
    },
    stars: DEFAULT_STAR_CONFIG,
    haze: {
      ...DEFAULT_HAZE_CONFIG,
      opacity: 0.2,  // Reduced haze
    },
    postProcessing: {
      bloom: DEFAULT_BLOOM_CONFIG,
      vignette: DEFAULT_POST_PROCESSING.vignette,
      // No film grain or chromatic aberration
    },
    shadows: false,
    antialias: true,
  },
  
  LOW: {
    bloom: {
      strength: 0,  // Bloom disabled
      threshold: 1.0,
      radius: 0,
      exposure: 1.0,
    },
    stars: {
      ...DEFAULT_STAR_CONFIG,
      maxSize: 1.5,  // Smaller stars
    },
    haze: {
      ...DEFAULT_HAZE_CONFIG,
      opacity: 0.1,  // Minimal haze
    },
    postProcessing: {
      bloom: {
        strength: 0,
        threshold: 1.0,
        radius: 0,
        exposure: 1.0,
      },
      // No additional effects
    },
    shadows: false,
    antialias: false,
  },
};

/**
 * Camera configuration
 */
export interface CameraConfig {
  fov: number;           // Field of view (degrees)
  near: number;          // Near clipping plane
  far: number;           // Far clipping plane
  position: [number, number, number];  // Initial position
  target: [number, number, number];    // Initial look-at target
}

/**
 * Default camera configuration
 */
export const DEFAULT_CAMERA_CONFIG: CameraConfig = {
  fov: 60,               // Standard field of view
  near: 0.1,             // Close clipping
  far: 5000000,          // Very far clipping for deep space
  position: [0, -350, 350],  // Zoomed in even closer - 45-degree angled view from below (looking up)
  target: [0, 0, 0],     // Look at origin
};

/**
 * Scene configuration
 */
export interface SceneConfig {
  background: string;    // Background color (hex)
  fog?: {
    color: string;       // Fog color (hex)
    density: number;     // Fog density (exponential)
  };
}

/**
 * Default scene configuration
 */
export const DEFAULT_SCENE_CONFIG: SceneConfig = {
  background: '#0A0E27',  // Deep space blue
  fog: {
    color: '#EBE2DB',     // Subtle fog for depth
    density: 0.00005,     // Very subtle
  },
};

/**
 * Get render configuration based on quality level
 */
export function getRenderConfig(quality: 'high' | 'medium' | 'low') {
  return RENDER_PRESETS[quality.toUpperCase() as keyof typeof RENDER_PRESETS];
}
