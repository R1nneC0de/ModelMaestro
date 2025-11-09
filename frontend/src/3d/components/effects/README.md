# Effects Components

This directory contains visual effect components for the 3D galaxy scene, including the multi-layer rendering pipeline.

## Multi-Layer Rendering Pipeline

The multi-layer rendering system implements selective post-processing by separating the scene into three distinct layers:

### Layer Architecture

1. **BASE_LAYER (0)**: Normal scene geometry
   - Celestial body base meshes
   - Navigation nodes
   - Scene objects without special effects

2. **BLOOM_LAYER (1)**: Glowing elements with bloom effect
   - Stars and star field
   - Haze particles
   - Celestial body emissive/glow components
   - Energy particles

3. **OVERLAY_LAYER (2)**: UI elements without bloom
   - UI overlays
   - Text elements
   - Controls and HUD

### Components

#### CompositionShader (`../../shaders/CompositionShader.ts`)

Custom GLSL shader that blends three render textures:
- **Base texture**: Main scene render
- **Bloom texture**: Bloom pass output with glow effects
- **Overlay texture**: UI overlay render

Blending modes:
- Bloom: Additive blending for luminous glow
- Overlay: Alpha blending for UI transparency

#### BloomEffect (`BloomEffect.tsx`)

Configures UnrealBloomPass for selective bloom:
- Strength: 1.5 (bloom intensity)
- Threshold: 0.4 (luminance threshold)
- Radius: 0 (tight bloom, no spread)

Features:
- Performance-aware settings (high/medium/low)
- Automatic quality adjustment
- Hook for custom integration

#### MultiLayerRenderer (`MultiLayerRenderer.tsx`)

Main rendering pipeline component that orchestrates the three-pass rendering:

**Pass 1: Bloom Layer**
- Renders BLOOM_LAYER objects
- Applies UnrealBloomPass
- Outputs to bloom texture

**Pass 2: Overlay Layer**
- Renders OVERLAY_LAYER objects
- No post-processing
- Outputs to overlay texture

**Pass 3: Base Layer + Composition**
- Renders BASE_LAYER objects
- Applies CompositionShader to blend all textures
- Outputs final result to screen

### Usage

#### Basic Setup

```tsx
import { GalaxyScene } from './components/scene/GalaxyScene';
import { MultiLayerRenderer } from './components/effects/MultiLayerRenderer';
import { ProceduralStarField } from './components/particles/ProceduralStarField';
import { CelestialBody } from './components/celestial/CelestialBody';

function App() {
  return (
    <GalaxyScene>
      <MultiLayerRenderer
        bloomEnabled={true}
        performanceMode="high"
      >
        {/* Stars automatically assigned to BLOOM_LAYER */}
        <ProceduralStarField />
        
        {/* Celestial bodies assigned to BASE + BLOOM layers */}
        <CelestialBody config={createModelConfig} />
        <CelestialBody config={pastModelsConfig} />
        <CelestialBody config={infoConfig} />
      </MultiLayerRenderer>
    </GalaxyScene>
  );
}
```

#### Custom Bloom Configuration

```tsx
<MultiLayerRenderer
  bloomConfig={{
    strength: 2.0,    // Stronger bloom
    threshold: 0.3,   // Lower threshold (more objects bloom)
    radius: 0.5,      // Some bloom spread
  }}
  bloomEnabled={true}
  performanceMode="high"
>
  {/* Scene content */}
</MultiLayerRenderer>
```

#### Performance Modes

- **high**: Full bloom with default settings
- **medium**: Reduced bloom intensity (80% of configured)
- **low**: Bloom disabled (strength = 0)

### Assigning Objects to Layers

Objects must be explicitly assigned to layers to appear in the correct render pass:

```tsx
// In component useEffect
useEffect(() => {
  if (meshRef.current) {
    // Assign to BASE_LAYER
    meshRef.current.layers.set(LAYERS.BASE);
    
    // Also enable BLOOM_LAYER for glowing objects
    if (hasGlow) {
      meshRef.current.layers.enable(LAYERS.BLOOM);
    }
  }
}, []);
```

### Requirements Satisfied

- **Req 4.1**: Bloom effects with intensity 0.3-1.5
- **Req 17.4**: Sprite-based stars on BLOOM_LAYER
- **Req 18.1**: Three rendering layers (BASE, BLOOM, OVERLAY)
- **Req 18.2**: Selective bloom on BLOOM_LAYER
- **Req 18.3**: Overlay layer without bloom
- **Req 18.4**: Three separate render passes
- **Req 18.5**: CompositionShader for final blending

### Performance Considerations

The multi-layer rendering pipeline adds overhead due to multiple render passes. Performance optimizations:

1. **Render to texture**: Bloom and overlay passes render to textures, not screen
2. **Selective rendering**: Only objects on specific layers are rendered in each pass
3. **Quality modes**: Automatically adjust bloom settings based on device capabilities
4. **Efficient composition**: Single shader pass for final blending

### Troubleshooting

**Objects not glowing:**
- Ensure objects are assigned to BLOOM_LAYER
- Check that bloom is enabled and strength > 0
- Verify object has emissive material properties

**UI elements have bloom:**
- Assign UI elements to OVERLAY_LAYER, not BLOOM_LAYER
- OVERLAY_LAYER bypasses bloom pass

**Performance issues:**
- Reduce bloom strength or disable bloom
- Use lower performance mode
- Reduce number of objects on BLOOM_LAYER

### Future Enhancements

Potential additions to the rendering pipeline:
- Depth of field (DOF) effect
- Vignette effect
- Film grain
- Chromatic aberration
- SSAO (Screen Space Ambient Occlusion)
- Motion blur

These can be added as additional passes in the MultiLayerRenderer component.
