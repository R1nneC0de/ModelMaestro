# 3D Components

React Three Fiber components for the Galaxy Homepage.

## Subdirectories

### scene/
Main scene setup components:
- GalaxyScene.tsx - Root 3D scene container
- LightingRig.tsx - Three-point lighting setup
- Camera setup and configuration

### celestial/
Celestial body components:
- CelestialBody.tsx - Base planet component
- ProceduralStarField.tsx - Background star generation
- HighlightGeometry.tsx - Hover effects

### particles/
Particle system components:
- ParticleSystem.tsx - Base particle system
- Body-specific particle effects
- Connection path particles

### effects/
Post-processing and visual effects:
- MultiLayerRenderer.tsx - Three-layer rendering pipeline
- BloomEffect.tsx - Selective bloom
- CompositionShader integration

### ui/
UI overlay components:
- SectionOverlay.tsx - Context-sensitive overlays
- FileUploadOverlay.tsx - Create Model section
- HistoryBrowserOverlay.tsx - Past Models section
- InfoOverlay.tsx - Info section
- NavigationHUD.tsx - Persistent navigation hints

### navigation/
Camera and navigation components:
- CameraController.tsx - Camera management
- InteractionManager.tsx - Raycasting and input
- TravelController integration
