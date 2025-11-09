# 3D Galaxy Homepage

This directory contains all 3D-specific code for the Galaxy Homepage experience.

## Directory Structure

- **components/** - React Three Fiber components
  - **scene/** - Main scene setup and containers
  - **celestial/** - Celestial body components (planets, stars)
  - **particles/** - Particle system components
  - **effects/** - Post-processing and visual effects
  - **ui/** - UI overlay components
  - **navigation/** - Camera and navigation components

- **config/** - Configuration files
  - Color palettes
  - Celestial body configurations
  - Galaxy generation parameters
  - Render settings

- **hooks/** - Custom React hooks for 3D interactions
  - Camera control hooks
  - Interaction management hooks
  - Performance monitoring hooks

- **utils/** - Utility functions
  - Galaxy generation algorithms
  - Camera calculations
  - Coordinate transformations

- **shaders/** - Custom GLSL shaders
  - Composition shaders
  - Custom material shaders

- **types/** - TypeScript type definitions
  - 3D-specific interfaces
  - Configuration types

## Technology Stack

- React Three Fiber (R3F) - Declarative Three.js
- Three.js - WebGL rendering
- @react-three/drei - R3F helpers
- @react-three/postprocessing - Post-processing effects
- @tweenjs/tween.js - Camera animations
- Zustand - State management
