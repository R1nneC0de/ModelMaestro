import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { LAYERS } from '../../config/renderConfig';

/**
 * ModelMoon Component
 * 
 * Represents a completed training session as a small orbiting "moon"
 * around the Past Models node
 * 
 * Requirements: 11.4, 12.3
 */

export interface ModelMoonProps {
  parentPosition: THREE.Vector3;
  orbitRadius: number;
  orbitSpeed?: number;
  size?: number;
  color?: string;
  index?: number;  // For multiple moons with different orbit phases
}

export function ModelMoon({
  parentPosition,
  orbitRadius,
  orbitSpeed = 0.0003,
  size = 3,
  color = '#FFB84D',
  index = 0,
}: ModelMoonProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const timeRef = useRef(0);
  
  // Initial angle offset based on index
  const initialAngle = (index * Math.PI * 2) / 3; // Distribute evenly if multiple moons
  
  useFrame((_state, delta) => {
    timeRef.current += delta;
    
    // Calculate orbital position
    const angle = initialAngle + timeRef.current * orbitSpeed;
    const x = parentPosition.x + Math.cos(angle) * orbitRadius;
    const y = parentPosition.y + Math.sin(angle) * orbitRadius;
    const z = parentPosition.z + Math.sin(timeRef.current * 0.5) * 5; // Slight vertical oscillation
    
    // Update mesh position
    if (meshRef.current) {
      meshRef.current.position.set(x, y, z);
    }
    
    // Update glow position
    if (glowRef.current) {
      glowRef.current.position.set(x, y, z);
    }
    
    // Gentle rotation
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.5;
      meshRef.current.rotation.z += delta * 0.3;
    }
  });
  
  return (
    <group>
      {/* Main moon sphere */}
      <mesh ref={meshRef} layers={LAYERS.BASE}>
        <sphereGeometry args={[size, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.8}
        />
      </mesh>
      
      {/* Glow effect */}
      <mesh ref={glowRef} layers={LAYERS.BLOOM}>
        <sphereGeometry args={[size * 1.2, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.3}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}
