# Celestial Components

Components for rendering celestial bodies (planets) in the galaxy scene.

## Components

### CelestialBody

Interactive planet component representing major platform sections (Create Model, Past Models, Info).

**Features:**
- Sphere geometry with 32 segments for smooth appearance
- MeshStandardMaterial with color and emissive properties
- Orbital animation around base position
- Click and hover interaction support
- Configurable via CelestialBodyConfig

**Requirements Met:**
- 1.2: Display at least three distinct celestial bodies
- 6.1: Create Model body with vibrant blue-purple tones
- 6.2: Past Models body with amber-gold tones
- 6.3: Info body with cool cyan-white tones

**Visual Properties:**
- Color: Primary body color
- Glow Color: Emissive color for bloom effect
- Emissive Intensity: Glow strength (0.9-1.2)
- Metalness: 0.3 for slight metallic look
- Roughness: 0.7 for diffuse surface

**Orbital Properties:**
- Orbit Radius: Distance from base position
- Orbit Speed: Angular velocity
- Orbit Axis: Rotation axis (default Z-up)

**Usage:**
```tsx
import { CELESTIAL_BODIES } from '../../config/celestialBodies';

<CelestialBody
  config={CELESTIAL_BODIES[0]}
  onClick={(id) => console.log('Clicked:', id)}
  onHover={(id, hovered) => console.log('Hover:', id, hovered)}
/>
```

## Configuration

Celestial bodies are configured in `config/celestialBodies.ts`:

- **Create Model**: Purple/blue, position [-200, 150, 0], scale 15
- **Past Models**: Amber/gold, position [200, -100, -50], scale 18
- **Info**: Cyan/white, position [0, 200, 100], scale 12

## Implementation Notes

- Uses useFrame hook for smooth orbital animation
- Cursor changes to pointer on hover
- Click events stop propagation to prevent conflicts
- Base position stored separately for orbital calculations
- Subtle body rotation (0.0001 rad/ms) for visual interest
