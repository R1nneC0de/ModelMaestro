import { NavigationNodeParticles } from './NodeParticles';
import { NAVIGATION_NODES } from '../../config/navigationNodes';

/**
 * Demo component showing how to integrate particle systems with navigation nodes
 * This can be added to GalaxyScene to enable optional particle effects
 */
export interface ParticleSystemDemoProps {
  enabled?: boolean;
  enableCreateModel?: boolean;
  enablePastModels?: boolean;
  enableInfo?: boolean;
}

/**
 * Renders particle systems for all navigation nodes
 * Individual node particles can be toggled on/off
 */
export function ParticleSystemDemo({
  enabled = true,
  enableCreateModel = true,
  enablePastModels = true,
  enableInfo = true,
}: ParticleSystemDemoProps) {
  if (!enabled) return null;
  
  return (
    <>
      {NAVIGATION_NODES.map(node => {
        // Determine if this specific node's particles should be enabled
        let nodeEnabled = true;
        
        switch (node.type) {
          case 'create':
            nodeEnabled = enableCreateModel;
            break;
          case 'history':
            nodeEnabled = enablePastModels;
            break;
          case 'info':
            nodeEnabled = enableInfo;
            break;
        }
        
        return (
          <NavigationNodeParticles
            key={`particles-${node.id}`}
            node={node}
            enabled={nodeEnabled}
          />
        );
      })}
    </>
  );
}

/**
 * Example usage in GalaxyScene:
 * 
 * import { ParticleSystemDemo } from './components/particles/ParticleSystemDemo';
 * 
 * function GalaxyScene() {
 *   return (
 *     <Canvas>
 *       {/* ... other scene components ... *\/}
 *       
 *       {/* Add particle systems - all enabled *\/}
 *       <ParticleSystemDemo enabled={true} />
 *       
 *       {/* Or with selective enabling *\/}
 *       <ParticleSystemDemo
 *         enabled={true}
 *         enableCreateModel={true}
 *         enablePastModels={false}
 *         enableInfo={true}
 *       />
 *     </Canvas>
 *   );
 * }
 */
