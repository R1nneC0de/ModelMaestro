/**
 * Unit tests for CompositionShader
 * 
 * Tests the shader creation and material configuration
 */

import { describe, it, expect } from 'vitest';
import { CompositionShader, createCompositionMaterial } from '../../src/3d/shaders/CompositionShader';
import { ShaderMaterial } from 'three';

describe('CompositionShader', () => {
  it('should have required uniforms', () => {
    expect(CompositionShader.uniforms).toBeDefined();
    expect(CompositionShader.uniforms.baseTexture).toBeDefined();
    expect(CompositionShader.uniforms.bloomTexture).toBeDefined();
    expect(CompositionShader.uniforms.overlayTexture).toBeDefined();
  });

  it('should have vertex and fragment shaders', () => {
    expect(CompositionShader.vertexShader).toBeDefined();
    expect(CompositionShader.fragmentShader).toBeDefined();
    expect(typeof CompositionShader.vertexShader).toBe('string');
    expect(typeof CompositionShader.fragmentShader).toBe('string');
  });

  it('should create a valid ShaderMaterial', () => {
    const material = createCompositionMaterial();
    
    expect(material).toBeInstanceOf(ShaderMaterial);
    expect(material.uniforms.baseTexture).toBeDefined();
    expect(material.uniforms.bloomTexture).toBeDefined();
    expect(material.uniforms.overlayTexture).toBeDefined();
    expect(material.depthWrite).toBe(false);
    expect(material.depthTest).toBe(false);
  });

  it('should have correct shader code structure', () => {
    const { vertexShader, fragmentShader } = CompositionShader;
    
    // Vertex shader should have vUv varying
    expect(vertexShader).toContain('varying vec2 vUv');
    expect(vertexShader).toContain('gl_Position');
    
    // Fragment shader should sample all three textures
    expect(fragmentShader).toContain('uniform sampler2D baseTexture');
    expect(fragmentShader).toContain('uniform sampler2D bloomTexture');
    expect(fragmentShader).toContain('uniform sampler2D overlayTexture');
    expect(fragmentShader).toContain('texture2D(baseTexture');
    expect(fragmentShader).toContain('texture2D(bloomTexture');
    expect(fragmentShader).toContain('texture2D(overlayTexture');
    
    // Fragment shader should blend layers
    expect(fragmentShader).toContain('gl_FragColor');
  });
});
