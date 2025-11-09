import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { LAYERS } from '../../config/renderConfig';

/**
 * TrainingProgressEffect Component
 * 
 * Visualizes training progress on the Create Model node:
 * - Increases node glow intensity during training
 * - Adds rapid particle movement around node
 * - Integrates with useTrainingProgress hook
 * 
 * Requirements: 11.3, 14.2
 */

export interface TrainingProgressEffectProps {
  nodePosition: THREE.Vector3;
  nodeRadius: number;
  progress: number;  // 0 to 1
  isActive: boolean;
}

export function TrainingProgressEffect({
  nodePosition,
  nodeRadius,
  progress,
  isActive,
}: TrainingProgressEffectProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const glowRingRef = useRef<THREE.Mesh>(null);
  const timeRef = useRef(0);
  
  const particleCount = 200;
  
  // Generate particle positions in orbital pattern
  const { positions, velocities } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount);
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      const angle = (i / particleCount) * Math.PI * 2;
      const radius = nodeRadius * 1.5; // Orbit outside the node
      const heightVariation = (Math.random() - 0.5) * nodeRadius * 0.5;
      
      positions[i3] = nodePosition.x + Math.cos(angle) * radius;
      positions[i3 + 1] = nodePosition.y + Math.sin(angle) * radius;
      positions[i3 + 2] = nodePosition.z + heightVariation;
      
      // Store initial angle as velocity for rotation
      velocities[i] = angle;
    }
    
    return { positions, velocities };
  }, [nodePosition, nodeRadius, particleCount]);
  
  // Generate colors (purple to cyan gradient)
  const colors = useMemo(() => {
    const colors = new Float32Array(particleCount * 3);
    const startColor = new THREE.Color('#B24BF3'); // Purple
    const endColor = new THREE.Color('#00D9FF');   // Cyan
    
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
    if (!isActive || !pointsRef.current) return;
    
    timeRef.current += delta;
    
    // Rapid particle movement - speed increases with progress
    const baseSpeed = 2.0;
    const progressSpeed = progress * 3.0; // Up to 3x faster at 100%
    const rotationSpeed = (baseSpeed + progressSpeed) * delta;
    
    const positionAttribute = pointsRef.current.geometry.attributes.position;
    const positions = positionAttribute.array as Float32Array;
    
    // Rotate particles around the node
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      const angle = velocities[i] + timeRef.current * rotationSpeed;
      const radius = nodeRadius * 1.5;
      const heightVariation = Math.sin(timeRef.current + i * 0.1) * nodeRadius * 0.3;
      
      positions[i3] = nodePosition.x + Math.cos(angle) * radius;
      positions[i3 + 1] = nodePosition.y + Math.sin(angle) * radius;
      positions[i3 + 2] = nodePosition.z + heightVariation;
    }
    
    positionAttribute.needsUpdate = true;
    
    // Pulsing glow ring intensity based on progress
    if (glowRingRef.current && glowRingRef.current.material instanceof THREE.MeshBasicMaterial) {
      const pulse = Math.sin(timeRef.current * 4) * 0.5 + 0.5; // 0 to 1
      const baseOpacity = 0.3 + (progress * 0.4); // 0.3 to 0.7 based on progress
      const pulsedOpacity = baseOpacity + (pulse * 0.2);
      glowRingRef.current.material.opacity = pulsedOpacity;
    }
  });
  
  if (!isActive) return null;
  
  return (
    <group>
      {/* Rapid moving particles */}
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
          size={1.5}
          vertexColors
          transparent
          opacity={0.8}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          sizeAttenuation={true}
        />
      </points>
      
      {/* Enhanced glow ring */}
      <mesh
        ref={glowRingRef}
        position={nodePosition}
        rotation={[Math.PI / 2, 0, 0]}
        layers={LAYERS.BLOOM}
      >
        <ringGeometry args={[
          nodeRadius * 1.4,
          nodeRadius * 1.6,
          64
        ]} />
        <meshBasicMaterial
          color="#00D9FF"
          transparent
          opacity={0.5}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}
