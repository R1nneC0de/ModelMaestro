import React from 'react';
import { LIGHTING_COLORS } from '../../config/colorPalette';

/**
 * LightingRig Component
 * Implements three-point lighting setup for cinematic quality
 * 
 * Requirements:
 * - 10.3: Three-point lighting (key, fill, rim lights)
 * - 10.3: Ambient light with low intensity
 * - Design: Configure light positions and intensities per specification
 * 
 * Three-Point Lighting Setup:
 * - Key Light: Primary light source (intensity 1.2, position [100, 200, 100])
 * - Fill Light: Softens shadows (intensity 0.4, position [-100, 50, -50])
 * - Rim Light: Separates objects from background (intensity 0.8, position [0, -100, 200])
 * - Ambient Light: Base illumination (intensity 0.2)
 */

export interface LightingRigProps {
  // Optional overrides for light intensities
  keyLightIntensity?: number;
  fillLightIntensity?: number;
  rimLightIntensity?: number;
  ambientLightIntensity?: number;
}

/**
 * LightingRig - Three-point lighting system
 * 
 * Provides professional lighting setup for the galaxy scene
 * with key, fill, rim, and ambient lights
 */
export const LightingRig: React.FC<LightingRigProps> = ({
  keyLightIntensity = 1.2,
  fillLightIntensity = 0.4,
  rimLightIntensity = 0.8,
  ambientLightIntensity = 0.2,
}) => {
  return (
    <>
      {/* Key Light - Primary directional light */}
      {/* Position: Upper right front, provides main illumination */}
      <directionalLight
        position={[100, 200, 100]}
        intensity={keyLightIntensity}
        color={LIGHTING_COLORS.KEY_LIGHT}
        castShadow={false} // Shadows can be enabled in high performance mode
      />

      {/* Fill Light - Secondary light to soften shadows */}
      {/* Position: Upper left back, slight blue tint */}
      <directionalLight
        position={[-100, 50, -50]}
        intensity={fillLightIntensity}
        color={LIGHTING_COLORS.FILL_LIGHT}
        castShadow={false}
      />

      {/* Rim Light - Backlight for edge definition */}
      {/* Position: Below and behind, slight warm tint */}
      <directionalLight
        position={[0, -100, 200]}
        intensity={rimLightIntensity}
        color={LIGHTING_COLORS.RIM_LIGHT}
        castShadow={false}
      />

      {/* Ambient Light - Base scene illumination */}
      {/* Low intensity, dark blue tint for space atmosphere */}
      <ambientLight
        intensity={ambientLightIntensity}
        color={LIGHTING_COLORS.AMBIENT_LIGHT}
      />
    </>
  );
};

export default LightingRig;
