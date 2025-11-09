# Custom Shaders

GLSL shaders for custom rendering effects.

## Files

### CompositionShader.ts
Multi-layer composition shader:
- Vertex shader for UV mapping
- Fragment shader for blending base, bloom, and overlay textures
- Additive blending for bloom layer
- Alpha blending for overlay layer

### StarShader.ts (optional)
Custom star rendering shader:
- Distance-based size scaling
- Color variation
- Glow effects

### ParticleShader.ts (optional)
Custom particle system shader:
- Animated particles
- Color gradients
- Opacity variations
