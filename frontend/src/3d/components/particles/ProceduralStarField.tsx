/**
 * Procedural Star Field Component
 * Generates and renders an animated galaxy with 15000-20000 stars using sprite-based rendering
 * Features:
 * - Animated spiral rotation with differential rotation based on distance
 * - Color gradients from warm center (orange/pink) to cool edges (purple/blue)
 * - Subtle twinkling/pulsing effects on stars
 * - Distance-based scaling
 * Requirements: 1.3, 17.1, 17.2, 17.3, 17.4, 17.5
 */

import React, { useMemo, useRef, useEffect } from 'react';
import * as THREE from 'three';
import { useFrame, useThree } from '@react-three/fiber';
import { generateStarField, calculateStarScale, applyGalaxyGradient } from '../../utils/galaxyGeneration';
import { 
  StarFieldConfig, 
  DEFAULT_STAR_FIELD_CONFIG 
} from '../../config/galaxyConfig';
import { 
  DEFAULT_STAR_CONFIG,
  DEFAULT_HAZE_CONFIG,
  LAYERS 
} from '../../config/renderConfig';

export interface ProceduralStarFieldProps {
  config?: Partial<StarFieldConfig>;
  quality?: 'high' | 'medium' | 'low' | 'mobile';
}

/**
 * ProceduralStarField Component
 * 
 * Generates a procedural galaxy with:
 * - 15000-20000 stars for dense, dramatic effect (Req 17.1)
 * - Core, outer core, and spiral arm distribution (Req 17.2)
 * - Animated spiral rotation with time-based movement (Req 17.3)
 * - Color gradients: warm orange/pink center → cool purple/blue edges (Req 17.3)
 * - Subtle twinkling/pulsing effects on stars (Req 17.3)
 * - Sprite-based rendering with textures (Req 17.4)
 * - Distance-based star scaling (Req 17.5)
 * - Selective bloom on BLOOM_LAYER (Req 17.4)
 * - Haze particle system at 50% of star count (Req 17.1)
 */
export const ProceduralStarField: React.FC<ProceduralStarFieldProps> = ({ 
  config: configOverride,
}) => {
  const { camera } = useThree();
  const starsRef = useRef<THREE.Points>(null);
  const hazeRef = useRef<THREE.Points>(null);
  
  // Merge config with defaults
  const config = useMemo(() => ({
    ...DEFAULT_STAR_FIELD_CONFIG,
    ...configOverride,
  }), [configOverride]);
  
  // Generate star field data (Req 17.1, 17.2)
  const { stars, hazeParticles, maxDistance } = useMemo(() => {
    const allStars = generateStarField(config);
    
    // Find max distance for gradient normalization
    const maxDist = Math.max(...allStars.map(s => s.distanceFromCenter));
    
    // Apply galaxy gradient colors (warm center → cool edges) (Req 17.3)
    const starsWithGradient = applyGalaxyGradient(allStars, maxDist);
    
    // Separate stars from haze particles
    const regularStars = starsWithGradient.filter((star) => !star.isHaze);
    const haze = starsWithGradient.filter((star) => star.isHaze);

    console.log(`Generated ${regularStars.length} stars and ${haze.length} haze particles with gradient colors`);
    
    return {
      stars: regularStars,
      hazeParticles: haze,
      maxDistance: maxDist,
    };
  }, [config]);
  
  // Create star sprite texture
  const starTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d')!;
    
    // Create radial gradient for star sprite
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.8)');
    gradient.addColorStop(0.4, 'rgba(255, 255, 255, 0.4)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    return texture;
  }, []);
  
  // Create haze sprite texture (larger, more diffuse)
  const hazeTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext('2d')!;
    
    // Create softer radial gradient for haze
    const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.6)');
    gradient.addColorStop(0.3, 'rgba(255, 255, 255, 0.3)');
    gradient.addColorStop(0.6, 'rgba(255, 255, 255, 0.1)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 128, 128);
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    return texture;
  }, []);
  
  // Create star geometry and attributes
  const starGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    
    // Position attribute
    const positions = new Float32Array(stars.length * 3);
    const colors = new Float32Array(stars.length * 3);
    const sizes = new Float32Array(stars.length);
    
    stars.forEach((star, i) => {
      // Position
      positions[i * 3] = star.position.x;
      positions[i * 3 + 1] = star.position.y;
      positions[i * 3 + 2] = star.position.z;
      
      // Color
      const color = new THREE.Color(star.color);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
      
      // Size
      sizes[i] = star.size * DEFAULT_STAR_CONFIG.minSize;
    });
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    return geometry;
  }, [stars]);
  
  // Create haze geometry and attributes
  const hazeGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    
    const positions = new Float32Array(hazeParticles.length * 3);
    const colors = new Float32Array(hazeParticles.length * 3);
    const sizes = new Float32Array(hazeParticles.length);
    
    hazeParticles.forEach((particle, i) => {
      // Position
      positions[i * 3] = particle.position.x;
      positions[i * 3 + 1] = particle.position.y;
      positions[i * 3 + 2] = particle.position.z;
      
      // Color (slightly dimmer for haze)
      const color = new THREE.Color(particle.color);
      colors[i * 3] = color.r * 0.8;
      colors[i * 3 + 1] = color.g * 0.8;
      colors[i * 3 + 2] = color.b * 0.8;
      
      // Size (larger for haze)
      sizes[i] = particle.size * DEFAULT_HAZE_CONFIG.size;
    });
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    return geometry;
  }, [hazeParticles]);
  
  // Assign stars to BLOOM_LAYER for selective bloom (Req 17.4, 18.2)
  // Note: Objects are visible on BASE layer by default, we enable BLOOM layer additionally
  useEffect(() => {
    if (starsRef.current) {
      // Enable BLOOM_LAYER in addition to BASE_LAYER (don't replace)
      starsRef.current.layers.enable(LAYERS.BLOOM);
      console.log('Stars assigned to BASE and BLOOM layers');
    }
    if (hazeRef.current) {
      // Enable BLOOM_LAYER in addition to BASE_LAYER (don't replace)
      hazeRef.current.layers.enable(LAYERS.BLOOM);
      console.log('Haze assigned to BASE and BLOOM layers');
    }
    console.log('Star field mounted with', stars.length, 'stars and', hazeParticles.length, 'haze particles');
  }, [stars.length, hazeParticles.length]);
  
  // Animation: spiral rotation, twinkling, and distance-based scaling (Req 17.3, 17.5)
  useFrame(({ clock }) => {
    if (!starsRef.current || !camera) return;
    
    const geometry = starsRef.current.geometry;
    const positions = geometry.attributes.position.array as Float32Array;
    const sizes = geometry.attributes.size.array as Float32Array;
    const cameraPosition = camera.position;
    const time = clock.getElapsedTime();
    
    // Rotation speed (increased for more visible spinning)
    const rotationSpeed = 0.1; // Radians per second (5x faster)
    
    // Update star positions and sizes
    for (let i = 0; i < stars.length; i++) {
      const star = stars[i];
      
      // Calculate rotation based on distance from center
      // Stars farther from center rotate slower (differential rotation)
      const distanceRatio = star.distanceFromCenter / maxDistance;
      const rotationAmount = time * rotationSpeed * (1 - distanceRatio * 0.5);
      
      // Calculate new angle
      const newAngle = star.angle + rotationAmount;
      
      // Calculate new position using polar coordinates
      const x = star.distanceFromCenter * Math.cos(newAngle);
      const y = star.distanceFromCenter * Math.sin(newAngle);
      const z = star.position.z; // Z stays the same
      
      // Update position
      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;
      
      // Calculate distance-based size scaling
      const starPos = new THREE.Vector3(x, y, z);
      const baseSize = star.size * DEFAULT_STAR_CONFIG.minSize;
      let scaledSize = calculateStarScale(
        starPos,
        cameraPosition,
        baseSize,
        DEFAULT_STAR_CONFIG.distanceScaleFactor
      );
      
      // Add subtle twinkling effect using sine wave
      // Different stars twinkle at different rates based on their index
      const twinkleSpeed = 2.0 + (i % 10) * 0.3; // Vary speed
      const twinklePhase = (i % 100) * 0.1; // Vary phase
      const twinkle = Math.sin(time * twinkleSpeed + twinklePhase) * 0.15 + 1.0; // 0.85 to 1.15
      
      scaledSize *= twinkle;
      
      sizes[i] = scaledSize;
    }
    
    // Mark attributes as needing update
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.size.needsUpdate = true;
  });
  
  // Animate haze particles with slower rotation and pulsing
  useFrame(({ clock }) => {
    if (!hazeRef.current) return;
    
    const geometry = hazeRef.current.geometry;
    const positions = geometry.attributes.position.array as Float32Array;
    const sizes = geometry.attributes.size.array as Float32Array;
    const time = clock.getElapsedTime();
    
    // Haze rotates slower than stars but still visible
    const hazeRotationSpeed = 0.05;
    
    for (let i = 0; i < hazeParticles.length; i++) {
      const particle = hazeParticles[i];
      
      // Calculate rotation
      const distanceRatio = particle.distanceFromCenter / maxDistance;
      const rotationAmount = time * hazeRotationSpeed * (1 - distanceRatio * 0.6);
      const newAngle = particle.angle + rotationAmount;
      
      // Update position
      const x = particle.distanceFromCenter * Math.cos(newAngle);
      const y = particle.distanceFromCenter * Math.sin(newAngle);
      
      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = particle.position.z;
      
      // Add gentle pulsing to haze
      const pulseSpeed = 1.0 + (i % 5) * 0.2;
      const pulsePhase = (i % 50) * 0.2;
      const pulse = Math.sin(time * pulseSpeed + pulsePhase) * 0.1 + 1.0; // 0.9 to 1.1
      
      const baseSize = particle.size * DEFAULT_HAZE_CONFIG.size;
      sizes[i] = baseSize * pulse;
    }
    
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.size.needsUpdate = true;
  });
  
  return (
    <group name="procedural-star-field">
      {/* Regular stars with sprite-based rendering (Req 17.4) */}
      <points ref={starsRef} geometry={starGeometry}>
        <pointsMaterial
          map={starTexture}
          size={DEFAULT_STAR_CONFIG.maxSize}
          sizeAttenuation={DEFAULT_STAR_CONFIG.sizeAttenuation}
          vertexColors
          transparent
          opacity={1.0}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
      
      {/* Haze particles (50% of star count) (Req 17.1) */}
      <points ref={hazeRef} geometry={hazeGeometry}>
        <pointsMaterial
          map={hazeTexture}
          size={DEFAULT_HAZE_CONFIG.size}
          sizeAttenuation={true}
          vertexColors
          transparent
          opacity={DEFAULT_HAZE_CONFIG.opacity}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
    </group>
  );
};

export default ProceduralStarField;
