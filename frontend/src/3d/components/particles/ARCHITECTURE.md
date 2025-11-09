# Particle Systems Architecture

## Component Hierarchy

```
ParticleSystem (Base Component)
├── Props: count, distribution, radius, size, color, opacity, animation, speed
├── Features: Flexible configuration, multiple distributions, animations
└── Rendering: Three.js Points with BufferGeometry

NodeParticles (Pre-configured Components)
├── CreateModelParticles
│   ├── Extends: ParticleSystem
│   ├── Config: 150 particles, purple/blue gradient, orbital
│   └── Speed: 0.15 rad/s
├── PastModelsParticles
│   ├── Extends: ParticleSystem
│   ├── Config: 180 particles, amber/gold gradient, orbital
│   └── Speed: 0.12 rad/s
├── InfoParticles
│   ├── Extends: ParticleSystem
│   ├── Config: 120 particles, cyan gradient, orbital
│   └── Speed: 0.18 rad/s
└── NavigationNodeParticles (Unified Component)
    └── Renders appropriate particles based on node type

ParticleSystemDemo (Integration Helper)
├── Props: enabled, enableCreateModel, enablePastModels, enableInfo
├── Features: Easy integration, individual toggles
└── Usage: Drop into scene for instant particles
```

## Data Flow

```
NAVIGATION_NODES (config)
        ↓
NavigationNodeParticles
        ↓
    [Switch on node.type]
        ↓
    ┌───┴───┬───────┐
    ↓       ↓       ↓
Create  Past    Info
Model   Models  Node
Particles Particles Particles
    ↓       ↓       ↓
    └───┬───┴───────┘
        ↓
  ParticleSystem (Base)
        ↓
    [Generate positions]
        ↓
    [Assign colors]
        ↓
    [Animate with useFrame]
        ↓
  Three.js Points Rendering
        ↓
    BLOOM_LAYER
        ↓
  Post-processing (Bloom)
        ↓
    Final Render
```

## Rendering Pipeline

```
1. Component Mount
   └── useMemo: Generate particle positions & colors
       ├── Calculate distribution (orbital/spherical/ring)
       ├── Apply radius variations
       ├── Assign gradient colors
       └── Store initial angles

2. Every Frame (useFrame)
   └── Update particle positions based on animation
       ├── orbit: Rotate around center
       ├── pulse: Scale size
       ├── float: Vertical motion
       └── none: Static

3. Three.js Rendering
   └── Points geometry with BufferGeometry
       ├── Position attribute (Float32Array)
       ├── Color attribute (Float32Array)
       └── PointsMaterial
           ├── Vertex colors enabled
           ├── Additive blending
           ├── Transparency enabled
           └── Size attenuation enabled

4. Post-processing
   └── BLOOM_LAYER assignment
       └── Selective bloom effect applied
           └── Glowing particles
```

## Distribution Algorithms

### Orbital Distribution
```
For each particle i:
  angle = (i / count) * 2π
  r = radius ± random variation (20%)
  heightVariation = random (-30% to +30% of radius)
  
  x = cos(angle) * r
  y = sin(angle) * r
  z = heightVariation
```

### Spherical Distribution
```
For each particle i:
  theta = random(0, 2π)
  phi = acos(2 * random() - 1)
  r = radius * (0.8 to 1.2)
  
  x = r * sin(phi) * cos(theta)
  y = r * sin(phi) * sin(theta)
  z = r * cos(phi)
```

### Ring Distribution
```
For each particle i:
  angle = (i / count) * 2π
  r = radius ± random variation (10%)
  
  x = cos(angle) * r
  y = sin(angle) * r
  z = random(-1, 1)  // Very thin
```

## Animation System

### Orbit Animation
```typescript
For each frame:
  time += delta * speed
  
  For each particle:
    angle = initialAngle + time
    currentRadius = sqrt(x² + y²)
    
    x = centerX + cos(angle) * currentRadius
    y = centerY + sin(angle) * currentRadius
    // z remains constant
```

### Pulse Animation
```typescript
For each frame:
  time += delta * speed
  scale = 1.0 + sin(time * 2) * 0.2
  
  material.size = baseSize * scale
```

### Float Animation
```typescript
For each frame:
  time += delta * speed
  
  For each particle:
    offset = particleIndex * 0.1
    z += sin(time + offset) * 0.05
```

## Color Gradient System

```
Input: color array ['#B24BF3', '#7B2FFF', '#00D9FF']
       particle count: 150

Process:
  For each particle i:
    colorIndex = floor((i / count) * colorArray.length)
    particleColor = colorArray[min(colorIndex, length - 1)]
    
    colors[i*3]     = particleColor.r
    colors[i*3 + 1] = particleColor.g
    colors[i*3 + 2] = particleColor.b

Result:
  Particles 0-49:   Purple (#B24BF3)
  Particles 50-99:  Deep Purple (#7B2FFF)
  Particles 100-149: Cyan (#00D9FF)
```

## Performance Optimization

### Memory Management
```
BufferGeometry with typed arrays:
  - positions: Float32Array(count * 3)
  - colors: Float32Array(count * 3)
  - initialAngles: Float32Array(count)

Total memory per particle system:
  - 150 particles: ~3.6 KB
  - 180 particles: ~4.3 KB
  - 120 particles: ~2.9 KB
  - Total: ~10.8 KB
```

### Rendering Optimization
```
1. Single draw call per particle system
2. BufferGeometry (no individual objects)
3. Instanced rendering via Points
4. Depth write disabled (transparency)
5. Frustum culling (automatic)
6. Layer-based rendering (BLOOM_LAYER)
```

### Animation Optimization
```
1. useFrame hook (60 FPS sync)
2. Direct array manipulation
3. needsUpdate flag only when changed
4. No object creation per frame
5. Minimal calculations per particle
```

## Integration Points

### Scene Graph
```
Canvas
└── GalaxyScene
    └── GalaxyContent
        ├── LightingRig
        ├── ProceduralStarField (7000+ stars)
        ├── ParticleSystemDemo
        │   ├── CreateModelParticles (150)
        │   ├── PastModelsParticles (180)
        │   └── InfoParticles (120)
        └── NavigationNodes (3x)
            ├── create-model
            ├── past-models
            └── info
```

### Layer System
```
LAYERS.BASE (0)
├── NavigationNodes
├── UI elements
└── Non-glowing geometry

LAYERS.BLOOM (1)
├── ProceduralStarField
├── ParticleSystemDemo ← Particles here
│   ├── CreateModelParticles
│   ├── PastModelsParticles
│   └── InfoParticles
└── Glowing elements

LAYERS.OVERLAY (2)
└── UI overlays
```

## Configuration System

### Node-Specific Configs
```typescript
NAVIGATION_NODES
├── create-model
│   ├── position: Vector3(0, 200, 0)
│   ├── circleRadius: 30
│   └── circleColor: '#B24BF3'
├── past-models
│   ├── position: Vector3(173, -100, 0)
│   ├── circleRadius: 35
│   └── circleColor: '#FFB84D'
└── info
    ├── position: Vector3(-173, -100, 0)
    ├── circleRadius: 28
    └── circleColor: '#00D9FF'
```

### Particle Configs
```typescript
CreateModelParticles
├── count: 150
├── radius: nodeRadius + 10
├── colors: ['#B24BF3', '#7B2FFF', '#00D9FF']
├── speed: 0.15
└── opacity: 0.6

PastModelsParticles
├── count: 180
├── radius: nodeRadius + 12
├── colors: ['#FFB84D', '#FFA726', '#FF8A00']
├── speed: 0.12
└── opacity: 0.5

InfoParticles
├── count: 120
├── radius: nodeRadius + 8
├── colors: ['#00D9FF', '#4DD0E1', '#00BCD4']
├── speed: 0.18
└── opacity: 0.7
```

## Extension Points

### Adding New Particle Systems
```typescript
// 1. Create new component
export function CustomParticles({ node, enabled }: NodeParticlesProps) {
  return (
    <ParticleSystem
      count={200}
      distribution="spherical"
      radius={node.circleRadius + 15}
      size={1.0}
      color={['#FF0000', '#00FF00']}
      opacity={0.8}
      animation="pulse"
      speed={0.25}
      centerPosition={node.position}
      enabled={enabled}
    />
  );
}

// 2. Add to NavigationNodeParticles switch
case 'custom':
  return <CustomParticles node={node} enabled={enabled} />;
```

### Adding New Distributions
```typescript
// In ParticleSystem.tsx, add new case:
case 'spiral': {
  const angle = (i / count) * Math.PI * 4; // 2 full spirals
  const r = (i / count) * radius;
  
  x = Math.cos(angle) * r;
  y = Math.sin(angle) * r;
  z = (i / count) * radius * 0.5;
  break;
}
```

### Adding New Animations
```typescript
// In ParticleSystem.tsx, add new case:
case 'wave': {
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    const waveOffset = (i / count) * Math.PI * 2;
    positions[i3 + 2] += Math.sin(time + waveOffset) * 2;
  }
  positionAttribute.needsUpdate = true;
  break;
}
```

## Testing Strategy

### Unit Tests
```typescript
describe('ParticleSystem', () => {
  it('generates correct number of particles', () => {
    const count = 150;
    // Test position array length = count * 3
  });
  
  it('applies color gradient correctly', () => {
    // Test color distribution across particles
  });
  
  it('animates particles smoothly', () => {
    // Test animation updates per frame
  });
});
```

### Integration Tests
```typescript
describe('ParticleSystemDemo', () => {
  it('renders all node particles', () => {
    // Test all three particle systems render
  });
  
  it('respects enable/disable flags', () => {
    // Test individual node toggles
  });
});
```

### Performance Tests
```typescript
describe('Performance', () => {
  it('maintains 60 FPS with all particles', () => {
    // Monitor frame rate
  });
  
  it('uses minimal memory', () => {
    // Check memory allocation
  });
});
```

## Conclusion

The particle system architecture is designed for:
- **Flexibility:** Easy to configure and extend
- **Performance:** Optimized rendering and memory usage
- **Maintainability:** Clean separation of concerns
- **Scalability:** Can handle more particles or systems
- **Integration:** Simple to add to existing scenes

All components work together to create a cohesive, performant, and visually appealing particle system for the 3D galaxy scene.
