/**
 * MultiLayerRenderer Component
 * 
 * Implements a three-layer rendering pipeline for selective post-processing:
 * 1. BASE_LAYER (0): Normal scene geometry
 * 2. BLOOM_LAYER (1): Stars, glowing elements, particles (with bloom)
 * 3. OVERLAY_LAYER (2): UI overlays, text, controls (no bloom)
 * 
 * Rendering sequence:
 * 1. Render BLOOM_LAYER with bloom effect to texture
 * 2. Render OVERLAY_LAYER to texture
 * 3. Render BASE_LAYER and composite all layers using CompositionShader
 * 
 * Requirements: 18.1, 18.2, 18.3, 18.4, 18.5
 */

import React, { useEffect, useMemo, useRef } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { 
  EffectComposer, 
  RenderPass, 
  ShaderPass,
  UnrealBloomPass 
} from 'three/examples/jsm/Addons.js';
import { 
  WebGLRenderTarget, 
  Vector2, 
  LinearFilter,
  RGBAFormat,
} from 'three';
import { LAYERS } from '../../config/renderConfig';
import { createCompositionMaterial } from '../../shaders/CompositionShader';
import { DEFAULT_BLOOM_CONFIG, BloomConfig } from '../../config/renderConfig';

export interface MultiLayerRendererProps {
  /**
   * Bloom configuration
   */
  bloomConfig?: Partial<BloomConfig>;
  
  /**
   * Whether bloom is enabled
   */
  bloomEnabled?: boolean;
  
  /**
   * Performance mode
   */
  performanceMode?: 'high' | 'medium' | 'low';
  
  /**
   * Children components to render
   */
  children?: React.ReactNode;
}

/**
 * MultiLayerRenderer Component
 * 
 * Sets up a three-pass rendering pipeline:
 * 1. Bloom pass (BLOOM_LAYER) - renderToScreen: false
 * 2. Overlay pass (OVERLAY_LAYER) - renderToScreen: false
 * 3. Base pass with CompositionShader - final output
 * 
 * Requirements:
 * - 18.1: Three rendering layers (BASE, BLOOM, OVERLAY)
 * - 18.2: Selective bloom on BLOOM_LAYER
 * - 18.3: Overlay layer without bloom
 * - 18.4: Three separate render passes
 * - 18.5: CompositionShader for final blending
 */
export const MultiLayerRenderer: React.FC<MultiLayerRendererProps> = ({
  bloomConfig: bloomConfigOverride,
  bloomEnabled = true,
  performanceMode = 'high',
  children,
}) => {
  const { gl, scene, camera, size } = useThree();
  
  // Refs for composers and render targets
  const bloomComposerRef = useRef<EffectComposer | null>(null);
  const overlayComposerRef = useRef<EffectComposer | null>(null);
  const baseComposerRef = useRef<EffectComposer | null>(null);
  
  const bloomTargetRef = useRef<WebGLRenderTarget | null>(null);
  const overlayTargetRef = useRef<WebGLRenderTarget | null>(null);
  
  // Merge bloom config
  const bloomConfig = useMemo(() => ({
    ...DEFAULT_BLOOM_CONFIG,
    ...bloomConfigOverride,
  }), [bloomConfigOverride]);
  
  // Adjust bloom for performance
  const adjustedBloomConfig = useMemo(() => {
    if (performanceMode === 'low' || !bloomEnabled) {
      return { ...bloomConfig, strength: 0 };
    }
    if (performanceMode === 'medium') {
      return { ...bloomConfig, strength: bloomConfig.strength * 0.8 };
    }
    return bloomConfig;
  }, [bloomConfig, performanceMode, bloomEnabled]);
  
  // Initialize render targets and composers
  useEffect(() => {
    // Create render targets for each layer
    const bloomTarget = new WebGLRenderTarget(size.width, size.height, {
      minFilter: LinearFilter,
      magFilter: LinearFilter,
      format: RGBAFormat,
    });
    bloomTargetRef.current = bloomTarget;
    
    const overlayTarget = new WebGLRenderTarget(size.width, size.height, {
      minFilter: LinearFilter,
      magFilter: LinearFilter,
      format: RGBAFormat,
    });
    overlayTargetRef.current = overlayTarget;
    
    // 1. Bloom Composer (BLOOM_LAYER) - Req 18.2, 18.4
    const bloomComposer = new EffectComposer(gl, bloomTarget);
    bloomComposer.renderToScreen = false; // Render to texture
    
    const bloomRenderPass = new RenderPass(scene, camera);
    bloomComposer.addPass(bloomRenderPass);
    
    // Add UnrealBloomPass with configured parameters
    if (adjustedBloomConfig.strength > 0) {
      const bloomPass = new UnrealBloomPass(
        new Vector2(size.width, size.height),
        adjustedBloomConfig.strength,   // 1.5
        adjustedBloomConfig.radius,      // 0
        adjustedBloomConfig.threshold    // 0.4
      );
      bloomComposer.addPass(bloomPass);
    }
    
    bloomComposerRef.current = bloomComposer;
    
    // 2. Overlay Composer (OVERLAY_LAYER) - Req 18.3, 18.4
    const overlayComposer = new EffectComposer(gl, overlayTarget);
    overlayComposer.renderToScreen = false; // Render to texture
    
    const overlayRenderPass = new RenderPass(scene, camera);
    overlayComposer.addPass(overlayRenderPass);
    
    overlayComposerRef.current = overlayComposer;
    
    // 3. Base Composer with CompositionShader - Req 18.4, 18.5
    const baseComposer = new EffectComposer(gl);
    baseComposer.renderToScreen = true; // Final output to screen
    
    const baseRenderPass = new RenderPass(scene, camera);
    baseComposer.addPass(baseRenderPass);
    
    // Create composition shader pass
    const compositionMaterial = createCompositionMaterial();
    const compositionPass = new ShaderPass(compositionMaterial);
    compositionPass.renderToScreen = true;
    
    // Set texture uniforms
    compositionMaterial.uniforms.baseTexture.value = baseComposer.renderTarget1.texture;
    compositionMaterial.uniforms.bloomTexture.value = bloomTarget.texture;
    compositionMaterial.uniforms.overlayTexture.value = overlayTarget.texture;
    
    baseComposer.addPass(compositionPass);
    
    baseComposerRef.current = baseComposer;
    
    // Cleanup
    return () => {
      bloomTarget.dispose();
      overlayTarget.dispose();
      bloomComposer.dispose();
      overlayComposer.dispose();
      baseComposer.dispose();
    };
  }, [gl, scene, camera, size, adjustedBloomConfig]);
  
  // Update composer sizes on window resize
  useEffect(() => {
    if (bloomComposerRef.current) {
      bloomComposerRef.current.setSize(size.width, size.height);
    }
    if (overlayComposerRef.current) {
      overlayComposerRef.current.setSize(size.width, size.height);
    }
    if (baseComposerRef.current) {
      baseComposerRef.current.setSize(size.width, size.height);
    }
    if (bloomTargetRef.current) {
      bloomTargetRef.current.setSize(size.width, size.height);
    }
    if (overlayTargetRef.current) {
      overlayTargetRef.current.setSize(size.width, size.height);
    }
  }, [size]);
  
  /**
   * Render pipeline function
   * Executes all three render passes in sequence
   * 
   * Requirements: 18.1, 18.2, 18.3, 18.4, 18.5
   */
  useFrame(() => {
    if (!bloomComposerRef.current || !overlayComposerRef.current || !baseComposerRef.current) {
      return;
    }
    
    // Store original camera layers
    const originalLayers = camera.layers.mask;
    
    // Pass 1: Render BLOOM_LAYER (Req 18.2)
    camera.layers.set(LAYERS.BLOOM);
    bloomComposerRef.current.render();
    
    // Pass 2: Render OVERLAY_LAYER (Req 18.3)
    camera.layers.set(LAYERS.OVERLAY);
    overlayComposerRef.current.render();
    
    // Pass 3: Render BASE_LAYER with composition (Req 18.4, 18.5)
    camera.layers.set(LAYERS.BASE);
    baseComposerRef.current.render();
    
    // Restore original camera layers
    camera.layers.mask = originalLayers;
  }, 1); // Priority 1 to render after scene updates
  
  // This component manages rendering, children are rendered normally
  return <>{children}</>;
};

/**
 * Hook to access multi-layer rendering state
 */
export function useMultiLayerRenderer() {
  const { gl, scene, camera } = useThree();
  
  return {
    gl,
    scene,
    camera,
    layers: LAYERS,
  };
}

export default MultiLayerRenderer;
