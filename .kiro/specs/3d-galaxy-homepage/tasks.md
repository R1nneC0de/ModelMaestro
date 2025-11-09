# Implementation Plan

## Overview

This implementation plan breaks down the 3D Galaxy Homepage into discrete, actionable coding tasks. Each task builds incrementally on previous work, following the 6-phase approach outlined in the design document. Tasks are organized to deliver working functionality at each milestone while maintaining code quality and testability.

## Design Update (Latest)

**Key Changes from Original Design:**
1. **Background**: Pure black (#000000) instead of dark blue
2. **Galaxy**: Animated spiral galaxy with color gradients (warm orange/pink center → cool purple/blue edges)
3. **Navigation Elements**: Transparent circles with icons and text labels (instead of 3D planet spheres)
4. **Visual Style**: Inspired by modern space visualization (similar to Blueyard example)
5. **Particle Count**: Increased to 15000-20000 for denser, more dramatic galaxy effect

**Updated Components:**
- `NavigationNode.tsx` (replaces `CelestialBody.tsx`) - Transparent circles with icons
- `ProceduralStarField.tsx` - Enhanced with animation and color gradients
- `navigationNodes.ts` (replaces `celestialBodies.ts`) - Updated configuration
- `colorPalette.ts` - Black background and new color scheme

**Tasks marked with "UPDATE" or "NEW" reflect these design changes.**

## Task List

- [x] 1. Project setup and environment configuration
  - Create new 3D directory structure in frontend/src/3d
  - Install required dependencies (@react-three/fiber, @react-three/drei, @react-three/postprocessing, three, @tweenjs/tween.js, zustand)
  - Configure TypeScript for Three.js types
  - Set up Vite configuration for 3D asset loading
  - Create backup of current frontend components
  - _Requirements: 13.1, 13.2, 19.1, 19.2, 19.8_

- [x] 2. Remove old frontend components
  - Delete frontend/src/pages directory
  - Delete frontend/src/components directory
  - Delete frontend/src/theme/theme.ts
  - Preserve frontend/src/services, frontend/src/types, and frontend/src/hooks
  - Update App.tsx to remove old routing
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.7_

- [x] 3. Create core configuration files
  - [x] 3.1 Create celestialBodies.ts with configuration for 3 planets (Create Model, Past Models, Info)
    - **UPDATE: Rename to navigationNodes.ts for new design**
    - Define positions, scales, colors, glow colors for each node
    - Configure orbital properties (radius, speed, axis)
    - Set camera positioning parameters
    - Add icon type/path for each node
    - Add text labels for each node
    - _Requirements: 6.1, 6.2, 6.3, 6.5, 10.2_
  
  - [x] 3.5 Update navigationNodes.ts configuration (NEW)
    - Rename from celestialBodies.ts
    - Update config structure for navigation nodes
    - Add iconType field (e.g., 'upload', 'history', 'info')
    - Add label field (e.g., 'CREATE MODEL', 'PAST MODELS', 'INFORMATION')
    - Add subtitle field (e.g., 'PROGRAMMABLE', 'SCENIUS', 'ABOUT')
    - Update colors for circle borders (cyan, purple, amber)
    - Remove planet-specific properties (scale, emissive, etc.)
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 3.2 Create galaxyConfig.ts with star field generation parameters
    - Define star counts, distribution parameters
    - Configure core, outer core, and spiral arm settings
    - Set galaxy thickness and haze ratio
    - _Requirements: 17.1, 17.2_
  
  - [x] 3.3 Create renderConfig.ts with rendering pipeline settings
    - Define layer constants (BASE_LAYER, BLOOM_LAYER, OVERLAY_LAYER)
    - Configure bloom parameters (strength, threshold, radius)
    - Set star size ranges and haze opacity
    - _Requirements: 4.1, 18.1, 18.2_
  
  - [x] 3.4 Create colorPalette.ts with all color definitions
    - Define background colors, celestial body colors
    - Set glow colors and accent colors
    - Configure color temperatures for each planet type
    - _Requirements: 10.1, 10.2, 10.4_
  
  - [x] 3.6 Update colorPalette.ts for new design (NEW)
    - **UPDATE: Change background to pure black (#000000)**
    - Add galaxy gradient colors (warm center #ffa575 → cool edges #311599)
    - Update node colors (cyan, purple, amber for circles)
    - Add text colors (white, light gray)
    - Add hover state colors
    - _Requirements: 10.1, 10.2, 10.4_

- [x] 4. Implement basic 3D scene foundation
  - [x] 4.1 Create GalaxyScene.tsx component
    - Set up R3F Canvas with camera and scene configuration
    - Configure camera position [0, 500, 500], FOV 60, near/far planes
    - **UPDATE: Set background to pure black (#000000) instead of dark blue**
    - Add scene fog (FogExp2) for atmospheric depth
    - Implement window resize handling
    - _Requirements: 1.1, 1.2, 10.3_
  
  - [x] 4.2 Create LightingRig.tsx component
    - Implement three-point lighting (key, fill, rim lights)
    - Add ambient light with low intensity
    - Configure light positions and intensities per design
    - _Requirements: 10.3_
  
  - [x] 4.3 Create basic CelestialBody.tsx component
    - **DEPRECATED: Will be replaced with NavigationNode component (see Task 4.4)**
    - ~~Render sphere geometry with MeshStandardMaterial~~
    - ~~Apply color and emissive properties from config~~
    - ~~Position bodies according to celestialBodies config~~
    - ~~Add basic orbital animation~~
    - _Requirements: 1.2, 6.1, 6.2, 6.3_
  
  - [ ] 4.4 Create NavigationNode.tsx component (NEW - replaces planets)
    - Render transparent circle using ring geometry (thin outline)
    - Add icon in center (SVG texture or simple geometry)
    - Add HTML text label above circle using drei's Html component
    - Position nodes in spiral arms of galaxy
    - Add subtle glow effect to circle border
    - Support hover state (brighten circle)
    - _Requirements: 1.2, 6.1, 6.2, 6.3_

- [x] 5. Implement procedural star field generation
  - [x] 5.1 Create galaxyGeneration.ts utility functions
    - Implement gaussianRandom function for distribution
    - Implement spiral function for arm generation
    - Create star position generation algorithm (core, outer core, arms)
    - _Requirements: 17.1, 17.2_
  
  - [x] 5.2 Create ProceduralStarField.tsx component
    - Generate 7000 star positions using galaxy generation algorithm
    - Create sprite-based stars with textures
    - Assign stars to BLOOM_LAYER for selective bloom
    - Implement distance-based star scaling
    - _Requirements: 1.3, 17.1, 17.2, 17.4, 17.5_
  
  - [x] 5.3 Add haze particle system to star field
    - Generate haze particles at 50% of star count
    - Use larger, more transparent sprites for haze
    - Distribute haze using same generation algorithm
    - _Requirements: 17.1_
  
  - [x] 5.4 Add animated spiral rotation to star field (NEW ENHANCEMENT)
    - Add time-based rotation to spiral arms
    - Animate star positions using sine/cosine functions
    - Implement color gradients (warm center → cool edges)
    - Use colors: orange/pink (#ffa575) center → purple/blue (#311599) edges
    - Increase particle count to 15000-20000 for denser look
    - Add subtle pulsing/twinkling effect to stars
    - _Requirements: 17.1, 17.2, 17.3_

- [x] 6. Implement interaction and raycasting system
  - [x] 6.1 Create useInteractionManager.ts hook
    - Set up Three.js Raycaster for mouse/touch input
    - Detect intersections with navigation nodes (updated from celestial bodies)
    - Emit hover events with debouncing (100ms threshold)
    - Emit click events for node selection
    - Handle interaction enabled/disabled state
    - _Requirements: 2.1, 2.2, 2.3, 3.5, 15.4_
  
  - [x] 6.2 Add hover effects to CelestialBody component
    - **UPDATE: Apply to NavigationNode component instead**
    - Create HighlightGeometry.tsx for hover visualization
    - Show highlight on hover with pulsing animation
    - Brighten circle border on hover
    - Change cursor to pointer on hover
    - _Requirements: 2.1, 2.2, 16.1_
  
  - [x] 6.3 Update hover effects for NavigationNode (NEW)
    - Brighten circle border glow on hover
    - Scale up icon slightly (1.1x)
    - Add subtle pulsing animation to circle
    - Fade in additional info text on hover
    - _Requirements: 2.1, 2.2, 16.1_

- [x] 7. Implement camera navigation system
  - [x] 7.1 Create navigationStore.ts with Zustand
    - Define navigation state (currentView, focusedBodyId, isTransitioning)
    - Create actions for travelTo, returnToOverview
    - Track transition phase and progress
    - Store camera position and target state
    - _Requirements: 3.5, 15.4_
  
  - [x] 7.2 Create cameraCalculations.ts utility
    - Implement calculateDestinationCoordinates function
    - Calculate camera offset based on body size and quadrant
    - Determine Z offset based on body type
    - _Requirements: 15.3_
  
  - [x] 7.3 Create useTravelController.ts hook
    - Implement two-phase camera animation (takeoff + approach)
    - Use TWEEN.js with Cubic.InOut easing
    - Phase 1: Takeoff (3 seconds) - rise vertically while tracking target
    - Phase 2: Approach (5 seconds) - fly to calculated destination
    - Update camera lookAt and orbit controls target during animation
    - Dispatch travel start and complete events
    - Prevent navigation during transitions
    - _Requirements: 2.3, 3.1, 3.2, 3.3, 3.4, 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [x] 7.4 Implement returnToOverview functionality
    - Animate camera back to overview position [0, 500, 500]
    - Duration 4 seconds with Cubic.InOut easing
    - Reset camera target to [0, 0, 0]
    - Clear focused body state
    - _Requirements: 3.5_

- [x] 8. Add dynamic highlight effects during navigation
  - [x] 8.1 Implement distance-based highlight scaling
    - Calculate distance from camera to target during approach
    - Scale highlight to 1.1% of distance value
    - Update highlight size in real-time during camera flight
    - _Requirements: 16.2, 16.3_
  
  - [x] 8.2 Implement highlight color transition on arrival
    - Fade highlight from initial glow color to cyan (RGB 59, 234, 247)
    - Transition duration 3 seconds
    - Remove highlight geometry after fade completes
    - _Requirements: 16.4, 16.5_
  
  - [x] 8.3 Add body scale animation on focus
    - Scale up focused body by 10-20% when camera arrives
    - Smooth animation over 1 second
    - Scale back down when returning to overview
    - _Requirements: 6.4_

- [x] 9. Implement multi-layer rendering pipeline
  - [x] 9.1 Create CompositionShader.ts
    - Write vertex shader for UV mapping
    - Write fragment shader to blend base, bloom, and overlay textures
    - Use additive blending for bloom layer
    - Use alpha blending for overlay layer
    - _Requirements: 18.5_
  
  - [x] 9.2 Create MultiLayerRenderer.tsx component
    - Set up EffectComposer with three render passes
    - Configure bloom composer for BLOOM_LAYER (renderToScreen: false)
    - Configure overlay composer for OVERLAY_LAYER (renderToScreen: false)
    - Configure base composer with CompositionShader for final output
    - Implement renderPipeline function to render all three passes
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_
  
  - [x] 9.3 Create BloomEffect.tsx component
    - Configure UnrealBloomPass with design parameters
    - Set strength: 1.5, threshold: 0.4, radius: 0
    - Apply bloom only to objects on BLOOM_LAYER
    - _Requirements: 4.1, 18.2_
  
  - [x] 9.4 Update CelestialBody and ProceduralStarField to use layers
    - Assign celestial body glows to BLOOM_LAYER
    - Assign all stars to BLOOM_LAYER
    - Assign base geometry to BASE_LAYER
    - _Requirements: 17.4, 18.2_

- [x] 10. Create particle systems for navigation nodes (UPDATED)
  - [x] 10.1 Create ParticleSystem.tsx base component
    - **UPDATE: Simplified for navigation nodes**
    - Implement Points geometry with custom material
    - Support orbital distribution around nodes
    - Implement subtle particle animation (orbit, pulse)
    - Assign particles to BLOOM_LAYER
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 10.2 Add subtle particles to Create Model node (OPTIONAL)
    - 100-200 small particles orbiting the circle
    - Colors: purple, blue gradient
    - Slow orbit behavior
    - _Requirements: 6.1_
  
  - [x] 10.3 Add subtle particles to Past Models node (OPTIONAL)
    - 100-200 small particles orbiting the circle
    - Amber/gold color
    - Slow orbit behavior
    - _Requirements: 6.2_
  
  - [x] 10.4 Add subtle particles to Info node (OPTIONAL)
    - 100-200 small particles orbiting the circle
    - Cyan color
    - Slow orbit behavior
    - _Requirements: 6.3_

- [x] 11. Implement UI overlay system
  - [x] 11.1 Create SectionOverlay.tsx component
    - Position overlay in screen space using HTML/CSS
    - Implement fade and slide entrance animation (500ms)
    - Implement fade exit animation (300ms)
    - Show/hide based on navigation state
    - Support different content for each section type
    - _Requirements: 2.4, 2.5_
  
  - [x] 11.2 Create FileUploadOverlay.tsx component
    - Reuse existing file validation logic from old FileUpload component
    - Implement CSV file upload with drag-and-drop
    - Show upload progress indicator
    - Display training configuration options
    - Integrate with backend API for file upload
    - _Requirements: 11.1, 11.5, 14.1_
  
  - [x] 11.3 Create HistoryBrowserOverlay.tsx component
    - Reuse existing history logic from old HistoryList component
    - Display scrollable list of training sessions
    - Show session cards with key metrics
    - Implement session detail view
    - Integrate with backend API for history data
    - _Requirements: 12.1, 12.2, 12.5, 14.3_
  
  - [x] 11.4 Create InfoOverlay.tsx component
    - Display platform information and documentation
    - Reuse content from old InfoPage component
    - Format content for overlay presentation
    - _Requirements: 14.4_
  
  - [x] 11.5 Create NavigationHUD.tsx component
    - Display current section name
    - Show navigation hints ("Click to explore", "ESC to return")
    - Display loading states during transitions
    - Show keyboard shortcuts
    - _Requirements: 1.4, 8.3_

- [x] 12. Add training visualization effects
  - [x] 12.1 Implement data upload particle animation
    - Animate particles flowing from upload area into Create Model planet
    - Trigger on successful file upload
    - Duration 2 seconds with smooth easing
    - _Requirements: 11.2_
  
  - [x] 12.2 Implement training progress visualization
    - Increase Create Model planet glow intensity during training
    - Add rapid particle movement around planet
    - Display progress percentage in overlay
    - Integrate with useTrainingProgress hook
    - _Requirements: 11.3, 14.2_
  
  - [x] 12.3 Implement training completion animation
    - Create ConnectionPath.tsx component for light streams
    - Animate connection forming from Create Model to Past Models
    - Transfer particles along connection path
    - Create new "moon" orbiting Past Models planet
    - _Requirements: 11.4, 12.3_

- [ ] 13. Implement keyboard navigation
  - [ ] 13.1 Add keyboard event listeners
    - Listen for Tab, Enter, Escape, Arrow keys, Space, 1-3 number keys
    - Implement focus cycling through celestial bodies with Tab
    - Implement selection with Enter key
    - Implement return to overview with Escape key
    - _Requirements: 8.2_
  
  - [ ] 13.2 Add visual focus indicators for keyboard navigation
    - Show focus ring around focused body
    - Update NavigationHUD to show focused body name
    - Ensure focus is visible and meets accessibility standards
    - _Requirements: 8.2, 8.4_

- [ ] 14. Implement performance monitoring and adaptive quality
  - [ ] 14.1 Create usePerformanceMonitor.ts hook
    - Track FPS and frame time
    - Calculate average FPS over 1-second intervals
    - Detect performance degradation (3 consecutive bad frames)
    - Emit performance events
    - _Requirements: 9.1, 9.5_
  
  - [ ] 14.2 Create performancePresets.ts configuration
    - Define HIGH, MEDIUM, LOW quality presets
    - Configure star counts, particle counts, effects for each level
    - Set texture sizes and postprocessing options
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ] 14.3 Create useAdaptiveQuality.ts hook
    - Detect optimal quality level on initial load (GPU, memory, mobile)
    - Monitor performance and adjust quality dynamically
    - Reduce quality when FPS drops below 30 for 3 seconds
    - Apply quality settings to scene components
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 9.1, 9.2_
  
  - [ ] 14.4 Implement quality-based feature toggling
    - Disable postprocessing effects in LOW mode
    - Reduce star and particle counts based on quality level
    - Adjust texture resolutions dynamically
    - Disable shadows in MEDIUM and LOW modes
    - _Requirements: 9.1, 9.2_

- [ ] 15. Add mobile optimizations and touch controls
  - [ ] 15.1 Implement touch interaction handling
    - Single touch for camera rotation
    - Pinch gesture for zoom
    - Double tap for body selection
    - Long press for info display
    - _Requirements: 5.4_
  
  - [ ] 15.2 Create mobile-specific quality preset
    - Reduce star count to 1500-2000
    - Disable all postprocessing except bloom
    - Use 512px textures
    - Reduce particle counts by 70%
    - Simplify materials to MeshBasicMaterial
    - _Requirements: 5.4_
  
  - [ ] 15.3 Implement responsive UI adjustments
    - Increase UI scale on mobile (1.2x)
    - Enlarge touch targets (1.5x)
    - Adjust camera FOV for mobile (70 degrees)
    - _Requirements: 5.4_

- [ ] 16. Implement error handling and fallback UI
  - [ ] 16.1 Create WebGL support detection
    - Check for WebGL and WebGL2 support
    - Detect WebGL version and capabilities
    - Return appropriate error messages
    - _Requirements: 9.5_
  
  - [ ] 16.2 Create FallbackUI.tsx component
    - Display error message for unsupported browsers
    - Provide simple 2D navigation buttons as alternative
    - Link to Create Model, Past Models, and Info pages
    - Style consistently with platform branding
    - _Requirements: 5.3, 8.1_
  
  - [ ] 16.3 Create Galaxy3DErrorBoundary component
    - Catch and handle React errors in 3D components
    - Display FallbackUI on error
    - Log errors to console and error tracking service
    - _Requirements: 9.5_
  
  - [ ] 16.4 Add loading states and progress indicators
    - Show loading animation during initial scene load
    - Display progress bar for asset loading
    - Show transition states during camera flights
    - _Requirements: 1.5_

- [ ] 17. Implement accessibility features
  - [ ] 17.1 Create reduced motion alternative
    - Detect prefers-reduced-motion media query
    - Provide simplified 2D navigation when enabled
    - Disable all animations and transitions
    - Maintain full functionality without motion
    - _Requirements: 8.1_
  
  - [ ] 17.2 Add screen reader support
    - Implement ARIA labels for all interactive elements
    - Add live region announcements for navigation state changes
    - Provide text alternatives for visual information
    - Announce section changes and loading states
    - _Requirements: 8.3_
  
  - [ ] 17.3 Ensure WCAG 2.1 AA compliance
    - Verify contrast ratios for all UI text (minimum 4.5:1)
    - Ensure all interactive elements are keyboard accessible
    - Provide focus indicators for all focusable elements
    - Test with screen readers (NVDA, JAWS, VoiceOver)
    - _Requirements: 8.4_
  
  - [ ] 17.4 Add "Skip to Navigation" button
    - Provide quick access to 2D navigation for users who prefer it
    - Position button prominently at top of page
    - Ensure button is keyboard accessible
    - _Requirements: 8.5_

- [ ] 18. Optimize performance and asset loading
  - [ ] 18.1 Implement geometry instancing for stars
    - Use InstancedMesh for star sprites
    - Set individual transforms with matrices
    - Reduce draw calls significantly
    - _Requirements: 9.2_
  
  - [ ] 18.2 Implement lazy loading for textures
    - Load low-res textures initially
    - Load high-res textures after scene is interactive
    - Use progressive loading for large assets
    - _Requirements: 9.1_
  
  - [ ] 18.3 Add frustum culling optimization
    - Ensure all objects have proper bounding spheres
    - Let Three.js automatically cull off-screen objects
    - _Requirements: 9.3_
  
  - [ ] 18.4 Compress and optimize 3D assets
    - Compress textures to appropriate formats (PNG, JPG, Basis)
    - Generate mipmaps for all textures
    - Optimize geometry vertex counts
    - Ensure total scene size is under 5MB
    - _Requirements: 9.4_

- [ ] 19. Integration and final polish
  - [ ] 19.1 Integrate with existing backend APIs
    - Connect FileUploadOverlay to data upload endpoint
    - Connect HistoryBrowserOverlay to training history endpoint
    - Integrate training progress updates
    - Handle API errors gracefully
    - _Requirements: 11.5, 12.5, 13.3, 13.4, 13.5, 14.5_
  
  - [ ] 19.2 Add connection paths between celestial bodies
    - Create ConnectionPath.tsx component
    - Render light streams between Create Model and Past Models
    - Animate particles traveling along paths
    - Show connections when relevant (e.g., after training)
    - _Requirements: 7.1, 7.5_
  
  - [ ] 19.3 Implement ambient data particle system
    - Create 2000 ambient particles distributed spherically
    - Animate particles with slow random movement
    - Use cyan color with low opacity
    - Add to scene background
    - _Requirements: 7.4_
  
  - [ ] 19.4 Add subtle camera drift in overview state
    - Implement gentle camera position oscillation
    - Very slow movement (0.1 units per second)
    - Create sense of floating in space
    - Disable during user interaction
    - _Requirements: 1.3_
  
  - [ ] 19.5 Polish visual details
    - Fine-tune lighting intensities and positions
    - Adjust bloom strength and threshold for optimal glow
    - Refine particle system parameters
    - Optimize color palette for visual harmony
    - Add subtle vignette and film grain effects
    - _Requirements: 4.3, 4.4, 4.5, 4.6, 10.3, 10.4, 10.5_

- [ ] 20. Testing and quality assurance
  - [ ] 20.1 Write unit tests for utility functions
    - Test galaxyGeneration.ts functions
    - Test cameraCalculations.ts functions
    - Test coordinate utilities
    - _Requirements: All_
  
  - [ ] 20.2 Write component tests
    - Test CelestialBody rendering and interactions
    - Test ProceduralStarField generation
    - Test overlay components
    - _Requirements: All_
  
  - [ ] 20.3 Write integration tests for navigation flow
    - Test complete navigation cycle (overview → focused → overview)
    - Test keyboard navigation
    - Test touch interactions on mobile
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ] 20.4 Perform visual regression testing
    - Capture snapshots of overview state
    - Capture snapshots of focused states
    - Compare against baseline images
    - _Requirements: All visual requirements_
  
  - [ ] 20.5 Conduct performance testing
    - Measure FPS in overview state (target: 60 FPS)
    - Measure FPS during transitions (target: 30+ FPS)
    - Test on various devices and browsers
    - Verify adaptive quality system works correctly
    - _Requirements: 3.2, 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ] 20.6 Conduct accessibility testing
    - Test with keyboard navigation only
    - Test with screen readers (NVDA, JAWS, VoiceOver)
    - Verify WCAG 2.1 AA compliance
    - Test reduced motion mode
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 20.7 User acceptance testing
    - Conduct user testing sessions
    - Gather feedback on navigation intuitiveness
    - Assess visual quality and performance
    - Identify usability issues
    - _Requirements: All_

