import { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { LAYERS } from '../../config/renderConfig';

/**
 * ConnectionPath Component
 * 
 * Creates a light stream connection between two nodes with traveling particles
 * Used for training completion animation
 * 
 * Requirements: 11.4, 12.3
 */

export interface ConnectionPathProps {
  startPosition: THREE.Vector3;
  endPosition: THREE.Vector3;
  color?: string;
  opacity?: number;
  particleCount?: number;
  animationDuration?: number;  // Duration in seconds
  onComplete?: () => void;
}

export function ConnectionPath({
  startPosition,
  endPosition,
  color = '#4DD0E1',
  opacity = 0.4,
  particleCount = 100,
  animationDuration = 3.0,
  onComplete,
}: ConnectionPathProps) {
  const lineRef = useRef<THREE.Line>(null);
  const particlesRef = useRef<THREE.Points>(null);
  const [isAnimating, setIsAnimating] = useState(true);
  const progressRef = useRef(0);
  const timeRef = useRef(0);
  
  // Create curved path between start and end
  const pathPoints = useMemo(() => {
    const points: THREE.Vector3[] = [];
    const segments = 50;
    
    // Calculate control point for bezier curve (arc upward)
    const midPoint = new THREE.Vector3()
      .addVectors(startPosition, endPosition)
      .multiplyScalar(0.5);
    
    // Add height to create arc
    const distance = startPosition.distanceTo(endPosition);
    const arcHeight = distance * 0.3; // Arc height is 30% of distance
    midPoint.z += arcHeight;
    
    // Create quadratic bezier curve
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const point = new THREE.Vector3();
      
      // Quadratic bezier formula: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
      point.x = Math.pow(1 - t, 2) * startPosition.x + 
                2 * (1 - t) * t * midPoint.x + 
                Math.pow(t, 2) * endPosition.x;
      
      point.y = Math.pow(1 - t, 2) * startPosition.y + 
                2 * (1 - t) * t * midPoint.y + 
                Math.pow(t, 2) * endPosition.y;
      
      point.z = Math.pow(1 - t, 2) * startPosition.z + 
                2 * (1 - t) * t * midPoint.z + 
                Math.pow(t, 2) * endPosition.z;
      
      points.push(point);
    }
    
    return points;
  }, [startPosition, endPosition]);
  
  // Create line geometry from path
  const lineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry().setFromPoints(pathPoints);
    return geometry;
  }, [pathPoints]);
  
  // Create particle positions along the path
  const { particlePositions, particleProgress } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const progress = new Float32Array(particleCount);
    
    for (let i = 0; i < particleCount; i++) {
      // Stagger particles along the path
      const t = i / particleCount;
      progress[i] = t;
      
      // Initial position at start
      positions[i * 3] = startPosition.x;
      positions[i * 3 + 1] = startPosition.y;
      positions[i * 3 + 2] = startPosition.z;
    }
    
    return { particlePositions: positions, particleProgress: progress };
  }, [particleCount, startPosition]);
  
  // Create particle colors (gradient from cyan to purple)
  const particleColors = useMemo(() => {
    const colors = new Float32Array(particleCount * 3);
    const startColor = new THREE.Color('#00D9FF'); // Cyan
    const endColor = new THREE.Color('#B24BF3');   // Purple
    
    for (let i = 0; i < particleCount; i++) {
      const t = i / particleCount;
      const color = new THREE.Color().lerpColors(startColor, endColor, t);
      
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }
    
    return colors;
  }, [particleCount]);
  
  // Animation loop
  useFrame((_state, delta) => {
    if (!isAnimating) return;
    
    timeRef.current += delta;
    progressRef.current = Math.min(timeRef.current / animationDuration, 1.0);
    
    // Animate particles along the path
    if (particlesRef.current) {
      const positionAttribute = particlesRef.current.geometry.attributes.position;
      const positions = positionAttribute.array as Float32Array;
      
      for (let i = 0; i < particleCount; i++) {
        // Calculate particle position along path with stagger
        const stagger = particleProgress[i] * 0.3; // 30% stagger
        const particleT = Math.max(0, Math.min(1, progressRef.current - stagger));
        
        // Get position on path
        const pathIndex = Math.floor(particleT * (pathPoints.length - 1));
        const nextIndex = Math.min(pathIndex + 1, pathPoints.length - 1);
        const localT = (particleT * (pathPoints.length - 1)) - pathIndex;
        
        const currentPoint = pathPoints[pathIndex];
        const nextPoint = pathPoints[nextIndex];
        
        // Interpolate between points
        positions[i * 3] = THREE.MathUtils.lerp(currentPoint.x, nextPoint.x, localT);
        positions[i * 3 + 1] = THREE.MathUtils.lerp(currentPoint.y, nextPoint.y, localT);
        positions[i * 3 + 2] = THREE.MathUtils.lerp(currentPoint.z, nextPoint.z, localT);
      }
      
      positionAttribute.needsUpdate = true;
    }
    
    // Animate line opacity (fade in then stay)
    if (lineRef.current && lineRef.current.material instanceof THREE.LineBasicMaterial) {
      const fadeInDuration = 0.5;
      if (progressRef.current < fadeInDuration) {
        lineRef.current.material.opacity = (progressRef.current / fadeInDuration) * opacity;
      } else {
        lineRef.current.material.opacity = opacity;
      }
    }
    
    // Complete animation
    if (progressRef.current >= 1.0) {
      setIsAnimating(false);
      if (onComplete) {
        onComplete();
      }
    }
  });
  
  // Create line material
  const lineMaterial = useMemo(() => {
    return new THREE.LineBasicMaterial({
      color: new THREE.Color(color),
      transparent: true,
      opacity: 0,
      linewidth: 2,
      blending: THREE.AdditiveBlending,
    });
  }, [color]);
  
  return (
    <group>
      {/* Connection line using primitive */}
      <primitive 
        ref={lineRef}
        object={new THREE.Line(lineGeometry, lineMaterial)}
        layers={LAYERS.BLOOM}
      />
      
      {/* Traveling particles */}
      <points ref={particlesRef} layers={LAYERS.BLOOM}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particleCount}
            array={particlePositions}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            count={particleCount}
            array={particleColors}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={2.0}
          vertexColors
          transparent
          opacity={0.9}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          sizeAttenuation={true}
        />
      </points>
    </group>
  );
}
