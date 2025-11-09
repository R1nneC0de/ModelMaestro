# Utility Functions

Utility functions for 3D calculations and algorithms.

## Files

### galaxyGeneration.ts
Procedural galaxy generation algorithms:
- gaussianRandom() - Gaussian distribution for star positions
- spiral() - Spiral arm generation
- generateStarPositions() - Complete star field generation
- Core, outer core, and spiral arm distribution

### cameraCalculations.ts
Camera positioning and movement calculations:
- calculateDestinationCoordinates() - Calculate camera target position
- getQuadrant() - Determine spatial quadrant
- applyQuadrantOffset() - Apply directional offset
- Camera offset based on body size and type

### coordinateUtils.ts
Coordinate transformation utilities:
- Screen space to world space conversion
- World space to screen space conversion
- Distance calculations
- Vector utilities

### performanceUtils.ts
Performance optimization utilities:
- Geometry instancing helpers
- Frustum culling utilities
- LOD (Level of Detail) calculations
- Memory management helpers
