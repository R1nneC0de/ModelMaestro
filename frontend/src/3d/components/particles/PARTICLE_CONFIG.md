# Particle System Configuration Reference

## Visual Configuration Summary

### Create Model Node Particles
```
Node Type: create
Particle Count: 150
Distribution: Orbital
Radius Offset: +10 units from circle edge
Particle Size: 0.8
Colors: Purple → Deep Purple → Cyan
  - #B24BF3 (Vibrant Purple)
  - #7B2FFF (Deep Purple)
  - #00D9FF (Electric Cyan)
Opacity: 0.6
Animation: Orbit
Speed: 0.15 (slow)
Visual Effect: Energetic, creative swirl
```

### Past Models Node Particles
```
Node Type: history
Particle Count: 180
Distribution: Orbital
Radius Offset: +12 units from circle edge
Particle Size: 0.7
Colors: Amber → Gold → Orange
  - #FFB84D (Warm Amber)
  - #FFA726 (Golden Orange)
  - #FF8A00 (Deep Orange)
Opacity: 0.5
Animation: Orbit
Speed: 0.12 (slower)
Visual Effect: Warm, historical archive rings
```

### Info Node Particles
```
Node Type: info
Particle Count: 120
Distribution: Orbital
Radius Offset: +8 units from circle edge
Particle Size: 0.9
Colors: Cyan → Bright Cyan → Cyan Blue
  - #00D9FF (Cool Cyan)
  - #4DD0E1 (Bright Cyan)
  - #00BCD4 (Cyan Blue)
Opacity: 0.7
Animation: Orbit
Speed: 0.18 (slightly faster)
Visual Effect: Clear, informative glow
```

## Total Particle Budget

When all node particles are enabled:
- Create Model: 150 particles
- Past Models: 180 particles
- Info: 120 particles
- **Total: 450 particles**

This is in addition to the procedural star field (7000-20000 stars depending on quality).

## Performance Impact

### High Quality Mode
- All particles enabled
- Full bloom effects
- Smooth 60 FPS on modern GPUs

### Medium Quality Mode
- All particles enabled
- Reduced bloom
- 45-60 FPS on mid-range GPUs

### Low Quality Mode
- Particles disabled (recommended)
- No bloom
- 30+ FPS on low-end GPUs

## Color Psychology

### Purple/Blue (Create Model)
- **Purple (#B24BF3)**: Creativity, innovation, imagination
- **Blue (#00D9FF)**: Technology, intelligence, trust
- **Effect**: Energetic and forward-thinking

### Amber/Gold (Past Models)
- **Amber (#FFB84D)**: Warmth, history, value
- **Gold (#FFA726)**: Achievement, success, quality
- **Effect**: Prestigious and established

### Cyan (Info)
- **Cyan (#00D9FF)**: Clarity, communication, information
- **Bright Cyan (#4DD0E1)**: Freshness, accessibility
- **Effect**: Clear and approachable

## Animation Timing

All particles use orbital animation with different speeds to create visual variety:

```
Create Model:  0.15 rad/s → Full rotation in ~42 seconds
Past Models:   0.12 rad/s → Full rotation in ~52 seconds
Info:          0.18 rad/s → Full rotation in ~35 seconds
```

The different speeds prevent visual synchronization and create a more organic, dynamic appearance.

## Rendering Details

### Material Properties
```typescript
{
  size: 0.7-0.9,
  vertexColors: true,
  transparent: true,
  opacity: 0.5-0.7,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
  sizeAttenuation: true
}
```

### Layer Assignment
All particles are assigned to `LAYERS.BLOOM` (layer 1) for selective bloom post-processing.

### Blending Mode
Additive blending creates a luminous, glowing appearance that enhances the cosmic atmosphere.

## Customization Guide

To adjust particle appearance, modify values in `NodeParticles.tsx`:

### Increase Particle Density
```typescript
count={300}  // Double the particles
```

### Adjust Orbit Radius
```typescript
radius={node.circleRadius + 20}  // Orbit further out
```

### Change Animation Speed
```typescript
speed={0.3}  // Faster orbit
```

### Modify Colors
```typescript
color={['#FF0000', '#00FF00', '#0000FF']}  // Custom gradient
```

### Adjust Opacity
```typescript
opacity={0.9}  // More visible
```

## Integration Checklist

- [x] Base ParticleSystem component created
- [x] Node-specific particle configurations defined
- [x] Color gradients match node themes
- [x] Animation speeds provide visual variety
- [x] Particle counts optimized for performance
- [x] Bloom layer assignment configured
- [x] Enable/disable functionality implemented
- [x] Documentation completed

## Visual Testing Checklist

When testing the particle systems, verify:

- [ ] Particles orbit smoothly around nodes
- [ ] Colors match node themes (purple, amber, cyan)
- [ ] Particles glow with bloom effect
- [ ] Animation is subtle and not distracting
- [ ] Particles don't interfere with node interactions
- [ ] Performance remains at 60 FPS
- [ ] Particles can be disabled without errors
- [ ] Different orbit speeds create visual variety
