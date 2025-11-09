# Design Document

## Overview

This design document outlines the technical architecture for the Agentic ML 3D Galaxy Homepage - a complete frontend redesign that transforms the platform into an immersive, cinematic spatial navigation experience. The design combines the proven navigation patterns from Galaxy1 (solar system with TravelController) with the modern rendering quality of Galaxy2 (procedural generation and multi-layer composition).

The system will be built using React Three Fiber (R3F) for declarative Three.js integration, TypeScript for type safety, and modern React patterns for state management. The architecture prioritizes performance, maintainability, and cinematic quality while ensuring all existing platform functionality remains accessible through the 3D interface.

### Design Philosophy

**Cinematic First**: Every interaction should feel like a scene from a sci-fi film - smooth camera movements, dramatic lighting, and atmospheric effects that create emotional engagement.

**Spatial Storytelling**: The 3D space itself communicates meaning - orbital patterns represent iteration cycles, energy flows show data movement, and proximity indicates relationships.

**Performance Balanced**: Premium visuals with intelligent fallbacks ensure the experience works across device capabilities without compromising core functionality.

**Accessibility Inclusive**: 3D navigation as the primary interface with 2D alternatives for users who need or prefer them.

## Architecture

### High-Level System Architecture


```
┌─────────────────────────────────────────────────────────────────┐
│                     React Application Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   App.tsx    │  │  Router      │  │  State Mgmt  │          │
│  │  (Root)      │──│  (Optional)  │──│  (Zustand)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   3D Scene Layer (R3F Canvas)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  GalaxyScene.tsx (Main 3D Container)                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │  Camera    │  │  Lighting  │  │  Controls  │        │   │
│  │  │  System    │  │  Rig       │  │  Manager   │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┴────────────────────────────┐     │
│  │                                                         │     │
│  ▼                          ▼                             ▼     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Procedural   │  │  Celestial   │  │  Particle    │          │
│  │ Star Field   │  │  Bodies      │  │  Systems     │          │
│  │ (Galaxy2)    │  │  (Planets)   │  │  (Effects)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Navigation & Interaction Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Travel      │  │  Raycaster   │  │  Event       │          │
│  │  Controller  │──│  (Click      │──│  System      │          │
│  │  (Galaxy1)   │  │  Detection)  │  │  (Custom)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Rendering Pipeline Layer                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  EffectComposer (Post-Processing)                        │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │  Bloom     │→ │  Overlay   │→ │ Composition│        │   │
│  │  │  Pass      │  │  Pass      │  │  Shader    │        │   │
│  │  │ (Layer 1)  │  │ (Layer 2)  │  │  (Final)   │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UI Overlay Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Section     │  │  File Upload │  │  History     │          │
│  │  Overlays    │  │  Interface   │  │  Browser     │          │
│  │  (HTML/CSS)  │  │  (Functional)│  │  (Functional)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Core Framework**
- React 18+ with TypeScript
- React Three Fiber (R3F) for declarative Three.js
- Three.js r150+ for WebGL rendering
- @react-three/drei for helpers and abstractions
- @react-three/postprocessing for effects

**State Management**
- Zustand for global state (navigation, UI visibility)
- React Context for 3D scene state
- Custom hooks for animation state

**Animation & Tweening**
- @tweenjs/tween.js for camera flights
- React Spring (via R3F) for UI animations
- GSAP (optional) for complex sequences

**Performance**
- React.memo for component optimization
- useMemo/useCallback for expensive computations
- Instanced meshes for repeated geometry
- LOD (Level of Detail) for distant objects



## Components and Interfaces

### Core 3D Components

#### GalaxyScene Component
Main container for the entire 3D experience.

```typescript
interface GalaxySceneProps {
  onSceneReady?: () => void;
  performanceMode?: 'high' | 'medium' | 'low' | 'auto';
}

// Responsibilities:
// - Initialize Three.js scene via R3F Canvas
// - Set up camera, lighting, and fog
// - Manage rendering pipeline
// - Handle window resize
// - Coordinate child components
```

#### ProceduralStarField Component
Generates and renders the background galaxy using Galaxy2 algorithm.

```typescript
interface StarFieldConfig {
  numStars: number;          // Default: 7000
  coreXDist: number;         // Core region X distribution
  coreYDist: number;         // Core region Y distribution
  outerCoreXDist: number;    // Outer core X distribution
  outerCoreYDist: number;    // Outer core Y distribution
  armXDist: number;          // Spiral arm X distribution
  armYDist: number;          // Spiral arm Y distribution
  armXMean: number;          // Spiral arm X mean
  armYMean: number;          // Spiral arm Y mean
  numArms: number;           // Number of spiral arms
  galaxyThickness: number;   // Z-axis thickness
  hazeRatio: number;         // Ratio of haze particles to stars
}

// Responsibilities:
// - Generate star positions using Gaussian distribution
// - Create sprite-based stars with distance scaling
// - Render haze particles for atmosphere
// - Assign stars to BLOOM_LAYER
// - Update star scales based on camera distance
```

#### CelestialBody Component
Represents a navigable planet (Create Model, Past Models, Info).

```typescript
interface CelestialBodyProps {
  id: string;                    // Unique identifier
  position: [number, number, number];
  scale: number;
  color: string;                 // Primary color (hex)
  glowColor: string;             // Glow/bloom color
  type: 'create' | 'history' | 'info';
  orbitRadius?: number;          // Optional orbital motion
  orbitSpeed?: number;
  onClick?: (id: string) => void;
  onHover?: (id: string, hovered: boolean) => void;
}

// Responsibilities:
// - Render planet mesh with custom material
// - Apply glow effects and particle systems
// - Handle hover and click interactions
// - Animate orbital motion
// - Display highlight geometry on hover
// - Scale up when focused
```



#### TravelController Hook
Custom React hook managing camera navigation (based on Galaxy1 TravelController).

```typescript
interface TravelState {
  isTransitioning: boolean;
  currentTarget: string | null;
  phase: 'idle' | 'takeoff' | 'traveling' | 'landing' | 'focused';
}

interface TravelControllerReturn {
  travelTo: (targetId: string) => Promise<void>;
  returnToOverview: () => Promise<void>;
  state: TravelState;
}

// Responsibilities:
// - Calculate destination coordinates based on target
// - Execute two-phase camera animation (takeoff + approach)
// - Use TWEEN.js with Cubic.InOut easing
// - Dispatch travel events (start, complete)
// - Prevent navigation during transitions
// - Update camera target and lookAt
```

#### InteractionManager Component
Handles raycasting and user input detection.

```typescript
interface InteractionManagerProps {
  celestialBodies: CelestialBodyProps[];
  onBodyClick: (id: string) => void;
  onBodyHover: (id: string, hovered: boolean) => void;
  enabled: boolean;
}

// Responsibilities:
// - Set up raycaster for mouse/touch input
// - Detect intersections with celestial bodies
// - Emit hover events with debouncing
// - Emit click events
// - Handle keyboard navigation (Tab, Enter, Arrows)
// - Provide visual cursor feedback
```

### Rendering Pipeline Components

#### MultiLayerRenderer Component
Implements Galaxy2's three-layer rendering approach.

```typescript
interface RenderLayer {
  name: 'base' | 'bloom' | 'overlay';
  layerIndex: number;
  enabled: boolean;
}

// Responsibilities:
// - Configure EffectComposer with three passes
// - Render bloom pass (layer 1) to texture
// - Render overlay pass (layer 2) to texture
// - Combine layers using CompositionShader
// - Apply final output to screen
```

#### BloomEffect Component
Configures UnrealBloomPass for selective glow.

```typescript
interface BloomConfig {
  strength: number;      // Default: 1.5
  threshold: number;     // Default: 0.4
  radius: number;        // Default: 0
  exposure: number;      // Default: 1.0
}

// Responsibilities:
// - Apply bloom only to BLOOM_LAYER objects
// - Adjust bloom parameters based on performance mode
// - Provide runtime bloom intensity control
```



### UI Overlay Components

#### SectionOverlay Component
Context-sensitive UI that appears when focusing on a celestial body.

```typescript
interface SectionOverlayProps {
  sectionId: 'create' | 'history' | 'info';
  visible: boolean;
  position: { x: number; y: number };  // Screen space coordinates
  onClose?: () => void;
}

// Responsibilities:
// - Render HTML/CSS overlay positioned in screen space
// - Animate entrance/exit with fade and slide
// - Display section-specific content
// - Embed functional components (FileUpload, HistoryList, etc.)
// - Handle close/back navigation
```

#### FileUploadOverlay Component
Embedded in Create Model section overlay.

```typescript
interface FileUploadOverlayProps {
  onFileSelect: (file: File) => void;
  onTrainingStart: (config: TrainingConfig) => void;
  visible: boolean;
}

// Responsibilities:
// - Reuse existing file validation logic
// - Display upload progress
// - Show training configuration options
// - Trigger data particle animation on upload
// - Integrate with backend API
```

#### HistoryBrowserOverlay Component
Embedded in Past Models section overlay.

```typescript
interface HistoryBrowserOverlayProps {
  sessions: TrainingSession[];
  onSessionSelect: (sessionId: string) => void;
  visible: boolean;
}

// Responsibilities:
// - Display scrollable list of training sessions
// - Show session cards with key metrics
// - Handle session detail view
// - Integrate with existing history API
```

#### NavigationHUD Component
Persistent heads-up display for navigation hints.

```typescript
interface NavigationHUDProps {
  currentSection: string | null;
  showControls: boolean;
  reducedMotion: boolean;
}

// Responsibilities:
// - Display current location
// - Show navigation controls (click to explore, ESC to return)
// - Provide accessibility shortcuts
// - Show loading states
// - Display performance warnings if needed
```



## Data Models

### Celestial Body Configuration

```typescript
interface CelestialBodyConfig {
  id: string;
  type: 'create' | 'history' | 'info';
  name: string;
  description: string;
  position: Vector3;
  scale: number;
  
  // Visual properties
  color: string;              // Primary color (hex)
  glowColor: string;          // Bloom glow color
  emissiveIntensity: number;  // Material emissive strength
  
  // Orbital properties
  orbitRadius: number;
  orbitSpeed: number;
  orbitAxis: Vector3;
  
  // Interaction properties
  clickable: boolean;
  hoverHighlight: boolean;
  
  // Particle effects
  particleSystem?: ParticleSystemConfig;
  
  // Camera positioning
  cameraOffset: Vector3;      // Offset from body center
  cameraDistance: number;     // Distance multiplier
}
```

### Star Configuration

```typescript
interface StarConfig {
  position: Vector3;
  starType: number;           // Index into star type distribution
  size: number;               // Base size before distance scaling
  color: string;              // Color based on star type
  layer: number;              // Rendering layer (BLOOM_LAYER)
}

interface StarTypeDistribution {
  colors: string[];           // Array of star colors by type
  sizes: number[];            // Array of base sizes by type
  percentages: number[];      // Distribution percentages (sum to 100)
}
```

### Navigation State

```typescript
interface NavigationState {
  // Current state
  currentView: 'overview' | 'focused';
  focusedBodyId: string | null;
  
  // Transition state
  isTransitioning: boolean;
  transitionPhase: 'idle' | 'takeoff' | 'traveling' | 'landing';
  transitionProgress: number;  // 0 to 1
  
  // Camera state
  cameraPosition: Vector3;
  cameraTarget: Vector3;
  cameraLookAt: Vector3;
  
  // Interaction state
  hoveredBodyId: string | null;
  interactionEnabled: boolean;
  
  // History
  navigationHistory: string[];  // Stack of visited body IDs
}
```

### Performance State

```typescript
interface PerformanceState {
  mode: 'high' | 'medium' | 'low';
  fps: number;
  frameTime: number;
  
  // Feature flags based on performance
  bloomEnabled: boolean;
  particlesEnabled: boolean;
  shadowsEnabled: boolean;
  antialiasEnabled: boolean;
  
  // Adaptive quality
  starCount: number;
  particleCount: number;
  textureQuality: 'high' | 'medium' | 'low';
}
```



## Artistic Direction

### Color Palette

**Background & Atmosphere**
- Deep Space Blue: `#0A0E27` (darkest background)
- Space Blue Mid: `#1A1F3A` (gradient mid-tone)
- Nebula Purple: `#2D1B3D` (atmospheric accents)
- Fog Color: `#EBE2DB` (subtle fog for depth)

**Celestial Body Colors**

*Create Model Planet*
- Primary: `#B24BF3` (vibrant purple)
- Glow: `#00D9FF` (electric blue)
- Particles: `#7B2FFF` (deep purple)
- Temperature: 5000K (vibrant, energetic)
- Metaphor: Creation, innovation, new beginnings

*Past Models Planet*
- Primary: `#FFB84D` (warm amber)
- Glow: `#FFA726` (golden orange)
- Particles: `#FF8A00` (deep orange)
- Temperature: 3500K (warm, historical)
- Metaphor: History, accumulated knowledge, archives

*Info Planet*
- Primary: `#00D9FF` (cool cyan)
- Glow: `#4DD0E1` (bright cyan)
- Particles: `#00BCD4` (cyan blue)
- Temperature: 6500K (cool, informative)
- Metaphor: Clarity, information, guidance

**Accent Colors**
- Connection Lines: `#4DD0E1` with 40% opacity
- Hover Highlight: `#00FFFF` (bright cyan)
- Active State: `#B24BF3` (purple)
- Warning/Error: `#FF5252` (red)
- Success: `#69F0AE` (green)

### Lighting Setup

**Three-Point Lighting Rig**

```typescript
interface LightingConfig {
  keyLight: {
    type: 'DirectionalLight';
    color: '#FFFFFF';
    intensity: 1.2;
    position: [100, 200, 100];
    castShadow: boolean;
  };
  
  fillLight: {
    type: 'DirectionalLight';
    color: '#B3D9FF';  // Slight blue tint
    intensity: 0.4;
    position: [-100, 50, -50];
  };
  
  rimLight: {
    type: 'DirectionalLight';
    color: '#FFE0B3';  // Slight warm tint
    intensity: 0.8;
    position: [0, -100, 200];
  };
  
  ambientLight: {
    type: 'AmbientLight';
    color: '#1A1F3A';
    intensity: 0.2;
  };
}
```

**Dynamic Lighting Effects**
- Point lights attached to each celestial body
- Pulsing intensity for active/training states
- Color temperature shifts during transitions
- Rim lighting for depth and separation



### Material Design

**Celestial Body Materials**

```typescript
interface PlanetMaterialConfig {
  type: 'MeshStandardMaterial' | 'MeshPhysicalMaterial';
  
  // Base properties
  color: string;
  metalness: number;      // 0.3 for slight metallic look
  roughness: number;      // 0.7 for diffuse surface
  
  // Emission (glow)
  emissive: string;       // Same as glow color
  emissiveIntensity: number;  // 0.5-1.5 range
  
  // Advanced properties (Physical material)
  clearcoat?: number;     // 0.3 for atmosphere effect
  clearcoatRoughness?: number;  // 0.4
  transmission?: number;  // 0 (opaque)
  
  // Textures (optional)
  map?: Texture;          // Albedo/color texture
  normalMap?: Texture;    // Surface detail
  emissiveMap?: Texture;  // Glow pattern
}
```

**Star Sprite Materials**

```typescript
interface StarMaterialConfig {
  type: 'SpriteMaterial';
  map: Texture;           // Circular gradient texture
  color: string;          // Star type color
  transparent: true;
  blending: AdditiveBlending;  // For glow effect
  depthWrite: false;      // Prevent z-fighting
  sizeAttenuation: true;  // Scale with distance
}
```

**Particle System Materials**

```typescript
interface ParticleMaterialConfig {
  type: 'PointsMaterial' | 'ShaderMaterial';
  size: number;           // 0.5-2.0 range
  color: string;
  transparent: true;
  opacity: number;        // 0.3-0.8 range
  blending: AdditiveBlending;
  depthWrite: false;
  vertexColors: boolean;  // For color variation
}
```

### Camera Configuration

**Overview Camera Position**
- Position: `[0, 500, 500]`
- LookAt: `[0, 0, 0]`
- FOV: 60 degrees
- Near: 0.1
- Far: 5,000,000
- Up Vector: `[0, 0, 1]` (Z-up orientation)

**Focused Camera Positions**
Calculated dynamically based on target body:
- Distance: `bodyDiameter * 3` to `bodyDiameter * 6`
- Offset: Positioned in quadrant relative to body position
- LookAt: Body center position
- Smooth interpolation during transitions

**Camera Controls**
- Type: MapControls (OrbitControls variant)
- Damping: Enabled (factor: 0.05)
- Pan: Screen space panning disabled
- Zoom: Min distance 1, Max distance 16,384
- Polar Angle: Max `(π/2) - (π/360)` (prevent flipping)



## Navigation Model

### Camera Flight Choreography

**Two-Phase Animation System** (based on Galaxy1 TravelController)

**Phase 1: Takeoff (3 seconds)**
```typescript
interface TakeoffPhase {
  duration: 3000;  // milliseconds
  easing: 'Cubic.InOut';
  
  from: {
    position: currentCameraPosition;
    target: currentTarget;
  };
  
  to: {
    position: {
      x: currentCameraPosition.x,
      y: currentCameraPosition.y,
      z: currentCameraPosition.z + takeoffHeight + 700
    };
    target: targetBodyPosition;
  };
  
  onUpdate: () => {
    // Update camera lookAt to target body
    // Update orbit controls target
    // Maintain smooth tracking
  };
}
```

**Phase 2: Approach (5 seconds)**
```typescript
interface ApproachPhase {
  duration: 5000;  // milliseconds
  easing: 'Cubic.InOut';
  
  from: {
    position: takeoffEndPosition;
    target: targetBodyPosition;
  };
  
  to: {
    position: calculateDestinationCoordinates(targetBody);
    target: targetBodyPosition;
  };
  
  onUpdate: () => {
    // Recalculate destination if body is orbiting
    // Update highlight size based on distance
    // Apply parallax to background stars
  };
  
  onComplete: () => {
    // Fade highlight color
    // Show section overlay
    // Enable section interactions
    // Dispatch travel complete event
  };
}
```

**Return to Overview**
```typescript
interface ReturnPhase {
  duration: 4000;  // milliseconds
  easing: 'Cubic.InOut';
  
  from: {
    position: currentCameraPosition;
    target: currentTarget;
  };
  
  to: {
    position: [0, 500, 500];
    target: [0, 0, 0];
  };
  
  onStart: () => {
    // Hide section overlay with fade
    // Remove highlight geometry
    // Reset interaction state
  };
}
```

### Destination Coordinate Calculation

```typescript
function calculateDestinationCoordinates(
  targetBody: CelestialBodyConfig
): Vector3 {
  const x = targetBody.position.x;
  const y = targetBody.position.y;
  const z = targetBody.position.z;
  
  // Determine quadrant for offset direction
  const quadrant = getQuadrant(x, y);
  
  // Calculate offset based on body size
  const offset = targetBody.scale > 3 
    ? targetBody.scale * 6 
    : targetBody.scale * 3;
  
  // Apply offset based on quadrant
  const [offsetX, offsetY] = applyQuadrantOffset(
    x, y, offset, quadrant
  );
  
  // Z offset based on body type
  const offsetZ = targetBody.type === 'info'
    ? z + (targetBody.scale * 50)
    : z + (targetBody.scale * 25);
  
  return new Vector3(offsetX, offsetY, offsetZ);
}
```



### Interaction Flow

**User Journey: Overview → Section → Functionality**

```
1. Initial Load (Overview State)
   ├─ User sees galaxy with 3 celestial bodies
   ├─ Navigation HUD shows "Click to explore"
   ├─ Camera at overview position [0, 500, 500]
   └─ All bodies slowly orbiting

2. Hover Interaction
   ├─ Raycaster detects mouse over body
   ├─ Highlight geometry appears (100ms)
   ├─ Tooltip shows section name
   ├─ Cursor changes to pointer
   └─ Body emissive intensity increases

3. Click Interaction
   ├─ User clicks on body
   ├─ Interaction disabled during transition
   ├─ Travel controller initiates
   ├─ Phase 1: Takeoff (3s)
   │   ├─ Camera rises vertically
   │   ├─ Camera target locks to body
   │   └─ Background stars parallax
   ├─ Phase 2: Approach (5s)
   │   ├─ Camera flies to destination
   │   ├─ Highlight scales dynamically
   │   ├─ Body scales up 10-20%
   │   └─ Parallax continues
   └─ Landing complete

4. Focused State
   ├─ Section overlay fades in (500ms)
   ├─ Highlight fades to cyan (3s)
   ├─ Functional UI becomes interactive
   ├─ Navigation HUD shows "ESC to return"
   └─ User can interact with section features

5. Section Interaction
   ├─ Create Model: Upload file, configure training
   ├─ Past Models: Browse history, view details
   └─ Info: Read about platform, view docs

6. Return to Overview
   ├─ User presses ESC or clicks "Back"
   ├─ Section overlay fades out (300ms)
   ├─ Camera returns to overview (4s)
   ├─ Body scales back to normal
   └─ Interaction re-enabled
```

### Keyboard Navigation

```typescript
interface KeyboardControls {
  'Tab': 'Cycle through celestial bodies';
  'Enter': 'Select focused body';
  'Escape': 'Return to overview';
  'ArrowLeft': 'Previous body';
  'ArrowRight': 'Next body';
  'Space': 'Pause/resume orbital motion';
  '1': 'Jump to Create Model';
  '2': 'Jump to Past Models';
  '3': 'Jump to Info';
}
```



## Postprocessing Stack

### Multi-Layer Rendering Pipeline

**Layer Configuration**
```typescript
const LAYERS = {
  BASE: 0,      // Normal geometry, UI elements
  BLOOM: 1,     // Stars, glowing elements, particles
  OVERLAY: 2    // UI overlays, text, controls
};
```

**Rendering Sequence**

```typescript
function renderPipeline() {
  // Pass 1: Render bloom layer
  camera.layers.set(LAYERS.BLOOM);
  bloomComposer.render();
  
  // Pass 2: Render overlay layer
  camera.layers.set(LAYERS.OVERLAY);
  overlayComposer.render();
  
  // Pass 3: Render base layer with composition
  camera.layers.set(LAYERS.BASE);
  baseComposer.render();
}
```

### Effect Configuration

**UnrealBloomPass**
```typescript
interface BloomPassConfig {
  resolution: Vector2;    // window.innerWidth x innerHeight
  strength: 1.5;          // Bloom intensity
  threshold: 0.4;         // Luminance threshold
  radius: 0;              // Bloom spread radius
}

// Applied only to BLOOM_LAYER objects
// Stars, planet glows, particles, energy streams
```

**CompositionShader**
```glsl
// Fragment Shader
uniform sampler2D baseTexture;
uniform sampler2D bloomTexture;
uniform sampler2D overlayTexture;

varying vec2 vUv;

void main() {
  vec4 base = texture2D(baseTexture, vUv);
  vec4 bloom = texture2D(bloomTexture, vUv);
  vec4 overlay = texture2D(overlayTexture, vUv);
  
  // Additive blending for bloom
  vec4 result = base + bloom;
  
  // Alpha blend overlay on top
  result = mix(result, overlay, overlay.a);
  
  gl_FragColor = result;
}
```

**Additional Effects (Optional/Performance-Based)**

*Vignette Effect*
```typescript
interface VignetteConfig {
  offset: 0.3;      // Inner radius
  darkness: 0.8;    // Outer darkness
}
```

*Film Grain*
```typescript
interface FilmGrainConfig {
  intensity: 0.15;  // Grain strength
  animated: true;   // Animate grain pattern
}
```

*Chromatic Aberration*
```typescript
interface ChromaticAberrationConfig {
  offset: 0.002;    // RGB channel separation
  radialModulation: true;  // Stronger at edges
}
```

*Depth of Field (DOF)*
```typescript
interface DOFConfig {
  focusDistance: number;    // Dynamic based on target
  focalLength: 0.02;
  bokehScale: 2.0;
  enabled: boolean;         // Only in focused state
}
```



## Scene Structure

### Spatial Layout

**Celestial Body Positioning**

```typescript
const CELESTIAL_BODIES: CelestialBodyConfig[] = [
  {
    id: 'create-model',
    type: 'create',
    name: 'Create Model',
    description: 'Start a new training workflow',
    position: new Vector3(-200, 150, 0),
    scale: 15,
    color: '#B24BF3',
    glowColor: '#00D9FF',
    emissiveIntensity: 1.2,
    orbitRadius: 50,
    orbitSpeed: 0.0002,
    orbitAxis: new Vector3(0, 0, 1),
    cameraDistance: 4
  },
  {
    id: 'past-models',
    type: 'history',
    name: 'Past Models',
    description: 'Browse your training history',
    position: new Vector3(200, -100, -50),
    scale: 18,
    color: '#FFB84D',
    glowColor: '#FFA726',
    emissiveIntensity: 1.0,
    orbitRadius: 30,
    orbitSpeed: 0.00015,
    orbitAxis: new Vector3(0, 0, 1),
    cameraDistance: 5
  },
  {
    id: 'info',
    type: 'info',
    name: 'Information',
    description: 'Learn about the platform',
    position: new Vector3(0, 200, 100),
    scale: 12,
    color: '#00D9FF',
    glowColor: '#4DD0E1',
    emissiveIntensity: 0.9,
    orbitRadius: 20,
    orbitSpeed: 0.0003,
    orbitAxis: new Vector3(0, 0, 1),
    cameraDistance: 3.5
  }
];
```

**Depth Layering**
- Background stars: Z range [-1000, -500]
- Procedural galaxy core: Z range [-200, 200]
- Celestial bodies: Z range [-100, 100]
- Particle effects: Z range [-50, 150]
- UI overlays: Screen space (no Z)

**Connection Paths**
```typescript
interface ConnectionPath {
  from: string;         // Body ID
  to: string;           // Body ID
  color: string;        // Line color
  opacity: number;      // 0.3-0.5 range
  animated: boolean;    // Pulse animation
  particles: boolean;   // Traveling particles
}

const CONNECTIONS: ConnectionPath[] = [
  {
    from: 'create-model',
    to: 'past-models',
    color: '#4DD0E1',
    opacity: 0.4,
    animated: true,
    particles: true  // Show when training completes
  }
];
```

### Particle Systems

**Ambient Data Particles**
```typescript
interface AmbientParticleConfig {
  count: 2000;
  distribution: 'spherical';  // Around scene center
  radius: 400;
  size: 0.5;
  color: '#4DD0E1';
  opacity: 0.3;
  speed: 0.1;
  direction: 'random';
}
```

**Body-Specific Particles**

*Create Model - Energy Particles*
```typescript
interface EnergyParticleConfig {
  count: 500;
  distribution: 'orbital';  // Around body
  radius: 20;
  size: 1.0;
  colors: ['#B24BF3', '#00D9FF', '#7B2FFF'];
  opacity: 0.6;
  speed: 0.3;
  behavior: 'orbit';  // Orbit around body
}
```

*Past Models - Archive Rings*
```typescript
interface RingParticleConfig {
  count: 800;
  distribution: 'ring';  // Multiple rings
  rings: 3;
  radius: [25, 30, 35];
  size: 0.8;
  color: '#FFB84D';
  opacity: 0.5;
  speed: 0.15;
  behavior: 'rotate';  // Rotate around body
}
```

*Info - Stable Glow*
```typescript
interface GlowParticleConfig {
  count: 300;
  distribution: 'surface';  // On body surface
  size: 1.2;
  color: '#00D9FF';
  opacity: 0.7;
  speed: 0.05;
  behavior: 'pulse';  // Gentle pulsing
}
```



## Performance Considerations

### Performance Monitoring

```typescript
interface PerformanceMonitor {
  fps: number;
  frameTime: number;
  drawCalls: number;
  triangles: number;
  
  // Thresholds
  targetFPS: 60;
  minAcceptableFPS: 30;
  
  // Monitoring
  measureInterval: 1000;  // Check every second
  degradationThreshold: 3;  // Consecutive bad frames
  
  // Actions
  onPerformanceDrop: () => void;
  onPerformanceRecover: () => void;
}
```

### Adaptive Quality System

**Quality Levels**

```typescript
enum QualityLevel {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

interface QualitySettings {
  [QualityLevel.HIGH]: {
    starCount: 7000;
    particleCount: 3600;  // Sum of all particle systems
    bloomEnabled: true;
    shadowsEnabled: true;
    antialiasEnabled: true;
    textureSize: 2048;
    postprocessing: ['bloom', 'vignette', 'grain', 'chromatic'];
  };
  
  [QualityLevel.MEDIUM]: {
    starCount: 4000;
    particleCount: 1800;
    bloomEnabled: true;
    shadowsEnabled: false;
    antialiasEnabled: true;
    textureSize: 1024;
    postprocessing: ['bloom', 'vignette'];
  };
  
  [QualityLevel.LOW]: {
    starCount: 2000;
    particleCount: 600;
    bloomEnabled: false;
    shadowsEnabled: false;
    antialiasEnabled: false;
    textureSize: 512;
    postprocessing: [];
  };
}
```

**Auto-Detection Logic**

```typescript
function detectOptimalQuality(): QualityLevel {
  const gpu = detectGPU();
  const memory = navigator.deviceMemory || 4;
  const isMobile = /mobile/i.test(navigator.userAgent);
  
  if (isMobile) {
    return QualityLevel.LOW;
  }
  
  if (gpu.tier >= 3 && memory >= 8) {
    return QualityLevel.HIGH;
  }
  
  if (gpu.tier >= 2 && memory >= 4) {
    return QualityLevel.MEDIUM;
  }
  
  return QualityLevel.LOW;
}
```

### Optimization Techniques

**Geometry Instancing**
```typescript
// Use InstancedMesh for repeated geometry
const starGeometry = new SphereGeometry(1, 8, 8);
const starMaterial = new MeshBasicMaterial();
const instancedStars = new InstancedMesh(
  starGeometry,
  starMaterial,
  starCount
);

// Set individual transforms
for (let i = 0; i < starCount; i++) {
  const matrix = new Matrix4();
  matrix.setPosition(positions[i]);
  matrix.scale(scales[i]);
  instancedStars.setMatrixAt(i, matrix);
}
```

**Frustum Culling**
```typescript
// Automatically handled by Three.js
// Ensure objects have proper bounding spheres
celestialBody.geometry.computeBoundingSphere();
```

**Level of Detail (LOD)**
```typescript
const lod = new LOD();

// High detail (close)
lod.addLevel(highDetailMesh, 0);

// Medium detail
lod.addLevel(mediumDetailMesh, 100);

// Low detail (far)
lod.addLevel(lowDetailMesh, 500);

scene.add(lod);
```

**Texture Optimization**
```typescript
// Compress textures
const texture = textureLoader.load('star.png');
texture.minFilter = LinearMipMapLinearFilter;
texture.generateMipmaps = true;

// Use appropriate formats
// - PNG for transparency
// - JPG for opaque textures
// - Basis/KTX2 for maximum compression
```

**Lazy Loading**
```typescript
// Load high-res textures after initial render
useEffect(() => {
  if (sceneReady) {
    setTimeout(() => {
      loadHighResTextures();
    }, 1000);
  }
}, [sceneReady]);
```



### Mobile Considerations

**Touch Interactions**
```typescript
interface TouchControls {
  // Single touch: Rotate camera
  onTouchMove: (delta: Vector2) => void;
  
  // Pinch: Zoom
  onPinch: (scale: number) => void;
  
  // Double tap: Select body
  onDoubleTap: (position: Vector2) => void;
  
  // Long press: Show info
  onLongPress: (position: Vector2) => void;
}
```

**Mobile Optimizations**
- Reduce star count to 1500-2000
- Disable all postprocessing except bloom
- Use lower resolution textures (512px)
- Disable shadows completely
- Reduce particle counts by 70%
- Simplify geometry (lower poly counts)
- Disable ambient particles
- Use simpler materials (MeshBasicMaterial)

**Responsive Layout**
```typescript
interface ResponsiveConfig {
  breakpoints: {
    mobile: 768;
    tablet: 1024;
    desktop: 1920;
  };
  
  adjustments: {
    mobile: {
      cameraFOV: 70;  // Wider FOV
      uiScale: 1.2;   // Larger UI elements
      hitAreaScale: 1.5;  // Larger touch targets
    };
    tablet: {
      cameraFOV: 65;
      uiScale: 1.1;
      hitAreaScale: 1.2;
    };
    desktop: {
      cameraFOV: 60;
      uiScale: 1.0;
      hitAreaScale: 1.0;
    };
  };
}
```

## Error Handling

### WebGL Support Detection

```typescript
function checkWebGLSupport(): {
  supported: boolean;
  version: number;
  message?: string;
} {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || 
               canvas.getContext('webgl');
    
    if (!gl) {
      return {
        supported: false,
        version: 0,
        message: 'WebGL is not supported in your browser'
      };
    }
    
    const version = gl instanceof WebGL2RenderingContext ? 2 : 1;
    
    return {
      supported: true,
      version,
      message: version === 1 
        ? 'WebGL 1.0 detected - some features may be limited'
        : undefined
    };
  } catch (e) {
    return {
      supported: false,
      version: 0,
      message: 'Error detecting WebGL support'
    };
  }
}
```

### Fallback UI

```typescript
interface FallbackUIProps {
  reason: 'no-webgl' | 'performance' | 'error';
  message: string;
  showAlternative: boolean;
}

// Render simple 2D navigation as fallback
function FallbackUI({ reason, message }: FallbackUIProps) {
  return (
    <div className="fallback-container">
      <h2>3D Experience Unavailable</h2>
      <p>{message}</p>
      
      {reason === 'no-webgl' && (
        <p>Please use a modern browser with WebGL support.</p>
      )}
      
      <div className="alternative-nav">
        <button onClick={() => navigate('/create')}>
          Create Model
        </button>
        <button onClick={() => navigate('/history')}>
          Past Models
        </button>
        <button onClick={() => navigate('/info')}>
          Information
        </button>
      </div>
    </div>
  );
}
```

### Error Boundaries

```typescript
class Galaxy3DErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Galaxy 3D Error:', error, errorInfo);
    // Log to error tracking service
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <FallbackUI 
          reason="error"
          message="An error occurred loading the 3D experience"
          showAlternative={true}
        />
      );
    }
    
    return this.props.children;
  }
}
```



## Testing Strategy

### Unit Testing

**Component Tests**
```typescript
describe('CelestialBody', () => {
  it('should render with correct position and scale', () => {
    const body = render(
      <CelestialBody 
        position={[0, 0, 0]}
        scale={10}
        color="#B24BF3"
      />
    );
    expect(body.position).toEqual([0, 0, 0]);
  });
  
  it('should emit click event when clicked', () => {
    const onClick = jest.fn();
    const body = render(
      <CelestialBody onClick={onClick} />
    );
    fireEvent.click(body);
    expect(onClick).toHaveBeenCalled();
  });
});
```

**Hook Tests**
```typescript
describe('useTravelController', () => {
  it('should transition to traveling state', async () => {
    const { result } = renderHook(() => useTravelController());
    
    act(() => {
      result.current.travelTo('create-model');
    });
    
    expect(result.current.state.isTransitioning).toBe(true);
    expect(result.current.state.phase).toBe('takeoff');
  });
});
```

### Integration Testing

**Navigation Flow Tests**
```typescript
describe('Galaxy Navigation', () => {
  it('should complete full navigation cycle', async () => {
    render(<GalaxyScene />);
    
    // Click on Create Model body
    const createBody = screen.getByTestId('body-create-model');
    fireEvent.click(createBody);
    
    // Wait for transition
    await waitFor(() => {
      expect(screen.getByText('Create Model')).toBeVisible();
    }, { timeout: 10000 });
    
    // Verify overlay is shown
    expect(screen.getByTestId('section-overlay')).toBeInTheDocument();
    
    // Return to overview
    fireEvent.keyDown(document, { key: 'Escape' });
    
    await waitFor(() => {
      expect(screen.queryByTestId('section-overlay')).not.toBeInTheDocument();
    });
  });
});
```

### Visual Regression Testing

**Snapshot Tests**
```typescript
describe('Visual Regression', () => {
  it('should match overview state snapshot', async () => {
    const { container } = render(<GalaxyScene />);
    await waitForSceneLoad();
    
    const canvas = container.querySelector('canvas');
    const snapshot = canvas.toDataURL();
    
    expect(snapshot).toMatchImageSnapshot();
  });
});
```

### Performance Testing

**FPS Monitoring**
```typescript
describe('Performance', () => {
  it('should maintain 60 FPS in overview state', async () => {
    const monitor = new PerformanceMonitor();
    render(<GalaxyScene performanceMonitor={monitor} />);
    
    await waitFor(() => {
      expect(monitor.averageFPS).toBeGreaterThan(55);
    }, { timeout: 5000 });
  });
  
  it('should maintain 30+ FPS during transitions', async () => {
    const monitor = new PerformanceMonitor();
    const { result } = renderHook(() => useTravelController());
    
    act(() => {
      result.current.travelTo('create-model');
    });
    
    await waitFor(() => {
      expect(monitor.minFPS).toBeGreaterThan(30);
    }, { timeout: 10000 });
  });
});
```

### Accessibility Testing

**Keyboard Navigation**
```typescript
describe('Accessibility', () => {
  it('should support keyboard navigation', () => {
    render(<GalaxyScene />);
    
    // Tab to first body
    fireEvent.keyDown(document, { key: 'Tab' });
    expect(screen.getByTestId('body-create-model')).toHaveFocus();
    
    // Enter to select
    fireEvent.keyDown(document, { key: 'Enter' });
    expect(screen.getByTestId('section-overlay')).toBeVisible();
  });
  
  it('should provide screen reader announcements', () => {
    render(<GalaxyScene />);
    
    const announcement = screen.getByRole('status');
    expect(announcement).toHaveTextContent('Galaxy loaded. 3 sections available.');
  });
});
```



## Visual Metaphor: Galaxy → AI/ML Ecosystem

### Conceptual Mapping

**Galaxy Structure → ML Platform Architecture**

| Galaxy Element | ML Concept | Visual Representation |
|----------------|------------|----------------------|
| Central Core | Platform Core | Bright, dense center with high activity |
| Spiral Arms | Data Pipelines | Flowing streams of particles |
| Stars | Data Points | Individual glowing sprites |
| Planets | Major Features | Large, interactive celestial bodies |
| Orbits | Iteration Cycles | Circular motion representing continuous improvement |
| Connections | Workflows | Light streams between bodies |
| Energy Pulses | Active Training | Animated particles along paths |
| Nebulae/Haze | Data Clouds | Soft, atmospheric particle systems |

### Storytelling Through Motion

**Create Model Planet**
- **Metaphor**: Birth of a new star/model
- **Motion**: Active, energetic particle swirls
- **Color**: Purple/blue (innovation, creation)
- **Behavior**: Pulsing energy, outward particle flow
- **Interaction**: Particles flow inward when data uploaded
- **Training State**: Intense glow, rapid particle movement

**Past Models Planet**
- **Metaphor**: Archive of stellar history
- **Motion**: Stable orbital rings (like Saturn)
- **Color**: Amber/gold (warmth, history, value)
- **Behavior**: Slow, steady rotation
- **Interaction**: Rings expand to reveal individual models
- **Sub-objects**: Each past model as a small moon

**Info Planet**
- **Metaphor**: Lighthouse/beacon of knowledge
- **Motion**: Gentle pulsing, stable presence
- **Color**: Cyan/white (clarity, information)
- **Behavior**: Consistent luminescence
- **Interaction**: Radiates information particles outward

### Dynamic Storytelling Events

**Training Initiation**
```typescript
interface TrainingVisualization {
  trigger: 'training-start';
  effects: [
    {
      type: 'particle-flow';
      from: 'create-model';
      to: 'center';
      duration: 2000;
      color: '#B24BF3';
    },
    {
      type: 'glow-pulse';
      target: 'create-model';
      intensity: [1.0, 2.0];
      frequency: 2;  // Hz
    },
    {
      type: 'energy-ring';
      target: 'create-model';
      expansion: [10, 30];
      duration: 3000;
    }
  ];
}
```

**Training Completion**
```typescript
interface CompletionVisualization {
  trigger: 'training-complete';
  effects: [
    {
      type: 'connection-form';
      from: 'create-model';
      to: 'past-models';
      duration: 3000;
      animation: 'grow';
    },
    {
      type: 'particle-transfer';
      from: 'create-model';
      to: 'past-models';
      count: 200;
      duration: 4000;
    },
    {
      type: 'new-moon';
      parent: 'past-models';
      size: 2;
      color: '#FFB84D';
      orbit: true;
    }
  ];
}
```

**Model Exploration**
```typescript
interface ExplorationVisualization {
  trigger: 'model-hover';
  effects: [
    {
      type: 'info-beam';
      from: 'model-moon';
      to: 'camera';
      color: '#4DD0E1';
      opacity: 0.3;
    },
    {
      type: 'data-preview';
      particles: 50;
      orbit: 'model-moon';
      color: '#FFB84D';
    }
  ];
}
```

### Atmospheric Storytelling

**Ambient Mood**
- Deep space background creates sense of exploration
- Subtle fog adds depth and mystery
- Slow camera drift suggests floating in space
- Particle movement implies living ecosystem
- Glow effects create warmth and invitation

**Emotional Beats**
1. **Wonder** (Initial load): Vast galaxy reveals itself
2. **Curiosity** (Hover): Objects respond to attention
3. **Anticipation** (Click): Journey begins
4. **Focus** (Travel): World narrows to destination
5. **Engagement** (Arrival): Ready to interact
6. **Accomplishment** (Action): Visual feedback confirms success



## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Basic 3D scene with navigation

- Set up React Three Fiber project structure
- Implement GalaxyScene component with camera and lighting
- Create basic CelestialBody components (3 planets)
- Implement ProceduralStarField (simplified, 2000 stars)
- Set up basic OrbitControls
- Implement raycasting for click detection
- Create simple TravelController with TWEEN.js
- Basic camera flight (single phase, 3 seconds)

**Deliverable**: Clickable planets with basic camera transitions

### Phase 2: Visual Polish (Week 2)
**Goal**: Cinematic quality rendering

- Implement multi-layer rendering pipeline
- Add UnrealBloomPass for glow effects
- Create CompositionShader for layer blending
- Enhance star field to 7000 stars with proper distribution
- Add particle systems to each planet
- Implement distance-based star scaling
- Add fog and atmospheric effects
- Create custom planet materials with emission

**Deliverable**: Visually stunning galaxy with bloom and particles

### Phase 3: Advanced Navigation (Week 3)
**Goal**: Smooth, professional camera work

- Implement two-phase camera flight (takeoff + approach)
- Add dynamic destination calculation
- Implement highlight geometry with distance scaling
- Add parallax effects during camera movement
- Create smooth highlight color transitions
- Implement keyboard navigation
- Add navigation state management (Zustand)
- Create NavigationHUD component

**Deliverable**: Professional camera choreography matching Galaxy1 quality

### Phase 4: UI Integration (Week 4)
**Goal**: Functional overlays and interactions

- Create SectionOverlay component system
- Implement FileUploadOverlay (reuse existing logic)
- Implement HistoryBrowserOverlay (reuse existing logic)
- Create InfoOverlay with platform information
- Add overlay animations (fade, slide)
- Integrate with backend APIs
- Implement training visualization effects
- Add connection paths between planets

**Deliverable**: Fully functional platform within 3D interface

### Phase 5: Performance & Polish (Week 5)
**Goal**: Optimization and refinement

- Implement performance monitoring
- Add adaptive quality system
- Optimize geometry with instancing
- Add LOD for distant objects
- Implement lazy loading for textures
- Add mobile optimizations
- Create fallback UI for unsupported browsers
- Implement error boundaries
- Add loading states and progress indicators

**Deliverable**: Performant experience across devices

### Phase 6: Accessibility & Testing (Week 6)
**Goal**: Inclusive and reliable

- Implement reduced motion alternative
- Add comprehensive keyboard navigation
- Create screen reader announcements
- Ensure WCAG 2.1 AA compliance
- Write unit tests for components
- Write integration tests for navigation
- Perform visual regression testing
- Conduct performance testing
- User testing and feedback incorporation

**Deliverable**: Production-ready, accessible 3D experience



## File Structure

```
frontend/
├── src/
│   ├── 3d/                          # New 3D-specific code
│   │   ├── components/
│   │   │   ├── GalaxyScene.tsx      # Main scene container
│   │   │   ├── CelestialBody.tsx    # Planet component
│   │   │   ├── ProceduralStarField.tsx
│   │   │   ├── ParticleSystem.tsx
│   │   │   ├── ConnectionPath.tsx
│   │   │   ├── HighlightGeometry.tsx
│   │   │   └── LightingRig.tsx
│   │   │
│   │   ├── effects/
│   │   │   ├── MultiLayerRenderer.tsx
│   │   │   ├── BloomEffect.tsx
│   │   │   ├── CompositionShader.ts
│   │   │   ├── VignetteEffect.tsx
│   │   │   └── FilmGrainEffect.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useTravelController.ts
│   │   │   ├── useInteractionManager.ts
│   │   │   ├── usePerformanceMonitor.ts
│   │   │   ├── useAdaptiveQuality.ts
│   │   │   └── useGalaxyState.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── galaxyGeneration.ts  # Procedural algorithms
│   │   │   ├── cameraCalculations.ts
│   │   │   ├── coordinateUtils.ts
│   │   │   └── performanceUtils.ts
│   │   │
│   │   ├── config/
│   │   │   ├── celestialBodies.ts   # Body configurations
│   │   │   ├── galaxyConfig.ts      # Star field config
│   │   │   ├── renderConfig.ts      # Rendering settings
│   │   │   ├── colorPalette.ts      # Color definitions
│   │   │   └── performancePresets.ts
│   │   │
│   │   ├── materials/
│   │   │   ├── PlanetMaterial.ts
│   │   │   ├── StarMaterial.ts
│   │   │   └── ParticleMaterial.ts
│   │   │
│   │   ├── store/
│   │   │   ├── navigationStore.ts   # Zustand store
│   │   │   └── performanceStore.ts
│   │   │
│   │   └── types/
│   │       ├── celestial.types.ts
│   │       ├── navigation.types.ts
│   │       └── performance.types.ts
│   │
│   ├── overlays/                    # UI overlay components
│   │   ├── SectionOverlay.tsx
│   │   ├── FileUploadOverlay.tsx
│   │   ├── HistoryBrowserOverlay.tsx
│   │   ├── InfoOverlay.tsx
│   │   ├── NavigationHUD.tsx
│   │   └── FallbackUI.tsx
│   │
│   ├── services/                    # Preserved from old frontend
│   │   ├── api.ts
│   │   └── ...
│   │
│   ├── types/                       # Preserved from old frontend
│   │   ├── index.ts
│   │   └── ...
│   │
│   ├── hooks/                       # Preserved hooks (non-3D)
│   │   ├── useTrainingProgress.ts
│   │   └── ...
│   │
│   ├── assets/
│   │   ├── textures/
│   │   │   ├── star-sprite.png
│   │   │   ├── particle-glow.png
│   │   │   └── planet-textures/
│   │   └── fonts/
│   │
│   ├── App.tsx                      # Updated root component
│   ├── main.tsx
│   └── index.html
│
├── public/
│   └── assets/
│
└── package.json                     # Updated dependencies
```

## Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.88.0",
    "@react-three/postprocessing": "^2.15.0",
    "three": "^0.158.0",
    
    "@tweenjs/tween.js": "^21.0.0",
    "zustand": "^4.4.0",
    
    "postprocessing": "^6.33.0",
    "detect-gpu": "^5.0.0"
  },
  "devDependencies": {
    "@types/three": "^0.158.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

## Migration Strategy

### Step 1: Backup Current Frontend
```bash
# Create backup branch
git checkout -b backup/old-frontend
git push origin backup/old-frontend

# Return to main development
git checkout main
```

### Step 2: Remove Old Components
```bash
# Delete old UI components
rm -rf frontend/src/pages
rm -rf frontend/src/components
rm frontend/src/theme/theme.ts
```

### Step 3: Preserve Reusable Code
```bash
# Keep these directories
# - frontend/src/services
# - frontend/src/types
# - frontend/src/hooks
# - .kiro/specs/frontend-ui (as reference)
```

### Step 4: Install New Dependencies
```bash
cd frontend
npm install @react-three/fiber @react-three/drei @react-three/postprocessing
npm install three @types/three
npm install @tweenjs/tween.js zustand
npm install postprocessing detect-gpu
```

### Step 5: Create New Structure
```bash
mkdir -p src/3d/{components,effects,hooks,utils,config,materials,store,types}
mkdir -p src/overlays
mkdir -p src/assets/textures
```

### Step 6: Implement Phase by Phase
Follow the implementation phases outlined above, testing thoroughly at each stage.

## Conclusion

This design provides a comprehensive blueprint for creating a cinematic 3D galaxy homepage that combines the best of Galaxy1's navigation architecture with Galaxy2's visual rendering quality. The system is designed to be performant, accessible, and maintainable while delivering a premium, immersive user experience that meaningfully connects the visual metaphor of space exploration to the AI/ML platform's purpose.

The modular architecture allows for incremental development and testing, while the adaptive quality system ensures the experience works across a wide range of devices. The design prioritizes both aesthetic excellence and functional reliability, creating a unique and memorable interface that sets the Agentic ML platform apart.

