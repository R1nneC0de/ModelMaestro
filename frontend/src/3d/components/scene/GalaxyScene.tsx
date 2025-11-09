import React, { useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
// import { OrbitControls } from '@react-three/drei'; // Disabled for locked camera view
import { FogExp2 } from 'three';
import { DEFAULT_CAMERA_CONFIG, DEFAULT_SCENE_CONFIG } from '../../config/renderConfig';

/**
 * GalaxyScene Component
 * Main container for the entire 3D galaxy experience
 * 
 * Requirements:
 * - 1.1: Render complete 3D cosmic scene within 3 seconds
 * - 1.2: Display at least three distinct celestial bodies
 * - 10.3: Implement three-point lighting with proper configuration
 */

export interface GalaxySceneProps {
  onSceneReady?: () => void;
  performanceMode?: 'high' | 'medium' | 'low' | 'auto';
  children?: React.ReactNode;
}

/**
 * GalaxyScene - Main 3D scene container
 * 
 * Sets up R3F Canvas with:
 * - Camera configuration (position [0, 500, 500], FOV 60)
 * - Scene fog (FogExp2) for atmospheric depth
 * - Window resize handling (automatic via R3F)
 * - Background color
 */
export const GalaxyScene: React.FC<GalaxySceneProps> = ({
  onSceneReady,
  performanceMode = 'auto',
  children,
}) => {
  const sceneReadyRef = useRef(false);

  // Notify parent when scene is ready
  useEffect(() => {
    if (!sceneReadyRef.current && onSceneReady) {
      // Small delay to ensure scene is fully initialized
      const timer = setTimeout(() => {
        sceneReadyRef.current = true;
        onSceneReady();
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [onSceneReady]);

  return (
    <div style={{ width: '100%', height: '100vh', background: DEFAULT_SCENE_CONFIG.background }}>
      <Canvas
        camera={{
          position: DEFAULT_CAMERA_CONFIG.position,
          fov: DEFAULT_CAMERA_CONFIG.fov,
          near: DEFAULT_CAMERA_CONFIG.near,
          far: DEFAULT_CAMERA_CONFIG.far,
        }}
        gl={{
          antialias: performanceMode === 'high' || performanceMode === 'auto',
          alpha: false,
          powerPreference: 'high-performance',
        }}
        dpr={[1, 2]} // Device pixel ratio: min 1, max 2 for retina displays
        onCreated={({ scene, gl }) => {
          // Set scene background color
          scene.background = null; // Let CSS handle background for now
          
          // Add fog for atmospheric depth (Req 1.1, 10.3)
          if (DEFAULT_SCENE_CONFIG.fog) {
            scene.fog = new FogExp2(
              DEFAULT_SCENE_CONFIG.fog.color,
              DEFAULT_SCENE_CONFIG.fog.density
            );
          }
          
          // Configure renderer
          gl.setClearColor(DEFAULT_SCENE_CONFIG.background);
          
          // Enable shadow mapping if in high performance mode
          if (performanceMode === 'high') {
            gl.shadowMap.enabled = true;
          }
        }}
      >
        {/* Orbit controls disabled for locked top-down view */}
        {/* <OrbitControls 
          enableDamping
          dampingFactor={0.05}
          minDistance={100}
          maxDistance={2000}
        /> */}
        
        {/* Children components will be rendered here */}
        {/* This includes: LightingRig, CelestialBodies, StarField, etc. */}
        {children}
      </Canvas>
    </div>
  );
};

export default GalaxyScene;
