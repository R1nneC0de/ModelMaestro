import { create } from 'zustand';

export type CameraState = 'home' | 'create-model' | 'past-models' | 'info';

interface GalaxyState {
  cameraState: CameraState;
  hoveredPlanet: string | null;
  isTransitioning: boolean;
  setCameraState: (state: CameraState) => void;
  setHoveredPlanet: (planet: string | null) => void;
  setIsTransitioning: (transitioning: boolean) => void;
}

export const useGalaxyStore = create<GalaxyState>((set) => ({
  cameraState: 'home',
  hoveredPlanet: null,
  isTransitioning: false,
  setCameraState: (state) => {
    set({ cameraState: state, isTransitioning: true });
    setTimeout(() => set({ isTransitioning: false }), 2500);
  },
  setHoveredPlanet: (planet) => set({ hoveredPlanet: planet }),
  setIsTransitioning: (transitioning) => set({ isTransitioning: transitioning }),
}));


