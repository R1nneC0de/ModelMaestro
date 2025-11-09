import React, { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import { Mesh, Shape, ExtrudeGeometry } from 'three';
import * as THREE from 'three';
import { NavigationNodeConfig } from '../../config/navigationNodes';
import { getNavigationNodeColors } from '../../config/colorPalette';
import { HighlightGeometry } from '../effects/HighlightGeometry';
import { useCurrentView } from '../../store/navigationStore';

/**
 * NavigationNode Component
 * Represents a navigable node as a transparent circle with icon and text label
 * Replaces the planet-based CelestialBody component with modern design
 * 
 * Requirements:
 * - 1.2: Display at least three distinct navigation nodes
 * - 6.1: Create Model node with vibrant purple tones
 * - 6.2: Past Models node with amber-gold tones
 * - 6.3: Info node with cool cyan tones
 * 
 * Features:
 * - Transparent circle using ring geometry (thin outline)
 * - Icon in center (simple geometry)
 * - HTML text label above circle using drei's Html component
 * - Positioned in spiral arms of galaxy
 * - Subtle glow effect on circle border
 * - Hover state (brighten circle)
 */

export interface NavigationNodeProps {
  config: NavigationNodeConfig;
  onClick?: (id: string) => void;
  onHover?: (id: string, hovered: boolean) => void;
  isFocused?: boolean;  // Whether this node is currently focused (Req 6.4)
  isTraining?: boolean;  // Whether this node is in training state (Req 11.3)
  trainingProgress?: number;  // Training progress 0-1 (Req 11.3)
}

/**
 * Create simple geometric icon based on type
 */
const createIconGeometry = (iconType: 'upload' | 'history' | 'info') => {
  const shape = new Shape();
  
  switch (iconType) {
    case 'upload':
      // Upload arrow icon - upward pointing arrow (larger and simpler)
      shape.moveTo(-0.4, -0.2);
      shape.lineTo(0, 0.5);
      shape.lineTo(0.4, -0.2);
      shape.lineTo(0.2, -0.2);
      shape.lineTo(0.2, -0.6);
      shape.lineTo(-0.2, -0.6);
      shape.lineTo(-0.2, -0.2);
      shape.closePath();
      break;
      
    case 'history':
      // History/clock icon - circle with clock hands (larger)
      // Outer circle
      for (let i = 0; i <= 32; i++) {
        const angle = (i / 32) * Math.PI * 2;
        const x = Math.cos(angle) * 0.5;
        const y = Math.sin(angle) * 0.5;
        if (i === 0) {
          shape.moveTo(x, y);
        } else {
          shape.lineTo(x, y);
        }
      }
      shape.closePath();
      
      // Add clock hands
      // Hour hand
      shape.moveTo(-0.05, 0);
      shape.lineTo(0.05, 0);
      shape.lineTo(0.05, 0.25);
      shape.lineTo(-0.05, 0.25);
      shape.closePath();
      
      // Minute hand
      shape.moveTo(-0.03, 0);
      shape.lineTo(0.03, 0);
      shape.lineTo(0.03, 0.4);
      shape.lineTo(-0.03, 0.4);
      shape.closePath();
      break;
      
    case 'info':
      // Info icon - letter 'i' shape (larger)
      // Top dot
      shape.moveTo(-0.15, 0.35);
      shape.lineTo(0.15, 0.35);
      shape.lineTo(0.15, 0.5);
      shape.lineTo(-0.15, 0.5);
      shape.closePath();
      
      // Bottom stem
      shape.moveTo(-0.15, -0.5);
      shape.lineTo(0.15, -0.5);
      shape.lineTo(0.15, 0.2);
      shape.lineTo(-0.15, 0.2);
      shape.closePath();
      break;
  }
  
  return new ExtrudeGeometry(shape, {
    depth: 0.1,  // Thicker for better visibility
    bevelEnabled: false,
  });
};

/**
 * NavigationNode - Interactive circle node with icon and label
 * 
 * Renders:
 * - Transparent circle outline (ring geometry)
 * - Icon in center (simple geometry based on type)
 * - Text label above circle (HTML overlay)
 * - Glow effect on hover
 */
export const NavigationNode: React.FC<NavigationNodeProps> = ({
  config,
  onClick,
  onHover,
  isFocused = false,
  isTraining = false,
  trainingProgress = 0,
}) => {
  const circleRef = useRef<Mesh>(null);
  const iconRef = useRef<Mesh>(null);
  const glowRingRef = useRef<Mesh>(null);
  const groupRef = useRef<THREE.Group>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [hoverIntensity, setHoverIntensity] = useState(0);
  const pulseTimeRef = useRef(0);
  
  // Particle burst state
  const [particles, setParticles] = useState<Array<{
    id: number;
    angle: number;
    distance: number;
    opacity: number;
    speed: number;
  }>>([]);
  
  // Focus scale state (Req 6.4)
  const focusScaleRef = useRef(1.0);
  const targetFocusScaleRef = useRef(1.0);
  
  // Highlight effects state (Req 16.2, 16.3, 16.4)
  const [enableDistanceScaling, setEnableDistanceScaling] = useState(false);
  const [enableColorTransition, setEnableColorTransition] = useState(false);
  const [showHighlight, setShowHighlight] = useState(false);
  
  // Get colors for this node type
  const colors = useMemo(() => getNavigationNodeColors(config.type), [config.type]);
  
  // Store the position
  const position = useMemo(() => config.position.clone(), [config.position]);
  
  // Create icon geometry
  const iconGeometry = useMemo(() => createIconGeometry(config.iconType), [config.iconType]);

  // Check if overlay is active (hide labels when overlay is shown)
  const currentView = useCurrentView();
  const shouldShowLabels = currentView === 'overview';

  // Update target focus scale when focus state changes (Req 6.4)
  useEffect(() => {
    if (isFocused) {
      // Scale up by 10-20% when focused (Req 6.4)
      // Using 15% as a middle ground
      targetFocusScaleRef.current = 1.15;
    } else {
      // Scale back to normal when not focused
      targetFocusScaleRef.current = 1.0;
    }
  }, [isFocused]);

  // Listen for travel events to control highlight effects (Req 16.2, 16.3, 16.4)
  useEffect(() => {
    const handleApproachStart = (event: Event) => {
      const customEvent = event as CustomEvent;
      if (customEvent.detail?.targetId === config.id) {
        // Enable distance-based scaling during approach (Req 16.2, 16.3)
        setEnableDistanceScaling(true);
        setShowHighlight(true);
      }
    };

    const handleArrival = (event: Event) => {
      const customEvent = event as CustomEvent;
      if (customEvent.detail?.targetId === config.id) {
        // Hide highlight immediately on arrival instead of showing color transition
        setEnableDistanceScaling(false);
        setEnableColorTransition(false);
        setShowHighlight(false);
      }
    };

    const handleReturnStart = () => {
      // Reset highlight effects when returning to overview
      setEnableDistanceScaling(false);
      setEnableColorTransition(false);
      setShowHighlight(false);
    };

    window.addEventListener('travel:approach-start', handleApproachStart);
    window.addEventListener('travel:arrival', handleArrival);
    window.addEventListener('travel:return-start', handleReturnStart);

    return () => {
      window.removeEventListener('travel:approach-start', handleApproachStart);
      window.removeEventListener('travel:arrival', handleArrival);
      window.removeEventListener('travel:return-start', handleReturnStart);
    };
  }, [config.id]);

  // Animate hover effects (Req 6.3: Task 6.3 - Update hover effects for NavigationNode)
  useFrame((_state, delta) => {
    // Animate focus scale (Req 6.4)
    // Smooth animation over 1 second (delta * 5 gives ~1 second transition at 60fps)
    const focusScaleDelta = (targetFocusScaleRef.current - focusScaleRef.current) * delta * 5;
    focusScaleRef.current += focusScaleDelta;
    
    // Apply focus scale to entire group
    if (groupRef.current) {
      groupRef.current.scale.setScalar(focusScaleRef.current);
    }
    
    // Animate glow intensity increase on hover (Req 6.1, 6.2, 6.3)
    if (isHovered) {
      // Smoothly increase hover intensity to 1.0
      setHoverIntensity(prev => Math.min(prev + delta * 3, 1.0));
      
      // Update pulse time for pulsing animation (Req 6.3)
      pulseTimeRef.current += delta * 2.5; // Pulse speed
    } else {
      // Smoothly decrease hover intensity back to 0
      setHoverIntensity(prev => Math.max(prev - delta * 3, 0));
      
      // Reset pulse time when not hovering
      pulseTimeRef.current = 0;
    }
    
    // Animate particles
    if (particles.length > 0) {
      setParticles(prev => 
        prev
          .map(p => ({
            ...p,
            distance: p.distance + p.speed * delta * 20,
            opacity: Math.max(0, p.opacity - delta * 1.5),
          }))
          .filter(p => p.opacity > 0)
      );
    }
    
    // Subtle scale animation on hover - icon scales to 1.1x (Req 6.3)
    if (iconRef.current) {
      const targetScale = isHovered ? 1.1 : 1.0;
      const currentScale = iconRef.current.scale.x;
      const newScale = currentScale + (targetScale - currentScale) * delta * 5;
      iconRef.current.scale.setScalar(newScale);
    }
    
    // Subtle pulsing animation to circle on hover (Req 6.3)
    if (circleRef.current && isHovered) {
      // Calculate pulse using sine wave (0.95 to 1.05 scale range)
      const pulse = Math.sin(pulseTimeRef.current) * 0.5 + 0.5; // Normalize to 0-1
      const scaleVariation = 0.95 + (pulse * 0.1); // 0.95 to 1.05
      circleRef.current.scale.setScalar(scaleVariation);
    } else if (circleRef.current) {
      // Return to normal scale when not hovering
      const currentScale = circleRef.current.scale.x;
      const newScale = currentScale + (1.0 - currentScale) * delta * 5;
      circleRef.current.scale.setScalar(newScale);
    }
    
    // Enhanced glow ring pulsing on hover or training (Req 6.3, 11.3)
    if (glowRingRef.current) {
      if (isHovered || isTraining) {
        // Pulse the glow ring with slightly different phase for layered effect
        const pulseSpeed = isTraining ? 3.0 : 1.0; // Faster pulse during training
        const glowPulse = Math.sin(pulseTimeRef.current * pulseSpeed + 0.5) * 0.5 + 0.5;
        const glowScale = 0.98 + (glowPulse * 0.08); // 0.98 to 1.06
        glowRingRef.current.scale.setScalar(glowScale);
        
        // Increase glow intensity during training (Req 11.3)
        if (glowRingRef.current.material instanceof THREE.MeshBasicMaterial) {
          const baseOpacity = 0.3;
          const trainingBoost = isTraining ? trainingProgress * 0.4 : 0; // Up to +0.4 opacity
          const hoverBoost = isHovered ? hoverIntensity * 0.4 : 0;
          glowRingRef.current.material.opacity = baseOpacity + trainingBoost + hoverBoost;
        }
      } else {
        // Return to normal scale
        const currentScale = glowRingRef.current.scale.x;
        const newScale = currentScale + (1.0 - currentScale) * delta * 5;
        glowRingRef.current.scale.setScalar(newScale);
        
        // Reset opacity
        if (glowRingRef.current.material instanceof THREE.MeshBasicMaterial) {
          glowRingRef.current.material.opacity = 0.3;
        }
      }
    }
  });

  // Handle click events
  const handleClick = (event: any) => {
    console.log('NavigationNode clicked:', config.id, 'clickable:', config.clickable);
    event.stopPropagation(); // Stop after logging
    if (onClick && config.clickable) {
      console.log('Calling onClick handler for:', config.id);
      onClick(config.id);
    }
  };

  // Handle pointer over events
  const handlePointerOver = (event: any) => {
    event.stopPropagation();
    if (config.hoverHighlight) {
      setIsHovered(true);
      document.body.style.cursor = 'pointer'; // Change cursor to pointer (Req 2.2)
      
      // Create particle burst
      const newParticles = Array.from({ length: 12 }, (_, i) => ({
        id: Date.now() + i,
        angle: (i / 12) * Math.PI * 2,
        distance: 0,
        opacity: 1,
        speed: 0.5 + Math.random() * 0.5,
      }));
      setParticles(newParticles);
      
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

  // Note: Using white color for all circles now (matching reference design)
  // const circleColor = isHovered ? colors.hover : colors.circle;

  // Hide navigation nodes when in focused view to prevent large circles from showing
  const shouldShowNode = currentView === 'overview';

  return (
    <group ref={groupRef} position={position} visible={shouldShowNode}>
      {/* Invisible larger hitbox for easier clicking */}
      <mesh
        position={[0, 0, 0]}
        rotation={[Math.PI / 2, 0, 0]}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        name={`${config.id}-hitbox`}
      >
        <circleGeometry args={[config.circleRadius * 1.5, 32]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      
      {/* Glass circle background - filled with frosted glass effect */}
      <mesh
        rotation={[Math.PI / 2, 0, 0]}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        <circleGeometry args={[config.circleRadius, 64]} />
        <meshBasicMaterial
          color="#FFFFFF"
          transparent
          opacity={0.35 + (hoverIntensity * 0.15)} // Much more visible glass fill
          depthWrite={false}
        />
      </mesh>
      
      {/* Glass circle outline (ring geometry) */}
      <mesh
        ref={circleRef}
        rotation={[Math.PI / 2, 0, 0]}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        name={config.id}
        userData={{ id: config.id }}
      >
        <ringGeometry args={[
          config.circleRadius * 0.96,
          config.circleRadius,
          64
        ]} />
        <meshBasicMaterial
          color="#FFFFFF"
          transparent
          opacity={0.85 + (hoverIntensity * 0.15)} // Very opaque, fully visible
        />
      </mesh>
      
      {/* Inner glass reflection ring */}
      <mesh
        rotation={[Math.PI / 2, 0, 0]}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        <ringGeometry args={[
          config.circleRadius * 0.7,
          config.circleRadius * 0.72,
          64
        ]} />
        <meshBasicMaterial
          color="#FFFFFF"
          transparent
          opacity={0.5 + (hoverIntensity * 0.25)} // More visible inner reflection
          depthWrite={false}
        />
      </mesh>
      
      {/* Icon in center */}
      <mesh
        ref={iconRef}
        position={[0, 0, 0]} // Center of circle
        rotation={[Math.PI / 2, 0, 0]}  // Rotate to face camera (looking up from below)
        scale={config.circleRadius * 0.5} // Larger scale for visibility
        geometry={iconGeometry}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        <meshBasicMaterial
          color="#FFFFFF"  // White icon like reference
          transparent
          opacity={0.9 + (hoverIntensity * 0.1)}  // Very visible icon
          side={THREE.DoubleSide}  // Render both sides
        />
      </mesh>
      
      {/* Soft glow ring for glass effect */}
      <mesh
        ref={glowRingRef}
        rotation={[Math.PI / 2, 0, 0]}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        <ringGeometry args={[
          config.circleRadius * 1.0,
          config.circleRadius * 1.08,
          64
        ]} />
        <meshBasicMaterial
          color={colors.circleGlow}
          transparent
          opacity={0.55 + (hoverIntensity * 0.45)} // Much stronger glow, very visible
          blending={2} // AdditiveBlending
          depthWrite={false}
        />
      </mesh>
      
      {/* Ripple effect rings - expand on hover */}
      {isHovered && [0, 1, 2].map((index) => (
        <mesh
          key={`ripple-${index}`}
          rotation={[Math.PI / 2, 0, 0]}
          onClick={handleClick}
        >
          <ringGeometry args={[
            config.circleRadius * (1.1 + index * 0.15 + (pulseTimeRef.current % 1) * 0.3),
            config.circleRadius * (1.12 + index * 0.15 + (pulseTimeRef.current % 1) * 0.3),
            64
          ]} />
          <meshBasicMaterial
            color={colors.circleGlow}
            transparent
            opacity={Math.max(0, 0.4 - (pulseTimeRef.current % 1) - index * 0.15)}
            blending={2}
            depthWrite={false}
          />
        </mesh>
      ))}

      {/* Text labels above circle - clean aesthetic design */}
      {shouldShowLabels && (
        <Html
          position={[0, config.circleRadius + 50, 0]}
          center
          distanceFactor={3}
          occlude={false}
          style={{
            pointerEvents: 'none',
            userSelect: 'none',
            transition: 'opacity 0.5s ease',
            transform: 'scale(60)',
            opacity: shouldShowLabels ? 1 : 0,
          }}
        >
          <div
            style={{
              textAlign: 'center',
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '8px',
              filter: 'drop-shadow(0 8px 24px rgba(0, 0, 0, 0.9))',
            }}
          >
            {/* Category/Subtitle - small text above */}
            <div
              style={{
                fontSize: '46px',
                fontWeight: '600',
                color: 'rgba(255, 255, 255, 0.75)',
                textTransform: 'uppercase',
                letterSpacing: '5px',
                transition: 'all 0.3s ease',
                textShadow: '0 4px 12px rgba(0, 0, 0, 1), 0 2px 6px rgba(0, 0, 0, 0.8)',
              }}
            >
              {config.subtitle}
            </div>
            
            {/* Main label - larger text below */}
            <div
              style={{
                fontSize: '78px',
                fontWeight: '900',
                color: '#FFFFFF',
                textTransform: 'uppercase',
                letterSpacing: '8px',
                textShadow: isHovered 
                  ? `0 0 40px ${colors.circleGlow}, 0 0 60px ${colors.circleGlow}, 0 0 80px ${colors.circleGlow}, 0 6px 20px rgba(0, 0, 0, 1)`
                  : `0 0 25px ${colors.circleGlow}, 0 0 40px ${colors.circleGlow}, 0 6px 20px rgba(0, 0, 0, 1)`,
                transition: 'all 0.3s ease',
                whiteSpace: 'nowrap',
              }}
            >
              {config.label}
            </div>
          
          {/* Description on hover - fade in below */}
          {isHovered && (
            <div
              style={{
                fontSize: '32px',
                fontWeight: '400',
                color: 'rgba(255, 255, 255, 0.7)',
                marginTop: '6px',
                maxWidth: '585px',
                lineHeight: '1.4',
                animation: 'fadeInSlide 0.4s ease-out',
                textAlign: 'center',
              }}
            >
              {config.description}
            </div>
          )}
        </div>
        
        <style>
          {`
            @keyframes fadeInSlide {
              from {
                opacity: 0;
                transform: translateY(-5px);
              }
              to {
                opacity: 1;
                transform: translateY(0);
              }
            }
          `}
        </style>
        </Html>
      )}

      {/* Particle burst effect */}
      {particles.map((particle) => {
        const x = Math.cos(particle.angle) * particle.distance;
        const y = Math.sin(particle.angle) * particle.distance;
        return (
          <mesh
            key={particle.id}
            position={[x, 0, y]}
            rotation={[Math.PI / 2, 0, 0]}
          >
            <circleGeometry args={[0.3, 8]} />
            <meshBasicMaterial
              color={colors.circleGlow}
              transparent
              opacity={particle.opacity * 0.8}
              blending={2}
              depthWrite={false}
            />
          </mesh>
        );
      })}
      
      {/* Highlight geometry for navigation travel effects only (Req 16.2, 16.3, 16.4) */}
      {config.hoverHighlight && showHighlight && (
        <HighlightGeometry
          scale={config.circleRadius * 1.15}
          color={colors.circleGlow}
          pulseSpeed={2.0}
          pulseIntensityMin={0.3}
          pulseIntensityMax={0.8}
          visible={showHighlight}
          targetPosition={config.position}
          enableDistanceScaling={enableDistanceScaling}
          enableColorTransition={enableColorTransition}
          onTransitionComplete={() => {
            // Remove highlight after color transition completes (Req 16.5)
            setShowHighlight(false);
            setEnableColorTransition(false);
          }}
        />
      )}
    </group>
  );
};

export default NavigationNode;
