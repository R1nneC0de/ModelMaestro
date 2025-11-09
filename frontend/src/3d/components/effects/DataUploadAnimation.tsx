import { useRef, useMemo, useEffect, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { LAYERS } from '../../config/renderConfig';

/**
 * DataUploadAnimation Component
 * 
 * Animates particles flowing from upload area into Create Model node
 * Triggered on successful file upload
 * Duration: 2 seconds with smooth easing
 * 
 * Requirements: 11.2
 */

export interface DataUploadAnimationProps {
  startPosition: THREE.Vector3;  // Upload area position (screen space converted to 3D)
  endPosition: THREE.Vector3;    // Create Model node position
  onComplete?: () => void;       // Callback when animation completes
  particleCount?: number;        // Number of particles (default: 50)
}

export function DataUploadAnimation({
  startPosition,
  endPosition,
  onComplete,
  particleCount = 50,
}: DataUploadAnimationProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const [isAnimating, setIsAnimating] = useState(true);
  const progressRef = useRef(0);
  const duration = 2.0; // 2 seconds
  
  // Generate particle positions and velocities
  const { positions, velocities, delays } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);
    const delays = new Float32Array(particleCount);
    
    // Calculate direction vector
    const direction = new THREE.Vector3()
      .subVectors(endPosition, startPosition)
      .normalize();
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      
      // Start all particles at the upload position with slight random spread
      const spread = 10;
      positions[i3] = startPosition.x + (Math.random() - 0.5) * spread;
      positions[i3 + 1] = startPosition.y + (Math.random() - 0.5) * spread;
      positions[i3 + 2] = startPosition.z + (Math.random() - 0.5) * spread;
      
      // Calculate velocity towards end position with slight variation
      const speedVariation = 0.8 + Math.random() * 0.4; // 0.8 to 1.2
      velocities[i3] = direction.x * speedVariation;
      velocities[i3 + 1] = direction.y * speedVariation;
      velocities[i3 + 2] = direction.z * speedVariation;
      
      // Stagger particle start times
      delays[i] = (i / particleCount) * 0.3; // 0 to 0.3 seconds delay
    }
    
    return { positions, velocities, delays };
  }, [startPosition, endPosition, particleCount]);
  
  // Generate colors (gradient from cyan to purple)
  const colors = useMemo(() => {
    const colors = new Float32Array(particleCount * 3);
    const startColor = new THREE.Color('#00D9FF'); // Cyan
    const endColor = new THREE.Color('#B24BF3');   // Purple
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      const t = i / particleCount;
      const color = new THREE.Color().lerpColors(startColor, endColor, t);
      
      colors[i3] = color.r;
      colors[i3 + 1] = color.g;
      colors[i3 + 2] = color.b;
    }
    
    return colors;
  }, [particleCount]);
  
  // Animation loop
  useFrame((_state, delta) => {
    if (!isAnimating || !pointsRef.current) return;
    
    progressRef.current += delta;
    const progress = Math.min(progressRef.current / duration, 1.0);
    
    // Smooth easing (ease-in-out cubic)
    const eased = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;
    
    const positionAttribute = pointsRef.current.geometry.attributes.position;
    const positions = positionAttribute.array as Float32Array;
    
    // Update particle positions
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      const delay = delays[i];
      
      // Calculate particle-specific progress with delay
      const particleProgress = Math.max(0, Math.min(1, (progressRef.current - delay) / duration));
      
      if (particleProgress > 0) {
        // Apply easing to particle progress
        const particleEased = particleProgress < 0.5
          ? 4 * particleProgress * particleProgress * particleProgress
          : 1 - Math.pow(-2 * particleProgress + 2, 3) / 2;
        
        // Interpolate from start to end position
        positions[i3] = startPosition.x + (endPosition.x - startPosition.x) * particleEased;
        positions[i3 + 1] = startPosition.y + (endPosition.y - startPosition.y) * particleEased;
        positions[i3 + 2] = startPosition.z + (endPosition.z - startPosition.z) * particleEased;
        
        // Add slight wave motion for visual interest
        const wave = Math.sin(particleProgress * Math.PI * 2) * 5;
        positions[i3 + 1] += wave;
      }
    }
    
    positionAttribute.needsUpdate = true;
    
    // Update material opacity (fade out near the end)
    if (pointsRef.current.material instanceof THREE.PointsMaterial) {
      const fadeStart = 0.8;
      if (progress > fadeStart) {
        const fadeProgress = (progress - fadeStart) / (1.0 - fadeStart);
        pointsRef.current.material.opacity = 1.0 - fadeProgress;
      }
    }
    
    // Complete animation
    if (progress >= 1.0) {
      setIsAnimating(false);
      if (onComplete) {
        onComplete();
      }
    }
  });
  
  if (!isAnimating && progressRef.current >= duration) {
    return null; // Remove from scene after animation completes
  }
  
  return (
    <points ref={pointsRef} layers={LAYERS.BLOOM}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={2.0}
        vertexColors
        transparent
        opacity={1.0}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        sizeAttenuation={true}
      />
    </points>
  );
}
