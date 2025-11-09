import { ParticleSystem } from './ParticleSystem';
import { NavigationNodeConfig } from '../../config/navigationNodes';

/**
 * Props for node-specific particle systems
 */
export interface NodeParticlesProps {
  node: NavigationNodeConfig;
  enabled?: boolean;
}

/**
 * Particle system for Create Model node
 * 100-200 small particles orbiting the circle
 * Colors: purple, blue gradient
 * Slow orbit behavior
 * Requirements: 6.1
 */
export function CreateModelParticles({ node, enabled = true }: NodeParticlesProps) {
  return (
    <ParticleSystem
      count={150}
      distribution="orbital"
      radius={node.circleRadius + 10}  // Orbit slightly outside the circle
      size={0.8}
      color={['#B24BF3', '#7B2FFF', '#00D9FF']}  // Purple to blue gradient
      opacity={0.6}
      animation="orbit"
      speed={0.15}  // Slow orbit
      centerPosition={node.position}
      enabled={enabled}
    />
  );
}

/**
 * Particle system for Past Models node
 * 100-200 small particles orbiting the circle
 * Amber/gold color
 * Slow orbit behavior
 * Requirements: 6.2
 */
export function PastModelsParticles({ node, enabled = true }: NodeParticlesProps) {
  return (
    <ParticleSystem
      count={180}
      distribution="orbital"
      radius={node.circleRadius + 12}  // Orbit slightly outside the circle
      size={0.7}
      color={['#FFB84D', '#FFA726', '#FF8A00']}  // Amber to gold gradient
      opacity={0.5}
      animation="orbit"
      speed={0.12}  // Slower orbit
      centerPosition={node.position}
      enabled={enabled}
    />
  );
}

/**
 * Particle system for Info node
 * 100-200 small particles orbiting the circle
 * Cyan color
 * Slow orbit behavior
 * Requirements: 6.3
 */
export function InfoParticles({ node, enabled = true }: NodeParticlesProps) {
  return (
    <ParticleSystem
      count={120}
      distribution="orbital"
      radius={node.circleRadius + 8}  // Orbit slightly outside the circle
      size={0.9}
      color={['#00D9FF', '#4DD0E1', '#00BCD4']}  // Cyan gradient
      opacity={0.7}
      animation="orbit"
      speed={0.18}  // Slightly faster orbit
      centerPosition={node.position}
      enabled={enabled}
    />
  );
}

/**
 * Combined particle system that renders particles for a specific node type
 * This component can be easily toggled on/off for optional particle effects
 */
export function NavigationNodeParticles({ node, enabled = true }: NodeParticlesProps) {
  if (!enabled) return null;
  
  switch (node.type) {
    case 'create':
      return <CreateModelParticles node={node} enabled={enabled} />;
    case 'history':
      return <PastModelsParticles node={node} enabled={enabled} />;
    case 'info':
      return <InfoParticles node={node} enabled={enabled} />;
    default:
      return null;
  }
}
