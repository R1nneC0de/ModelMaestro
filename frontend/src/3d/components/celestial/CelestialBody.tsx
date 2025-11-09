import React, { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh, Vector3 } from 'three';
import { NavigationNodeConfig } from '../../config/navigationNodes';
import { HighlightGeometry } from '../effects/HighlightGeometry';
import { LAYERS } from '../../config/renderConfig';

/**
 * CelestialBody Component
 * Represents a navigable planet in the galaxy scene
 * 
 * Requirements:
 * - 1.2: Display at least three distinct celestial bodies
 * - 6.1: Create Model body with vibrant blue-purple tones and active energy
 * - 6.2: Past Models body with amber-gold tones and orbital ring structures
 * - 6.3: Info body with cool cyan-white tones and stable luminescence
 * 
 * Features:
 * - Sphere geometry with MeshStandardMaterial
 * - Color and emissive properties from config
 * - Positioned according to celestialBodies config
 * - Basic orbital animation
 */

export interface CelestialBodyProps {
  config: NavigationNodeConfig;
  onClick?: (id: string) => void;
  onHover?: (id: string, hovered: boolean) => void;
}

/**
 * CelestialBody - Interactive planet component
 * 
 * Renders a sphere with:
 * - Custom color and glow (emissive) properties
 * - Orbital motion around its position
 * - Click and hover interaction support
 */
export const CelestialBody: React.FC<CelestialBodyProps> = ({
  config,
  onClick,
  onHover,
}) => {
  const meshRef = useRef<Mesh>(null);
  const orbitAngleRef = useRef(0);
  const [isHovered, setIsHovered] = useState(false);
  const [hoverEmissiveBoost, setHoverEmissiveBoost] = useState(0);
  
  // Store the base position for orbital calculations
  const basePosition = useMemo(() => config.position.clone(), [config.position]);

  // Assign celestial body to appropriate layers (Req 17.4, 18.2)
  // Note: Objects are visible on BASE layer (0) by default
  useEffect(() => {
    if (meshRef.current) {
      // If the material has emissive properties (glow), also add to BLOOM_LAYER
      // This allows the MultiLayerRenderer to apply bloom to glowing parts
      if (config.glowIntensity > 0) {
        meshRef.current.layers.enable(LAYERS.BLOOM);
        console.log(`Celestial body ${config.id} assigned to BASE and BLOOM layers`);
      } else {
        console.log(`Celestial body ${config.id} assigned to BASE layer only`);
      }
    }
  }, [config.id, config.glowIntensity]);

  // Animate hover effects (orbital motion removed for navigation nodes)
  useFrame((_state, delta) => {
    if (!meshRef.current) return;

    // Navigation nodes are stationary at their position
    meshRef.current.position.copy(basePosition);

    // Animate glow intensity increase on hover (Req 2.2)
    if (isHovered) {
      // Smoothly increase glow boost to 0.5
      setHoverEmissiveBoost(prev => Math.min(prev + delta * 2, 0.5));
    } else {
      // Smoothly decrease glow boost back to 0
      setHoverEmissiveBoost(prev => Math.max(prev - delta * 2, 0));
    }
  });

  // Handle click events
  const handleClick = (event: any) => {
    event.stopPropagation();
    if (onClick && config.clickable) {
      onClick(config.id);
    }
  };

  // Handle pointer over events
  const handlePointerOver = (event: any) => {
    event.stopPropagation();
    if (config.hoverHighlight) {
      setIsHovered(true);
      document.body.style.cursor = 'pointer'; // Change cursor to pointer (Req 2.2)
      
      if (onHover) {
        onHover(config.id, true);
      }
    }
  };

  // Handle pointer out events
  const handlePointerOut = (event: any) => {
    event.stopPropagation();
    if (config.hoverHighlight) {
      setIsHovered(false);
      document.body.style.cursor = 'default';
      
      if (onHover) {
        onHover(config.id, false);
      }
    }
  };

  return (
    <group>
      {/* Main navigation node mesh - temporary sphere until NavigationNode component is created */}
      <mesh
        ref={meshRef}
        position={config.position}
        scale={config.circleRadius / 10} // Scale based on circle radius
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        name={config.id} // Set name for raycasting identification
        userData={{ id: config.id }} // Set userData for raycasting identification
      >
        {/* Sphere geometry - 32 segments for smooth appearance */}
        <sphereGeometry args={[1, 32, 32]} />
        
        {/* MeshStandardMaterial with circle color and glow */}
        {/* Glow intensity increases on hover (Req 2.2) */}
        <meshStandardMaterial
          color={config.circleColor}
          emissive={config.circleColor}
          emissiveIntensity={config.glowIntensity + hoverEmissiveBoost}
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* Highlight geometry shown on hover (Req 2.1, 16.1) */}
      {config.hoverHighlight && meshRef.current && (
        <group position={meshRef.current.position}>
          <HighlightGeometry
            scale={config.circleRadius / 10}
            color="#00FFFF" // Bright cyan for highlight
            pulseSpeed={2.0}
            pulseIntensityMin={0.3}
            pulseIntensityMax={0.8}
            visible={isHovered}
          />
        </group>
      )}
    </group>
  );
};

export default CelestialBody;
