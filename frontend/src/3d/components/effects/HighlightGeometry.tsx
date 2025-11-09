import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Mesh, Color, Vector3 } from 'three';
import * as TWEEN from '@tweenjs/tween.js';

/**
 * HighlightGeometry Component
 * Renders a pulsing highlight ring around celestial bodies on hover
 * 
 * Requirements:
 * - 2.1: Show highlight on hover with pulsing animation
 * - 2.2: Provide visual feedback for interactive objects
 * - 16.1: Animated pulsing effect for hover state
 * - 16.2: Distance-based highlight scaling during camera approach
 * - 16.3: Real-time highlight size updates during camera flight
 * - 16.4: Highlight color transition on arrival (fade to cyan)
 * - 16.5: Remove highlight geometry after fade completes
 */

export interface HighlightGeometryProps {
  scale: number;
  color?: string;
  pulseSpeed?: number;
  pulseIntensityMin?: number;
  pulseIntensityMax?: number;
  visible?: boolean;
  targetPosition?: Vector3;  // Position of the target body for distance calculation
  enableDistanceScaling?: boolean;  // Enable distance-based scaling (Req 16.2)
  enableColorTransition?: boolean;  // Enable color transition on arrival (Req 16.4)
  onTransitionComplete?: () => void;  // Callback when color transition completes (Req 16.5)
}

/**
 * HighlightGeometry - Animated highlight ring for hover effects
 * 
 * Features:
 * - Pulsing animation using sine wave
 * - Configurable color and pulse parameters
 * - Slightly larger than the target object for visibility
 * - Additive blending for glow effect
 * - Distance-based scaling during camera approach (Req 16.2, 16.3)
 * - Color transition on arrival (Req 16.4, 16.5)
 */
export const HighlightGeometry: React.FC<HighlightGeometryProps> = ({
  scale,
  color = '#00FFFF', // Bright cyan (Req 16.1)
  pulseSpeed = 2.0,
  pulseIntensityMin = 0.3,
  pulseIntensityMax = 0.8,
  visible = true,
  targetPosition,
  enableDistanceScaling = false,
  enableColorTransition = false,
  onTransitionComplete,
}) => {
  const meshRef = useRef<Mesh>(null);
  const timeRef = useRef(0);
  const { camera } = useThree();
  
  // State for distance-based scaling (Req 16.2)
  const distanceScaleRef = useRef(1.0);
  const baseScaleRef = useRef(scale);
  
  // State for color transition (Req 16.4)
  const currentColorRef = useRef(new Color(color));
  const targetColorRef = useRef(new Color('#3BEAF7')); // Cyan RGB(59, 234, 247)
  const transitionProgressRef = useRef(0);
  const isTransitioningRef = useRef(false);
  const transitionTweenRef = useRef<TWEEN.Tween<any> | null>(null);

  // Parse initial color
  const initialColor = useMemo(() => new Color(color), [color]);

  // Update base scale when prop changes
  useEffect(() => {
    baseScaleRef.current = scale;
  }, [scale]);

  // Start color transition when enabled (Req 16.4)
  useEffect(() => {
    if (enableColorTransition && !isTransitioningRef.current) {
      isTransitioningRef.current = true;
      transitionProgressRef.current = 0;
      
      // Create TWEEN for color transition (3 seconds)
      const progressObj = { value: 0 };
      transitionTweenRef.current = new TWEEN.Tween(progressObj)
        .to({ value: 1 }, 3000) // 3 seconds (Req 16.4)
        .easing(TWEEN.Easing.Cubic.InOut)
        .onUpdate(() => {
          transitionProgressRef.current = progressObj.value;
        })
        .onComplete(() => {
          // Transition complete, notify parent to remove highlight (Req 16.5)
          if (onTransitionComplete) {
            onTransitionComplete();
          }
        })
        .start();
    }
    
    return () => {
      // Cleanup tween on unmount
      if (transitionTweenRef.current) {
        transitionTweenRef.current.stop();
      }
    };
  }, [enableColorTransition, onTransitionComplete]);

  // Animate pulsing effect and handle distance-based scaling
  useFrame((_state, delta) => {
    if (!meshRef.current || !visible) return;

    // Update TWEEN for color transition
    if (isTransitioningRef.current) {
      TWEEN.update();
    }

    // Update time for pulsing
    timeRef.current += delta * pulseSpeed;

    // Calculate pulse intensity using sine wave
    const pulse = Math.sin(timeRef.current) * 0.5 + 0.5; // Normalize to 0-1
    const intensity = pulseIntensityMin + (pulse * (pulseIntensityMax - pulseIntensityMin));

    // Distance-based scaling (Req 16.2, 16.3)
    if (enableDistanceScaling && targetPosition) {
      // Calculate distance from camera to target
      const distance = camera.position.distanceTo(targetPosition);
      
      // Scale highlight to 1.1% of distance value (Req 16.2)
      // This creates a dynamic effect where the highlight grows as camera approaches
      const distanceScale = distance * 0.011; // 1.1% of distance
      
      // Clamp to reasonable values (between 0.5x and 2x base scale)
      // Also ensure it doesn't exceed a maximum absolute size
      const relativeScale = distanceScale / baseScaleRef.current;
      const maxAbsoluteScale = 50; // Maximum size in world units
      const absoluteClampedScale = Math.min(relativeScale * baseScaleRef.current, maxAbsoluteScale) / baseScaleRef.current;
      distanceScaleRef.current = Math.max(0.5, Math.min(2.0, absoluteClampedScale));
    } else {
      distanceScaleRef.current = 1.0;
    }

    // Apply combined scale (base scale * distance scale * pulse)
    const scalePulse = 1.0 + (pulse * 0.05); // 0-5% scale variation
    const finalScale = baseScaleRef.current * distanceScaleRef.current * scalePulse;
    meshRef.current.scale.setScalar(finalScale);

    // Color transition (Req 16.4)
    if (isTransitioningRef.current) {
      // Interpolate from initial color to cyan
      currentColorRef.current.lerpColors(
        initialColor,
        targetColorRef.current,
        transitionProgressRef.current
      );
      
      // Update material color
      if (meshRef.current.material && 'color' in meshRef.current.material) {
        (meshRef.current.material as any).color.copy(currentColorRef.current);
      }
      
      // Fade out opacity during transition (Req 16.5)
      const fadeOutOpacity = intensity * (1 - transitionProgressRef.current * 0.5);
      if (meshRef.current.material && 'opacity' in meshRef.current.material) {
        (meshRef.current.material as any).opacity = fadeOutOpacity;
      }
    } else {
      // Normal pulsing opacity
      if (meshRef.current.material && 'opacity' in meshRef.current.material) {
        (meshRef.current.material as any).opacity = intensity;
      }
    }
  });

  if (!visible) return null;

  return (
    <mesh ref={meshRef}>
      {/* Ring geometry - slightly larger than the body */}
      <ringGeometry args={[
        scale * 1.1,  // Inner radius
        scale * 1.15, // Outer radius
        64            // Segments for smooth circle
      ]} />
      
      {/* Material with transparency and additive blending */}
      <meshBasicMaterial
        color={currentColorRef.current}
        transparent
        opacity={pulseIntensityMax}
        depthWrite={false}
        blending={2} // AdditiveBlending
      />
    </mesh>
  );
};

export default HighlightGeometry;
