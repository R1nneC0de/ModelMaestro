# Scene Components

Core 3D scene setup components for the Galaxy Homepage.

## Components

### GalaxyScene

Main container for the entire 3D galaxy experience. Sets up the React Three Fiber Canvas with proper camera configuration, fog, and rendering settings.

**Features:**
- Camera positioned at [0, 500, 500] with FOV 60
- FogExp2 for atmospheric depth
- Automatic window resize handling via R3F
- Performance mode support (high/medium/low/auto)
- Scene ready callback

**Requirements Met:**
- 1.1: Render complete 3D cosmic scene
- 1.2: Display celestial bodies
- 10.3: Scene configuration

**Usage:**
```tsx
<GalaxyScene onSceneReady={() => console.log('Ready!')} performanceMode="high">
  {/* Your 3D content here */}
</GalaxyScene>
```

### LightingRig

Three-point lighting setup for cinematic quality rendering.

**Features:**
- Key Light: Primary directional light (intensity 1.2, position [100, 200, 100])
- Fill Light: Softens shadows (intensity 0.4, position [-100, 50, -50])
- Rim Light: Edge definition (intensity 0.8, position [0, -100, 200])
- Ambient Light: Base illumination (intensity 0.2)

**Requirements Met:**
- 10.3: Three-point lighting with proper configuration

**Usage:**
```tsx
<LightingRig 
  keyLightIntensity={1.2}
  fillLightIntensity={0.4}
  rimLightIntensity={0.8}
  ambientLightIntensity={0.2}
/>
```

## Implementation Notes

- All components use TypeScript for type safety
- Camera configuration follows design specifications
- Fog density set to 0.00005 for subtle atmospheric effect
- Lighting colors defined in colorPalette.ts
- Performance mode affects antialiasing and shadow settings
