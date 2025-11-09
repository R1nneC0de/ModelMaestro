# Particle Systems

This directory contains particle system components for the 3D galaxy scene.

## Components

### ParticleSystem

Base particle system component that provides flexible particle rendering with various distribution patterns and animations.

**Features:**
- Multiple distribution types: `orbital`, `spherical`, `ring`
- Animation behaviors: `orbit`, `pulse`, `float`, `none`
- Color gradients support
- Assigned to BLOOM_LAYER for glow effects
- Configurable size, opacity, and speed

**Usage:**
```tsx
import { ParticleSystem } from './components/particles';

<ParticleSystem
  count={150}
  distribution="orbital"
  radius={40}
  size={0.8}
  color={['#B24BF3', '#00D9FF']}
  opacity={0.6}
  animation="orbit"
  speed={0.15}
  centerPosition={new Vector3(0, 0, 0)}
  enabled={true}
/>
```

### NodeParticles

Pre-configured particle systems for each navigation node type. These are **optional** components that can be enabled/disabled.

**Components:**
- `CreateModelParticles` - Purple/blue gradient particles for Create Model node
- `PastModelsParticles` - Amber/gold particles for Past Models node
- `InfoParticles` - Cyan particles for Info node
- `NavigationNodeParticles` - Unified component that renders appropriate particles based on node type

**Usage:**
```tsx
import { NavigationNodeParticles } from './components/particles';
import { NAVIGATION_NODES } from './config/navigationNodes';

// Render particles for all nodes
{NAVIGATION_NODES.map(node => (
  <NavigationNodeParticles
    key={node.id}
    node={node}
    enabled={true}  // Set to false to disable particles
  />
))}

// Or render specific node particles
<CreateModelParticles node={createNode} enabled={true} />
```

### ProceduralStarField

Generates the background galaxy with procedural star distribution.

**Features:**
- Gaussian distribution for realistic galaxy structure
- Core, outer core, and spiral arm regions
- Distance-based star scaling
- Haze particles for atmospheric effect
- Animated spiral rotation

## Configuration

Particle systems use the following configuration from `renderConfig.ts`:
- `LAYERS.BLOOM` - Particles are assigned to bloom layer for glow effects
- Additive blending for luminous appearance
- Size attenuation for depth perception

## Performance

Particle counts are kept modest for performance:
- Create Model: 150 particles
- Past Models: 180 particles
- Info: 120 particles
- Total: ~450 particles (when all enabled)

These counts can be adjusted in `NodeParticles.tsx` based on performance requirements.

## Optional Nature

The node particle systems (tasks 10.2, 10.3, 10.4) are marked as **OPTIONAL** in the implementation plan. They can be:
- Enabled by default for enhanced visual appeal
- Disabled for better performance on lower-end devices
- Toggled via a quality settings system
- Controlled per-node for selective effects

To disable all node particles:
```tsx
<NavigationNodeParticles node={node} enabled={false} />
```

## Requirements

- Requirements 6.1: Create Model node particles
- Requirements 6.2: Past Models node particles
- Requirements 6.3: Info node particles
