# Custom Hooks

React hooks for 3D interactions and state management.

## useInteractionManager

Manages raycasting and user input detection for celestial bodies.

### Features
- Mouse and touch input detection
- Raycasting for object intersection
- Hover event emission with debouncing (100ms)
- Click event emission
- Enabled/disabled state management
- Mobile touch support

### Usage

```tsx
import { useThree } from '@react-three/fiber';
import { useInteractionManager } from '../hooks/useInteractionManager';

function MyScene() {
  const { camera, gl } = useThree();
  const [celestialBodies, setCelestialBodies] = useState<Object3D[]>([]);
  
  const {
    hoveredObjectId,
    clickedObjectId,
    isHovering,
    clearHover,
    clearClick,
  } = useInteractionManager({
    camera,
    domElement: gl.domElement,
    interactiveObjects: celestialBodies,
    enabled: true,
    hoverDebounceMs: 100,
  });
  
  // React to hover changes
  useEffect(() => {
    if (hoveredObjectId) {
      console.log('Hovering over:', hoveredObjectId);
    }
  }, [hoveredObjectId]);
  
  // React to click events
  useEffect(() => {
    if (clickedObjectId) {
      console.log('Clicked on:', clickedObjectId);
      // Initiate camera flight, etc.
    }
  }, [clickedObjectId]);
  
  return (
    // ... your scene components
  );
}
```

### Configuration

```typescript
interface InteractionManagerConfig {
  camera: Camera | null;              // Three.js camera
  domElement: HTMLElement | null;     // Canvas DOM element
  interactiveObjects: Object3D[];     // Array of objects to raycast against
  enabled?: boolean;                  // Enable/disable interactions (default: true)
  hoverDebounceMs?: number;           // Hover debounce delay (default: 100ms)
}
```

### Return Values

```typescript
interface InteractionManagerReturn {
  hoveredObjectId: string | null;     // ID of currently hovered object
  clickedObjectId: string | null;     // ID of clicked object (cleared after 100ms)
  isHovering: boolean;                // Whether any object is hovered
  clearHover: () => void;             // Manually clear hover state
  clearClick: () => void;             // Manually clear click state
}
```

### Object Identification

The hook identifies objects by checking:
1. `object.userData.id` - Custom ID set on the object
2. `object.name` - Object name matching celestial body IDs

Make sure to set one of these on your interactive objects:

```tsx
<mesh
  name="create-model"
  userData={{ id: 'create-model' }}
  // ... other props
>
```

### Touch Support

The hook automatically handles touch events for mobile devices:
- Touch start: Triggers hover state
- Touch end: Triggers click event if object was hovered

### Requirements Satisfied

- **2.1**: Highlight objects on hover within 100ms
- **2.2**: Display UI overlay with section name on hover
- **2.3**: Initiate camera flight on click
- **3.5**: Prevent navigation during transitions (via enabled prop)
- **15.4**: Support touch input for mobile devices

### Notes

- Hover events are debounced by 100ms to prevent excessive updates
- Click events are automatically cleared after 100ms to allow consumers to react
- The hook cleans up all event listeners on unmount
- Raycasting is performed recursively through object hierarchies
