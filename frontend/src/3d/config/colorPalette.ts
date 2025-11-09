/**
 * Color palette configuration for the 3D galaxy experience
 * Defines all colors used throughout the scene
 * Requirements: 10.1, 10.2, 10.4
 */

/**
 * Background and atmospheric colors
 * Pure black background for modern space visualization (Req 10.1)
 * Updated for new design - inspired by Blueyard example
 */
export const BACKGROUND_COLORS = {
  PURE_BLACK: '#000000',           // Pure black background (NEW DESIGN)
  DEEP_SPACE_BLUE: '#0A0E27',      // Legacy - kept for reference
  SPACE_BLUE_MID: '#1A1F3A',       // Legacy - kept for reference
  NEBULA_PURPLE: '#2D1B3D',        // Legacy - kept for reference
  FOG_COLOR: '#000000',            // Black fog to match background (UPDATED)
} as const;

/**
 * Navigation node color configurations (NEW DESIGN)
 * Transparent circles with icons instead of 3D planet spheres (Req 10.2)
 * Updated to match new design with navigation nodes
 */
export const NAVIGATION_NODE_COLORS = {
  // Create Model Node - purple/cyan theme
  CREATE_MODEL: {
    circle: '#B24BF3',             // Purple circle border (Req 10.2)
    circleGlow: '#00D9FF',         // Cyan glow
    icon: '#FFFFFF',               // White icon
    label: '#FFFFFF',              // White label text
    subtitle: '#B3D9FF',           // Light blue subtitle
    particles: '#7B2FFF',          // Deep purple particles
    hover: '#E0B3FF',              // Lighter purple on hover
    temperature: 5000,             // Kelvin - vibrant, energetic (Req 10.4)
  },
  
  // Past Models Node - amber/gold theme
  PAST_MODELS: {
    circle: '#FFB84D',             // Amber circle border (Req 10.2)
    circleGlow: '#FFA726',         // Golden glow
    icon: '#FFFFFF',               // White icon
    label: '#FFFFFF',              // White label text
    subtitle: '#FFE0B3',           // Light amber subtitle
    particles: '#FF8A00',          // Deep orange particles
    hover: '#FFD699',              // Lighter amber on hover
    temperature: 3500,             // Kelvin - warm, historical (Req 10.4)
  },
  
  // Info Node - cyan theme
  INFO: {
    circle: '#00D9FF',             // Cyan circle border (Req 10.2)
    circleGlow: '#4DD0E1',         // Bright cyan glow
    icon: '#FFFFFF',               // White icon
    label: '#FFFFFF',              // White label text
    subtitle: '#B3D9FF',           // Light cyan subtitle
    particles: '#00BCD4',          // Cyan blue particles
    hover: '#66E6FF',              // Lighter cyan on hover
    temperature: 6500,             // Kelvin - cool, informative (Req 10.4)
  },
} as const;

/**
 * Legacy celestial body colors (DEPRECATED - kept for reference)
 * Use NAVIGATION_NODE_COLORS for new design
 */
export const CELESTIAL_BODY_COLORS = {
  // Create Model Planet - vibrant, energetic, innovative
  CREATE_MODEL: {
    primary: '#B24BF3',            // Vibrant purple (Req 10.2)
    glow: '#00D9FF',               // Electric blue glow
    particles: '#7B2FFF',          // Deep purple particles
    temperature: 5000,             // Kelvin - vibrant, energetic (Req 10.4)
    emissive: '#B24BF3',
    emissiveIntensity: 1.2,
  },
  
  // Past Models Planet - warm, historical, valuable
  PAST_MODELS: {
    primary: '#FFB84D',            // Warm amber (Req 10.2)
    glow: '#FFA726',               // Golden orange glow
    particles: '#FF8A00',          // Deep orange particles
    temperature: 3500,             // Kelvin - warm, historical (Req 10.4)
    emissive: '#FFB84D',
    emissiveIntensity: 1.0,
  },
  
  // Info Planet - cool, clear, informative
  INFO: {
    primary: '#00D9FF',            // Cool cyan (Req 10.2)
    glow: '#4DD0E1',               // Bright cyan glow
    particles: '#00BCD4',          // Cyan blue particles
    temperature: 6500,             // Kelvin - cool, informative (Req 10.4)
    emissive: '#00D9FF',
    emissiveIntensity: 0.9,
  },
} as const;

/**
 * Accent colors for UI and interactions (UPDATED for new design)
 */
export const ACCENT_COLORS = {
  // Primary accents (node colors)
  CYAN: '#00D9FF',                 // Cyan - Info node
  PURPLE: '#B24BF3',               // Purple - Create Model node
  AMBER: '#FFB84D',                // Amber - Past Models node
  
  // Legacy names (kept for compatibility)
  ELECTRIC_BLUE: '#00D9FF',        // Primary accent
  
  // Hover states (NEW DESIGN)
  HOVER_CYAN: '#66E6FF',           // Lighter cyan on hover
  HOVER_PURPLE: '#E0B3FF',         // Lighter purple on hover
  HOVER_AMBER: '#FFD699',          // Lighter amber on hover
  HOVER_HIGHLIGHT: '#FFFFFF',      // White highlight for emphasis
  
  // Interaction states
  ACTIVE_STATE: '#B24BF3',         // Purple for active
  FOCUS_RING: '#4DD0E1',           // Cyan for focus
  SELECTED: '#00FFFF',             // Bright cyan for selected
  
  // Connection and flow
  CONNECTION_LINE: '#4DD0E1',      // Cyan for connections
  CONNECTION_OPACITY: 0.4,         // 40% opacity
  ENERGY_FLOW: '#00D9FF',          // Electric blue for energy
  
  // Feedback colors
  SUCCESS: '#69F0AE',              // Green for success
  WARNING: '#FFB84D',              // Amber for warning
  ERROR: '#FF5252',                // Red for error
  INFO: '#4DD0E1',                 // Cyan for info
} as const;

/**
 * Lighting colors
 * Three-point lighting setup with color temperatures
 */
export const LIGHTING_COLORS = {
  KEY_LIGHT: '#FFFFFF',            // Pure white key light
  FILL_LIGHT: '#B3D9FF',           // Slight blue tint
  RIM_LIGHT: '#FFE0B3',            // Slight warm tint
  AMBIENT_LIGHT: '#1A1F3A',        // Dark blue ambient
} as const;

/**
 * Particle system colors
 */
export const PARTICLE_COLORS = {
  // Ambient data particles
  AMBIENT_DATA: '#4DD0E1',         // Cyan
  AMBIENT_OPACITY: 0.3,
  
  // Create Model energy particles
  ENERGY_PRIMARY: '#B24BF3',       // Purple
  ENERGY_SECONDARY: '#00D9FF',     // Blue
  ENERGY_TERTIARY: '#7B2FFF',      // Deep purple
  
  // Past Models archive particles
  ARCHIVE_PRIMARY: '#FFB84D',      // Amber
  ARCHIVE_SECONDARY: '#FFA726',    // Gold
  ARCHIVE_TERTIARY: '#FF8A00',     // Orange
  
  // Info glow particles
  INFO_GLOW: '#00D9FF',            // Cyan
  INFO_SECONDARY: '#4DD0E1',       // Bright cyan
} as const;

/**
 * Galaxy gradient colors (NEW DESIGN)
 * Animated spiral galaxy with color gradients - blue/cyan core with purple/pink edges
 * Matching Blueyard reference design
 * Requirements: 10.1, 10.2
 */
export const GALAXY_COLORS = {
  // Bright cyan/blue center
  CENTER_WARM: '#00D9FF',          // Bright cyan center
  CENTER_MID: '#4DD0E1',           // Cyan-blue
  
  // Transition colors
  MID_PURPLE: '#7B2FFF',           // Deep purple transition
  MID_BLUE: '#5e35b1',             // Blue-purple transition
  
  // Cool edge colors (purple/pink)
  EDGE_COOL: '#B24BF3',            // Purple edges
  EDGE_DARK: '#8B1FA8',            // Deep purple/pink
} as const;

/**
 * Star colors
 * From hot (blue-white) to cool (red-orange)
 * Updated with galaxy gradient colors for new design
 */
export const STAR_COLORS = {
  // Galaxy gradient colors (NEW)
  GALAXY_CENTER: '#ffa575',        // Warm center
  GALAXY_MID_WARM: '#ff8a65',      // Mid warm
  GALAXY_MID_PURPLE: '#9c4dcc',    // Purple transition
  GALAXY_MID_BLUE: '#5e35b1',      // Blue transition
  GALAXY_EDGE: '#311599',          // Cool edge
  
  // Traditional star colors (legacy)
  HOT_WHITE: '#FFFFFF',            // Hottest stars
  BLUE_WHITE: '#B3D9FF',           // Hot stars
  WHITE: '#FFFFFF',                // Medium stars
  YELLOW_WHITE: '#FFE0B3',         // Warm stars
  ORANGE: '#FFB84D',               // Cool stars
  RED_ORANGE: '#FF8A00',           // Coolest stars
} as const;

/**
 * UI overlay colors (UPDATED for new design)
 */
export const UI_COLORS = {
  // Text colors (NEW DESIGN)
  TEXT_PRIMARY: '#FFFFFF',         // White text - primary labels
  TEXT_SECONDARY: '#E5E7EB',       // Light gray text - secondary info
  TEXT_MUTED: '#9CA3AF',           // Medium gray text - muted content
  TEXT_SUBTLE: '#6B7280',          // Dark gray text - subtle hints
  
  // Background colors (updated for black background)
  OVERLAY_BG: 'rgba(0, 0, 0, 0.85)',        // Black with transparency
  OVERLAY_BG_LIGHT: 'rgba(0, 0, 0, 0.7)',   // Lighter black variant
  OVERLAY_BG_DARK: 'rgba(0, 0, 0, 0.95)',   // Darker variant
  
  // Border colors
  BORDER_PRIMARY: '#4DD0E1',       // Cyan border
  BORDER_SECONDARY: '#B24BF3',     // Purple border
  BORDER_TERTIARY: '#FFB84D',      // Amber border
  BORDER_SUBTLE: 'rgba(77, 208, 225, 0.3)',  // Subtle cyan
  BORDER_WHITE: 'rgba(255, 255, 255, 0.2)',  // Subtle white
} as const;

/**
 * Gradient definitions (UPDATED for new design)
 */
export const GRADIENTS = {
  // Galaxy gradient (NEW DESIGN) - warm center to cool edges
  GALAXY: {
    center: GALAXY_COLORS.CENTER_WARM,      // #ffa575 warm orange/pink
    midWarm: GALAXY_COLORS.CENTER_MID,      // #ff8a65
    midPurple: GALAXY_COLORS.MID_PURPLE,    // #9c4dcc
    midBlue: GALAXY_COLORS.MID_BLUE,        // #5e35b1
    edge: GALAXY_COLORS.EDGE_COOL,          // #311599 cool purple/blue
  },
  
  // Background (pure black - no gradient needed)
  BACKGROUND: {
    start: BACKGROUND_COLORS.PURE_BLACK,
    end: BACKGROUND_COLORS.PURE_BLACK,
  },
  
  // Legacy gradients (kept for reference)
  NEBULA: {
    start: BACKGROUND_COLORS.SPACE_BLUE_MID,
    end: BACKGROUND_COLORS.NEBULA_PURPLE,
  },
  
  ENERGY: {
    start: CELESTIAL_BODY_COLORS.CREATE_MODEL.primary,
    end: CELESTIAL_BODY_COLORS.CREATE_MODEL.glow,
  },
  
  // Node-specific gradients (NEW)
  NODE_CREATE: {
    start: NAVIGATION_NODE_COLORS.CREATE_MODEL.circle,
    end: NAVIGATION_NODE_COLORS.CREATE_MODEL.circleGlow,
  },
  
  NODE_HISTORY: {
    start: NAVIGATION_NODE_COLORS.PAST_MODELS.circle,
    end: NAVIGATION_NODE_COLORS.PAST_MODELS.circleGlow,
  },
  
  NODE_INFO: {
    start: NAVIGATION_NODE_COLORS.INFO.circle,
    end: NAVIGATION_NODE_COLORS.INFO.circleGlow,
  },
} as const;

/**
 * Color utility functions
 */

/**
 * Convert hex color to RGB values
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
  } : null;
}

/**
 * Convert RGB to hex color
 */
export function rgbToHex(r: number, g: number, b: number): string {
  return '#' + [r, g, b].map(x => {
    const hex = x.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
}

/**
 * Get color with opacity
 */
export function withOpacity(hex: string, opacity: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})`;
}

/**
 * Interpolate between two colors
 */
export function lerpColor(color1: string, color2: string, t: number): string {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  
  if (!rgb1 || !rgb2) return color1;
  
  const r = Math.round(rgb1.r + (rgb2.r - rgb1.r) * t);
  const g = Math.round(rgb1.g + (rgb2.g - rgb1.g) * t);
  const b = Math.round(rgb1.b + (rgb2.b - rgb1.b) * t);
  
  return rgbToHex(r, g, b);
}

/**
 * Get navigation node colors by type (NEW DESIGN)
 */
export function getNavigationNodeColors(type: 'create' | 'history' | 'info') {
  switch (type) {
    case 'create':
      return NAVIGATION_NODE_COLORS.CREATE_MODEL;
    case 'history':
      return NAVIGATION_NODE_COLORS.PAST_MODELS;
    case 'info':
      return NAVIGATION_NODE_COLORS.INFO;
    default:
      return NAVIGATION_NODE_COLORS.CREATE_MODEL;
  }
}

/**
 * Get celestial body colors by type (LEGACY - use getNavigationNodeColors for new design)
 */
export function getCelestialBodyColors(type: 'create' | 'history' | 'info') {
  switch (type) {
    case 'create':
      return CELESTIAL_BODY_COLORS.CREATE_MODEL;
    case 'history':
      return CELESTIAL_BODY_COLORS.PAST_MODELS;
    case 'info':
      return CELESTIAL_BODY_COLORS.INFO;
    default:
      return CELESTIAL_BODY_COLORS.CREATE_MODEL;
  }
}

/**
 * Get galaxy color based on distance from center (NEW DESIGN)
 * @param distanceRatio - 0 (center) to 1 (edge)
 * @returns hex color string
 */
export function getGalaxyColorByDistance(distanceRatio: number): string {
  // Clamp ratio between 0 and 1
  const t = Math.max(0, Math.min(1, distanceRatio));
  
  // Define color stops
  if (t < 0.2) {
    // Center: warm orange/pink
    return lerpColor(GALAXY_COLORS.CENTER_WARM, GALAXY_COLORS.CENTER_MID, t / 0.2);
  } else if (t < 0.4) {
    // Transition to purple
    return lerpColor(GALAXY_COLORS.CENTER_MID, GALAXY_COLORS.MID_PURPLE, (t - 0.2) / 0.2);
  } else if (t < 0.7) {
    // Purple to blue transition
    return lerpColor(GALAXY_COLORS.MID_PURPLE, GALAXY_COLORS.MID_BLUE, (t - 0.4) / 0.3);
  } else {
    // Edge: cool purple/blue
    return lerpColor(GALAXY_COLORS.MID_BLUE, GALAXY_COLORS.EDGE_COOL, (t - 0.7) / 0.3);
  }
}
