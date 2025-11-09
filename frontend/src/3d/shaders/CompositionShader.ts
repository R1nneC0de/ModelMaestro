/**
 * CompositionShader
 * 
 * Custom shader for blending multiple render layers:
 * - Base layer: Normal scene geometry
 * - Bloom layer: Glowing elements with bloom effect applied
 * - Overlay layer: UI elements and overlays
 * 
 * Blending modes:
 * - Bloom: Additive blending for luminous glow
 * - Overlay: Alpha blending for UI elements
 * 
 * Requirements: 18.5
 */

import { ShaderMaterial } from 'three';

/**
 * Vertex Shader
 * Simple pass-through shader that maps UV coordinates
 */
const vertexShader = `
  varying vec2 vUv;
  
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

/**
 * Fragment Shader
 * Blends base, bloom, and overlay textures
 */
const fragmentShader = `
  uniform sampler2D baseTexture;
  uniform sampler2D bloomTexture;
  uniform sampler2D overlayTexture;
  
  varying vec2 vUv;
  
  void main() {
    // Sample all three textures
    vec4 base = texture2D(baseTexture, vUv);
    vec4 bloom = texture2D(bloomTexture, vUv);
    vec4 overlay = texture2D(overlayTexture, vUv);
    
    // Start with base color
    vec4 result = base;
    
    // Add bloom using additive blending
    // This creates the luminous glow effect
    result.rgb += bloom.rgb;
    
    // Blend overlay on top using alpha blending
    // This preserves UI element transparency
    result.rgb = mix(result.rgb, overlay.rgb, overlay.a);
    result.a = max(result.a, overlay.a);
    
    gl_FragColor = result;
  }
`;

/**
 * CompositionShader definition
 * 
 * Uniforms:
 * - baseTexture: The main scene render
 * - bloomTexture: The bloom pass output
 * - overlayTexture: The UI overlay render
 */
export const CompositionShader = {
  uniforms: {
    baseTexture: { value: null },
    bloomTexture: { value: null },
    overlayTexture: { value: null },
  },
  
  vertexShader,
  fragmentShader,
};

/**
 * Create a ShaderMaterial from the CompositionShader
 */
export function createCompositionMaterial(): ShaderMaterial {
  return new ShaderMaterial({
    uniforms: {
      baseTexture: { value: null },
      bloomTexture: { value: null },
      overlayTexture: { value: null },
    },
    vertexShader,
    fragmentShader,
    depthWrite: false,
    depthTest: false,
  });
}

export default CompositionShader;
