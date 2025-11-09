import React from 'react';
import { GalaxyScene } from './scene/GalaxyScene';
import { LightingRig } from './scene/LightingRig';
import { NavigationNode } from './navigation/NavigationNode';
import { ProceduralStarField } from './particles/ProceduralStarField';
import { ParticleSystemDemo } from './particles/ParticleSystemDemo';
import { TrainingVisualization } from './effects/TrainingVisualization';
// import { ClickTestCube } from './debug/ClickTestCube'; // Removed - was blocking clicks
import { NAVIGATION_NODES } from '../config/navigationNodes';
import { useTravelController } from '../hooks/useTravelController';
import { useFocusedBodyId, useNavigationStore } from '../store/navigationStore';
import { 
  SectionOverlay, 
  FileUploadOverlay, 
  HistoryBrowserOverlay, 
  InfoOverlay,
  NavigationHUD 
} from './ui';

/**
 * GalaxyContent Component
 * Inner component that uses R3F hooks (must be inside Canvas)
 * Handles travel controller and navigation logic
 */
const GalaxyContent: React.FC = () => {
  const { travelTo, returnToOverview } = useTravelController();
  const focusedBodyId = useFocusedBodyId();
  const { isTraining, trainingProgress } = useNavigationStore();
  
  // Expose returnToOverview to window for overlay close button
  React.useEffect(() => {
    (window as any).__galaxyReturnToOverview = returnToOverview;
    return () => {
      delete (window as any).__galaxyReturnToOverview;
    };
  }, [returnToOverview]);

  const handleBodyClick = (id: string) => {
    console.log(`Clicked on celestial body: ${id}`);
    // Initiate travel to the clicked body
    travelTo(id);
  };

  const handleBodyHover = (id: string, hovered: boolean) => {
    console.log(`Hover ${hovered ? 'enter' : 'exit'} on: ${id}`);
  };

  // Handle ESC key to return to overview
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && focusedBodyId) {
        returnToOverview();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [focusedBodyId, returnToOverview]);

  return (
    <>
      {/* Three-point lighting setup */}
      <LightingRig />

      {/* Procedural star field with 7000+ stars and haze particles */}
      <ProceduralStarField />

      {/* Particle systems for navigation nodes (Task 10) */}
      <ParticleSystemDemo 
        enabled={true}
        enableCreateModel={true}
        enablePastModels={true}
        enableInfo={true}
      />

      {/* Render all three navigation nodes with focus state (Req 6.4) and training state (Req 11.3) */}
      {NAVIGATION_NODES.map((nodeConfig) => (
        <NavigationNode
          key={nodeConfig.id}
          config={nodeConfig}
          onClick={handleBodyClick}
          onHover={handleBodyHover}
          isFocused={focusedBodyId === nodeConfig.id}
          isTraining={nodeConfig.id === 'create-model' && isTraining}
          trainingProgress={nodeConfig.id === 'create-model' ? trainingProgress : 0}
        />
      ))}

      {/* Training visualization effects (Task 12) */}
      <TrainingVisualization />
      
      {/* DEBUG: Test cube to verify clicks work - REMOVED, was blocking clicks */}
      {/* <ClickTestCube /> */}
    </>
  );
};

/**
 * GalaxyDemo Component
 * Demonstrates the complete 3D galaxy scene with procedural star field and UI overlays
 * 
 * This component combines:
 * - GalaxyScene (canvas, camera, fog)
 * - LightingRig (three-point lighting)
 * - ProceduralStarField (7000+ stars with haze)
 * - NavigationNode components (3 transparent circles with icons)
 * - Travel controller for camera navigation
 * - Focus state management for body scaling (Req 6.4)
 * - UI overlays for each section (Task 11)
 * - NavigationHUD for persistent navigation hints
 */
export const GalaxyDemo: React.FC = () => {
  const focusedBodyId = useFocusedBodyId();
  const transitionPhase = useNavigationStore((state) => state.transitionPhase);

  const handleSceneReady = () => {
    console.log('Galaxy scene is ready!');
  };
  
  const handleCloseOverlay = () => {
    // Call the returnToOverview function exposed by GalaxyContent
    if ((window as any).__galaxyReturnToOverview) {
      (window as any).__galaxyReturnToOverview();
    }
  };

  // Determine which overlay to show based on focused body
  // Only show overlay when travel is complete (phase is 'focused')
  const renderOverlay = () => {
    if (!focusedBodyId || transitionPhase !== 'focused') return null;

    switch (focusedBodyId) {
      case 'create-model':
        return (
          <SectionOverlay onClose={handleCloseOverlay}>
            <FileUploadOverlay visible={true} />
          </SectionOverlay>
        );
      case 'past-models':
        return (
          <SectionOverlay onClose={handleCloseOverlay}>
            <HistoryBrowserOverlay visible={true} />
          </SectionOverlay>
        );
      case 'info':
        return (
          <SectionOverlay onClose={handleCloseOverlay}>
            <InfoOverlay visible={true} />
          </SectionOverlay>
        );
      default:
        return null;
    }
  };

  return (
    <>
      {/* 3D Scene */}
      <GalaxyScene onSceneReady={handleSceneReady} performanceMode="high">
        <GalaxyContent />
      </GalaxyScene>

      {/* UI Overlays */}
      {renderOverlay()}

      {/* Navigation HUD */}
      <NavigationHUD showControls={true} />
    </>
  );
};

export default GalaxyDemo;
