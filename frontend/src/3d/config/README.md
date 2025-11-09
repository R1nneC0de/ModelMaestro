# Configuration Files

Configuration files for the 3D Galaxy Homepage.

## Files

### celestialBodies.ts
Configuration for the three main navigable planets:
- Create Model planet (purple/blue)
- Past Models planet (amber/gold)
- Info planet (cyan/white)

Includes position, scale, colors, orbital properties, and camera positioning.

### galaxyConfig.ts
Parameters for procedural star field generation:
- Star counts and distribution
- Core, outer core, and spiral arm settings
- Galaxy thickness and haze ratio

### renderConfig.ts
Rendering pipeline settings:
- Layer constants (BASE_LAYER, BLOOM_LAYER, OVERLAY_LAYER)
- Bloom parameters (strength, threshold, radius)
- Star size ranges and haze opacity

### colorPalette.ts
All color definitions:
- Background colors
- Celestial body colors
- Glow colors and accent colors
- Color temperatures for each planet type

### performancePresets.ts
Quality level configurations:
- HIGH, MEDIUM, LOW presets
- Star counts, particle counts, effects per level
- Texture sizes and postprocessing options
