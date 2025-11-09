# Navigation Components

This directory contains components for interactive navigation nodes in the 3D galaxy scene.

## Components

### NavigationNode

The `NavigationNode` component represents a navigable section of the platform as a transparent circle with an icon and text label. This replaces the planet-based `CelestialBody` component with a modern, minimalist design inspired by contemporary space visualizations.

**Features:**
- Transparent circle outline using ring geometry
- Simple geometric icon in the center (upload, history, info)
- HTML text labels above the circle (label, subtitle, description)
- Positioned in spiral arms of the galaxy
- Subtle glow effect on the circle border
- Hover state with brightening and scaling effects
- Click interaction support

**Requirements Addressed:**
- 1.2: Display at least three distinct navigation nodes
- 6.1: Create Model node with vibrant purple tones
- 6.2: Past Models node with amber-gold tones
- 6.3: Info node with cool cyan tones

**Usage:**

```tsx
import { NavigationNode } from './components/navigation';
import { NAVIGATION_NODES } from './config/navigationNodes';

function Scene() {
  const handleClick = (id: string) => {
    console.log('Node clicked:', id);
  };
  
  const handleHover = (id: string, hovered: boolean) => {
    console.log('Node hover:', id, hovered);
  };
  
  return (
    <>
      {NAVIGATION_NODES.map(config => (
        <NavigationNode
          key={config.id}
          config={config}
          onClick={handleClick}
          onHover={handleHover}
        />
      ))}
    </>
  );
}
```

## Design Notes

### Icon Types

The component supports three icon types, each rendered as simple geometric shapes:

1. **upload** - Upward pointing arrow (for Create Model)
2. **history** - Clock/circular icon (for Past Models)
3. **info** - Letter 'i' shape (for Information)

Icons are created using Three.js `Shape` and `ExtrudeGeometry` for clean, scalable vector graphics.

### Color Scheme

Each node type has its own color palette defined in `colorPalette.ts`:

- **Create Model**: Purple circle (#B24BF3) with cyan glow (#00D9FF)
- **Past Models**: Amber circle (#FFB84D) with golden glow (#FFA726)
- **Info**: Cyan circle (#00D9FF) with bright cyan glow (#4DD0E1)

### Hover Effects

On hover, the node:
1. Brightens the circle color
2. Increases opacity
3. Scales up the icon (1.1x)
4. Shows additional description text
5. Displays a pulsing highlight ring
6. Changes cursor to pointer

### Text Labels

Text labels are rendered using `@react-three/drei`'s `Html` component, which allows HTML/CSS rendering in 3D space:

- **Label**: Main section name (e.g., "CREATE MODEL")
- **Subtitle**: Secondary text (e.g., "PROGRAMMABLE")
- **Description**: Appears on hover with additional context

## Integration

The NavigationNode component integrates with:

- **navigationNodes.ts**: Configuration for node properties
- **colorPalette.ts**: Color definitions for each node type
- **HighlightGeometry**: Hover highlight effect
- **useInteractionManager**: Raycasting and interaction handling (future)

## Performance Considerations

- Uses `useMemo` for geometry creation to avoid recreation on every render
- Smooth animations using `useFrame` with delta time
- Efficient ring geometry with 64 segments for smooth circles
- HTML labels use CSS transitions for smooth opacity changes
