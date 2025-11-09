/**
 * BloomEffect Component
 * 
 * Configures UnrealBloomPass for selective bloom on BLOOM_LAYER objects.
 * Creates luminous glow effects for stars, celestial bodies, and particles.
 * 
 * Features:
 * - Selective bloom on BLOOM_LAYER (layer 1) only
 * - Configurable strength, threshold, and radius
 * - Performance-aware settings
 * 
 * Requirements: 4.1, 18.2
 */

import React, { useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import { EffectComposer, RenderPass, UnrealBloomPass } from 'three/examples/jsm/Addons.js';
import { Vector2 } from 'three';
import { DEFAULT_BLOOM_CONFIG, BloomConfig } from '../../config/renderConfig';

export interface BloomEffectProps {
  /**
   * Bloom configuration
   * Defaults to DEFAULT_BLOOM_CONFIG if not provided
   */
  config?: Partial<BloomConfig>;
  
  /**
   * Whether bloom is enabled
   * Can be disabled for performance
   */
  enabled?: boolean;
  
  /**
   * Performance mode
   * Adjusts bloom quality based on device capabilities
   */
  performanceMode?: 'high' | 'medium' | 'low';
}

/**
 * BloomEffect Component
 * 
 * Sets up UnrealBloomPass with design parameters:
 * - Strength: 1.5 (bloom intensity)
 * - Threshold: 0.4 (luminance threshold)
 * - Radius: 0 (tight bloom, no spread)
 * 
 * Applied only to objects on BLOOM_LAYER (layer 1)
 * 
 * Note: This component is designed to be used within a custom rendering pipeline.
 * For the full multi-layer implementation, see MultiLayerRenderer.tsx
 */
export const BloomEffect: React.FC<BloomEffectProps> = ({
  config: configOverride,
  enabled = true,
  performanceMode = 'high',
}) => {
  const { gl, scene, camera, size } = useThree();
  
  // Merge config with defaults
  const config = useMemo(() => ({
    ...DEFAULT_BLOOM_CONFIG,
    ...configOverride,
  }), [configOverride]);
  
  // Adjust config based on performance mode
  const adjustedConfig = useMemo(() => {
    if (performanceMode === 'low') {
      return {
        ...config,
        strength: 0, // Disable bloom in low mode
      };
    }
    
    if (performanceMode === 'medium') {
      return {
        ...config,
        strength: config.strength * 0.8, // Reduce bloom intensity
      };
    }
    
    return config;
  }, [config, performanceMode]);
  
  // Create bloom composer
  const bloomComposer = useMemo(() => {
    if (!enabled || adjustedConfig.strength === 0) {
      return null;
    }
    
    // Create effect composer
    const composer = new EffectComposer(gl);
    composer.renderToScreen = false; // We'll composite manually
    
    // Add render pass
    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);
    
    // Add bloom pass with configured parameters (Req 4.1)
    const bloomPass = new UnrealBloomPass(
      new Vector2(size.width, size.height),
      adjustedConfig.strength,   // Strength: 1.5
      adjustedConfig.radius,      // Radius: 0
      adjustedConfig.threshold    // Threshold: 0.4
    );
    
    composer.addPass(bloomPass);
    
    return composer;
  }, [gl, scene, camera, size, enabled, adjustedConfig]);
  
  // Update composer size on window resize
  React.useEffect(() => {
    if (bloomComposer) {
      bloomComposer.setSize(size.width, size.height);
    }
  }, [bloomComposer, size]);
  
  // This component doesn't render anything directly
  // It's used by MultiLayerRenderer to access the bloom composer
  return null;
};

/**
 * Hook to create and manage bloom composer
 * Can be used independently or within MultiLayerRenderer
 */
export function useBloomComposer(
  config?: Partial<BloomConfig>,
  enabled: boolean = true,
  performanceMode: 'high' | 'medium' | 'low' = 'high'
) {
  const { gl, scene, camera, size } = useThree();
  
  const bloomConfig = useMemo(() => ({
    ...DEFAULT_BLOOM_CONFIG,
    ...config,
  }), [config]);
  
  // Adjust for performance
  const adjustedConfig = useMemo(() => {
    if (performanceMode === 'low') {
      return { ...bloomConfig, strength: 0 };
    }
    if (performanceMode === 'medium') {
      return { ...bloomConfig, strength: bloomConfig.strength * 0.8 };
    }
    return bloomConfig;
  }, [bloomConfig, performanceMode]);
  
  const composer = useMemo(() => {
    if (!enabled || adjustedConfig.strength === 0) {
      return null;
    }
    
    const comp = new EffectComposer(gl);
    comp.renderToScreen = false;
    
    const renderPass = new RenderPass(scene, camera);
    comp.addPass(renderPass);
    
    const bloomPass = new UnrealBloomPass(
      new Vector2(size.width, size.height),
      adjustedConfig.strength,
      adjustedConfig.radius,
      adjustedConfig.threshold
    );
    
    comp.addPass(bloomPass);
    
    return comp;
  }, [gl, scene, camera, size, enabled, adjustedConfig]);
  
  // Update size on resize
  React.useEffect(() => {
    if (composer) {
      composer.setSize(size.width, size.height);
    }
  }, [composer, size]);
  
  return composer;
}

export default BloomEffect;
