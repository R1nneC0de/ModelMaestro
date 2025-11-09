# 3D Galaxy Homepage: Implementation Plan

## Quick Start Implementation Guide

This document provides a practical, step-by-step implementation plan for the 3D galaxy homepage.

---

## Phase 1: Setup & Foundation

### 1.1 Install Dependencies

```bash
cd frontend
npm install three @react-three/fiber @react-three/drei
npm install @react-spring/three gsap
npm install zustand
```

### 1.2 Create Base Scene Component

**File:** `frontend/src/components/galaxy/GalaxyScene.tsx`

```typescript
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars } from '@react-three/drei';
import { Suspense } from 'react';
import { GalaxyContent } from './GalaxyContent';
import { PostProcessing } from './PostProcessing';

export function GalaxyScene() {
  return (
    <Canvas
      gl={{ antialias: true, alpha: false }}
      dpr={[1, 2]} // Adaptive pixel ratio
      style={{ position: 'fixed', inset: 0, zIndex: 0 }}
    >
      <Suspense fallback={null}>
        <PerspectiveCamera makeDefault position={[0, 0, 15]} fov={50} />
        <ambientLight intensity={0.3} />
        <GalaxyContent />
        <PostProcessing />
      </Suspense>
    </Canvas>
  );
}
```

### 1.3 Create Planet Component

**File:** `frontend/src/components/galaxy/Planet.tsx`

```typescript
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh, MeshStandardMaterial } from 'three';
import { Text } from '@react-three/drei';

interface PlanetProps {
  position: [number, number, number];
  radius: number;
  color: string;
  label: string;
  description?: string;
  onClick?: () => void;
  isFocused?: boolean;
}

export function Planet({
  position,
  radius,
  color,
  label,
  description,
  onClick,
  isFocused = false,
}: PlanetProps) {
  const meshRef = useRef<Mesh>(null);
  const materialRef = useRef<MeshStandardMaterial>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={(e) => {
          e.stopPropagation();
          // Scale up on hover
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          // Scale back
        }}
      >
        <sphereGeometry args={[radius, 32, 32]} />
        <meshStandardMaterial
          ref={materialRef}
          color={color}
          emissive={color}
          emissiveIntensity={isFocused ? 0.5 : 0.2}
        />
      </mesh>
      
      {/* Glow effect using point light */}
      <pointLight
        color={color}
        intensity={isFocused ? 2 : 1}
        distance={radius * 3}
      />
      
      {/* Label */}
      <Text
        position={[0, radius + 1, 0]}
        fontSize={0.5}
        color="#E6EDF3"
        anchorX="center"
        anchorY="middle"
        font="/fonts/PlusJakartaSans-Bold.woff"
      >
        {label}
      </Text>
    </group>
  );
}
```

---

## Phase 2: Camera System

### 2.1 Camera Controller

**File:** `frontend/src/components/galaxy/CameraController.tsx`

```typescript
import { useThree } from '@react-three/fiber';
import { useEffect } from 'react';
import { useGalaxyStore } from '../../stores/galaxyStore';
import { gsap } from 'gsap';

export function CameraController() {
  const { camera } = useThree();
  const { cameraState, isTransitioning } = useGalaxyStore();

  useEffect(() => {
    if (isTransitioning) return;

    const positions: Record<string, [number, number, number]> = {
      home: [0, 0, 15],
      'create-model': [-8, 2, 8],
      'past-models': [8, 2, 8],
      info: [0, -4, 10],
    };

    const targets: Record<string, [number, number, number]> = {
      home: [0, 0, 0],
      'create-model': [-8, 2, 0],
      'past-models': [8, 2, 0],
      info: [0, -4, 0],
    };

    const pos = positions[cameraState] || positions.home;
    const target = targets[cameraState] || targets.home;

    gsap.to(camera.position, {
      x: pos[0],
      y: pos[1],
      z: pos[2],
      duration: 2.5,
      ease: 'power2.inOut',
    });

    // Use lookAt or gsap for target
    gsap.to({}, {
      duration: 2.5,
      ease: 'power2.inOut',
      onUpdate: () => {
        camera.lookAt(target[0], target[1], target[2]);
      },
    });
  }, [cameraState, camera, isTransitioning]);

  return null;
}
```

### 2.2 Galaxy Store (State Management)

**File:** `frontend/src/stores/galaxyStore.ts`

```typescript
import { create } from 'zustand';

interface GalaxyState {
  cameraState: 'home' | 'create-model' | 'past-models' | 'info';
  hoveredPlanet: string | null;
  isTransitioning: boolean;
  setCameraState: (state: GalaxyState['cameraState']) => void;
  setHoveredPlanet: (planet: string | null) => void;
  setIsTransitioning: (transitioning: boolean) => void;
}

export const useGalaxyStore = create<GalaxyState>((set) => ({
  cameraState: 'home',
  hoveredPlanet: null,
  isTransitioning: false,
  setCameraState: (state) => {
    set({ cameraState: state, isTransitioning: true });
    setTimeout(() => set({ isTransitioning: false }), 2500);
  },
  setHoveredPlanet: (planet) => set({ hoveredPlanet: planet }),
  setIsTransitioning: (transitioning) => set({ isTransitioning }),
}));
```

---

## Phase 3: Scene Content

### 3.1 Starfield Component

**File:** `frontend/src/components/galaxy/Starfield.tsx`

```typescript
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Points, BufferGeometry, BufferAttribute } from 'three';

export function Starfield() {
  const pointsRef = useRef<Points>(null);
  const count = 300;
  const positions = new Float32Array(count * 3);

  // Generate random star positions
  for (let i = 0; i < count * 3; i++) {
    positions[i] = (Math.random() - 0.5) * 50;
  }

  useFrame((state) => {
    if (pointsRef.current) {
      // Subtle rotation
      pointsRef.current.rotation.y += 0.0001;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.5}
        color="#ffffff"
        sizeAttenuation={true}
        transparent
        opacity={0.6}
      />
    </points>
  );
}
```

### 3.2 Orbital Trails

**File:** `frontend/src/components/galaxy/OrbitalTrail.tsx`

```typescript
import { useMemo } from 'react';
import { CatmullRomCurve3, Vector3, BufferGeometry, BufferAttribute } from 'three';

interface OrbitalTrailProps {
  start: [number, number, number];
  end: [number, number, number];
  color: string;
  visible?: boolean;
}

export function OrbitalTrail({ start, end, color, visible = false }: OrbitalTrailProps) {
  const curve = useMemo(() => {
    const points = [
      new Vector3(...start),
      new Vector3((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 2, (start[2] + end[2]) / 2),
      new Vector3(...end),
    ];
    return new CatmullRomCurve3(points);
  }, [start, end]);

  const geometry = useMemo(() => {
    const points = curve.getPoints(50);
    const positions = new Float32Array(points.length * 3);
    points.forEach((point, i) => {
      positions[i * 3] = point.x;
      positions[i * 3 + 1] = point.y;
      positions[i * 3 + 2] = point.z;
    });
    const geo = new BufferGeometry();
    geo.setAttribute('position', new BufferAttribute(positions, 3));
    return geo;
  }, [curve]);

  return (
    <line geometry={geometry} visible={visible}>
      <lineBasicMaterial
        color={color}
        transparent
        opacity={visible ? 0.3 : 0}
        linewidth={2}
      />
    </line>
  );
}
```

---

## Phase 4: Post-Processing

### 4.1 Post-Processing Setup

**File:** `frontend/src/components/galaxy/PostProcessing.tsx`

```typescript
import { useThree } from '@react-three/fiber';
import { useEffect } from 'react';
import { EffectComposer, Bloom, DepthOfField, Vignette } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';

export function PostProcessing() {
  return (
    <EffectComposer>
      <Bloom
        intensity={0.8}
        luminanceThreshold={0.6}
        luminanceSmoothing={0.9}
        height={300}
      />
      <DepthOfField
        focusDistance={0.02}
        focalLength={0.02}
        bokehScale={2}
        height={480}
      />
      <Vignette
        eskil={false}
        offset={0.1}
        darkness={0.3}
      />
    </EffectComposer>
  );
}
```

---

## Phase 5: Integration with Existing App

### 5.1 Update HomePage

**File:** `frontend/src/pages/HomePage.tsx`

```typescript
import { GalaxyScene } from '../components/galaxy/GalaxyScene';
import { useGalaxyStore } from '../stores/galaxyStore';
import { useNavigate } from 'react-router-dom';

export function HomePage() {
  const navigate = useNavigate();
  const { setCameraState } = useGalaxyStore();

  // When camera state changes, navigate to appropriate route
  useEffect(() => {
    const unsubscribe = useGalaxyStore.subscribe(
      (state) => state.cameraState,
      (cameraState) => {
        if (cameraState === 'create-model') {
          // Show create model UI overlay
        } else if (cameraState === 'past-models') {
          navigate('/history');
        } else if (cameraState === 'info') {
          // Show info UI overlay
        }
      }
    );
    return unsubscribe;
  }, [navigate]);

  return (
    <>
      <GalaxyScene />
      <UIOverlay />
    </>
  );
}
```

### 5.2 UI Overlay Component

**File:** `frontend/src/components/galaxy/UIOverlay.tsx`

```typescript
import { useGalaxyStore } from '../../stores/galaxyStore';
import { Box, Typography, Button, Paper } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

export function UIOverlay() {
  const { cameraState } = useGalaxyStore();

  const overlayContent = {
    'create-model': {
      title: 'Create Model',
      description: 'Start a new training session',
      action: 'Begin Training',
    },
    'past-models': {
      title: 'Past Models',
      description: 'View your training history',
      action: 'View History',
    },
    info: {
      title: 'About',
      description: 'Learn about the platform',
      action: 'Learn More',
    },
  };

  const content = overlayContent[cameraState];

  if (!content || cameraState === 'home') return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'fixed',
          bottom: '10%',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10,
        }}
      >
        <Paper
          sx={{
            p: 4,
            borderRadius: 4,
            backgroundColor: 'rgba(17, 25, 40, 0.95)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(56, 189, 248, 0.2)',
            maxWidth: 500,
            textAlign: 'center',
          }}
        >
          <Typography variant="h2" sx={{ mb: 2, color: '#E6EDF3' }}>
            {content.title}
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, color: 'rgba(230, 237, 243, 0.7)' }}>
            {content.description}
          </Typography>
          <Button
            variant="contained"
            sx={{
              backgroundColor: '#0EA5E9',
              color: '#071018',
              '&:hover': {
                backgroundColor: '#0284C7',
                boxShadow: '0 0 12px rgba(14, 165, 233, 0.4)',
              },
            }}
          >
            {content.action}
          </Button>
        </Paper>
      </motion.div>
    </AnimatePresence>
  );
}
```

---

## Performance Optimization Checklist

- [ ] Implement LOD system for planets
- [ ] Use instanced rendering for particles
- [ ] Reduce particle count on mobile
- [ ] Lower post-processing resolution
- [ ] Implement frustum culling
- [ ] Add WebGL capability detection
- [ ] Create 2D fallback mode
- [ ] Optimize shader complexity
- [ ] Use texture compression
- [ ] Implement adaptive quality

---

## Accessibility Checklist

- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Screen reader labels
- [ ] ARIA announcements for state changes
- [ ] Respect `prefers-reduced-motion`
- [ ] High contrast mode support
- [ ] Focus indicators
- [ ] Alternative text for visual elements

---

## Next Steps

1. **Prototype:** Build minimal working version
2. **Test:** Performance on various devices
3. **Iterate:** Refine animations and transitions
4. **Polish:** Add post-processing effects
5. **Optimize:** Performance tuning
6. **Accessibility:** Add keyboard navigation
7. **Documentation:** User guide for navigation

---

*This implementation plan provides a practical roadmap for building the 3D galaxy homepage experience.*

