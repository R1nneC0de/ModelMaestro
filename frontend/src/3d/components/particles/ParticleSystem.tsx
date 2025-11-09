import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { LAYERS } from '../../config/renderConfig';

/**
 * Particle distribution types
 */
export type ParticleDistribution = 'orbital' | 'spherical' | 'ring';

/**
 * Particle animation behavior
 */
export type ParticleAnimation = 'orbit' | 'pulse' | 'float' | 'none';

/**
 * Configuration for particle system
 */
export interface ParticleSystemConfig {
  // Particle count
  count: number;
  
  // Distribution
  distribution: ParticleDistribution;
  radius: number;              // Base radius for distribution
  
  // Visual properties
  size: number;                // Particle size
  color: string | string[];    // Single color or gradient colors
  opacity: number;             // Base opacity (0-1)
  
  // Animation
  animation: ParticleAnimation;
  speed: number;               // Animation speed multiplier
  
  // Position offset (for orbiting around a node)
  centerPosition?: THREE.Vector3;
}

/**
 * Props for ParticleSystem component
 */
export interface ParticleSystemProps extends ParticleSystemConfig {
  enabled?: boolean;           // Enable/disable rendering
}

/**
 * Base particle system component for navigation nodes
 * Implements Points geometry with custom material
 * Supports orbital distribution and subtle animations
 * Requirements: 6.1, 6.2, 6.3
 */
export function ParticleSystem({
  count,
  distribution,
  radius,
  size,
  color,
  opacity,
  animation,
  speed,
  centerPosition = new THREE.Vector3(0, 0, 0),
  enabled = true,
}: ParticleSystemProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const timeRef = useRef(0);
  
  // Generate particle positions based on distribution type
  const { positions, colors, initialAngles } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const initialAngles = new Float32Array(count);
    
    // Parse colors
    const colorArray = Array.isArray(color) ? color : [color];
    const threeColors = colorArray.map(c => new THREE.Color(c));
    
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      // Generate position based on distribution type
      let x = 0, y = 0, z = 0;
      
      switch (distribution) {
        case 'orbital': {
          // Distribute particles in a circular orbit around the center
          const angle = (i / count) * Math.PI * 2;
          const r = radius + (Math.random() - 0.5) * radius * 0.2; // Slight radius variation
          const heightVariation = (Math.random() - 0.5) * radius * 0.3; // Vertical spread
          
          x = Math.cos(angle) * r;
          y = Math.sin(angle) * r;
          z = heightVariation;
          
          initialAngles[i] = angle;
          break;
        }
        
        case 'spherical': {
          // Distribute particles in a sphere around the center
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.acos(2 * Math.random() - 1);
          const r = radius * (0.8 + Math.random() * 0.4); // Radius variation
          
          x = r * Math.sin(phi) * Math.cos(theta);
          y = r * Math.sin(phi) * Math.sin(theta);
          z = r * Math.cos(phi);
          
          initialAngles[i] = theta;
          break;
        }
        
        case 'ring': {
          // Distribute particles in a flat ring
          const angle = (i / count) * Math.PI * 2;
          const r = radius + (Math.random() - 0.5) * radius * 0.1; // Slight radius variation
          
          x = Math.cos(angle) * r;
          y = Math.sin(angle) * r;
          z = (Math.random() - 0.5) * 2; // Very thin vertical spread
          
          initialAngles[i] = angle;
          break;
        }
      }
      
      // Apply center position offset
      positions[i3] = x + centerPosition.x;
      positions[i3 + 1] = y + centerPosition.y;
      positions[i3 + 2] = z + centerPosition.z;
      
      // Assign color (gradient if multiple colors provided)
      const colorIndex = Math.floor((i / count) * threeColors.length);
      const particleColor = threeColors[Math.min(colorIndex, threeColors.length - 1)];
      
      colors[i3] = particleColor.r;
      colors[i3 + 1] = particleColor.g;
      colors[i3 + 2] = particleColor.b;
    }
    
    return { positions, colors, initialAngles };
  }, [count, distribution, radius, color, centerPosition]);
  
  // Animation loop
  useFrame((_state, delta) => {
    if (!enabled || !pointsRef.current) return;
    
    timeRef.current += delta * speed;
    const time = timeRef.current;
    
    const positionAttribute = pointsRef.current.geometry.attributes.position;
    const positions = positionAttribute.array as Float32Array;
    
    switch (animation) {
      case 'orbit': {
        // Rotate particles around the center
        for (let i = 0; i < count; i++) {
          const i3 = i * 3;
          const angle = initialAngles[i] + time;
          
          if (distribution === 'orbital' || distribution === 'ring') {
            const currentRadius = Math.sqrt(
              Math.pow(positions[i3] - centerPosition.x, 2) +
              Math.pow(positions[i3 + 1] - centerPosition.y, 2)
            );
            
            positions[i3] = centerPosition.x + Math.cos(angle) * currentRadius;
            positions[i3 + 1] = centerPosition.y + Math.sin(angle) * currentRadius;
            // Z remains the same
          }
        }
        positionAttribute.needsUpdate = true;
        break;
      }
      
      case 'pulse': {
        // Pulsing scale effect (handled via material uniforms)
        const scale = 1.0 + Math.sin(time * 2) * 0.2;
        if (pointsRef.current.material instanceof THREE.PointsMaterial) {
          pointsRef.current.material.size = size * scale;
        }
        break;
      }
      
      case 'float': {
        // Gentle floating motion
        for (let i = 0; i < count; i++) {
          const i3 = i * 3;
          const offset = i * 0.1; // Phase offset per particle
          
          positions[i3 + 2] += Math.sin(time + offset) * 0.05;
        }
        positionAttribute.needsUpdate = true;
        break;
      }
      
      case 'none':
      default:
        // No animation
        break;
    }
  });
  
  if (!enabled) return null;
  
  return (
    <points ref={pointsRef} layers={LAYERS.BLOOM}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={count}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={size}
        vertexColors
        transparent
        opacity={opacity}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        sizeAttenuation={true}
      />
    </points>
  );
}
