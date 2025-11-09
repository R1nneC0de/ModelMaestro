# UI Overlay Components

This directory contains all UI overlay components for the 3D Galaxy Homepage. These components provide context-sensitive interfaces that appear when users interact with navigation nodes in the 3D scene.

## Components Overview

### 1. SectionOverlay
**Purpose:** Base container for all section-specific overlays

**Features:**
- Smooth fade and slide animations (500ms entrance, 300ms exit)
- Backdrop with blur effect
- ESC key and backdrop click to close
- Accessible with ARIA attributes
- Responsive design

**Usage:**
```tsx
<SectionOverlay onClose={handleClose}>
  <YourContent />
</SectionOverlay>
```

---

### 2. FileUploadOverlay
**Purpose:** Create Model section - Upload datasets and start training

**Features:**
- Drag-and-drop file upload
- File validation (CSV, JSON, Excel, max 50MB)
- Training prompt input
- Upload progress indicator
- Error and success messages
- Integration with backend API

**Usage:**
```tsx
<SectionOverlay>
  <FileUploadOverlay visible={true} />
</SectionOverlay>
```

**API Integration:**
- Uses `useTraining()` hook
- Submits to `/api/v1/projects` endpoint
- Validates files using `utils/validators.ts`

---

### 3. HistoryBrowserOverlay
**Purpose:** Past Models section - Browse training history

**Features:**
- Grid layout of session cards
- Session status indicators (training, completed, failed)
- Click to view detailed session information
- Loading, error, and empty states
- Animated card entrance
- Progress bar for active training

**Usage:**
```tsx
<SectionOverlay>
  <HistoryBrowserOverlay visible={true} />
</SectionOverlay>
```

**API Integration:**
- Uses `useHistory()` hook for session list
- Uses `useSessionDetail()` hook for details
- Fetches from `/api/v1/projects` endpoint

---

### 4. InfoOverlay
**Purpose:** Information section - Platform documentation

**Features:**
- Platform description
- Step-by-step usage guide
- Key features grid
- Use case examples
- Responsive layout

**Usage:**
```tsx
<SectionOverlay>
  <InfoOverlay visible={true} />
</SectionOverlay>
```

**Content Sections:**
1. What is this?
2. How to Use (4 steps)
3. Key Features (6 features)
4. Use Case Examples (4 examples)

---

### 5. NavigationHUD
**Purpose:** Persistent heads-up display for navigation

**Features:**
- Current location display
- Navigation hints
- Loading state during transitions
- Keyboard shortcuts modal (toggle with '?')
- Screen reader announcements
- Always visible in top-left corner

**Usage:**
```tsx
<NavigationHUD showControls={true} />
```

**Keyboard Shortcuts:**
- `ESC` - Return to overview
- `Tab` - Cycle through nodes
- `Enter` - Select focused node
- `←` `→` - Navigate between nodes
- `1` `2` `3` - Quick access to sections
- `?` - Toggle shortcuts help
- `Space` - Pause/resume animation

---

## Integration Example

```tsx
import { 
  SectionOverlay, 
  FileUploadOverlay, 
  HistoryBrowserOverlay, 
  InfoOverlay,
  NavigationHUD 
} from './ui';
import { useFocusedBodyId } from '../../store/navigationStore';

function GalaxyDemo() {
  const focusedBodyId = useFocusedBodyId();

  const renderOverlay = () => {
    switch (focusedBodyId) {
      case 'create-model':
        return (
          <SectionOverlay>
            <FileUploadOverlay visible={true} />
          </SectionOverlay>
        );
      case 'past-models':
        return (
          <SectionOverlay>
            <HistoryBrowserOverlay visible={true} />
          </SectionOverlay>
        );
      case 'info':
        return (
          <SectionOverlay>
            <InfoOverlay visible={true} />
          </SectionOverlay>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <GalaxyScene>
        {/* 3D content */}
      </GalaxyScene>
      {renderOverlay()}
      <NavigationHUD showControls={true} />
    </>
  );
}
```

## Design System

### Colors
- **Background:** `#0F141B` (panel), `#0A0E14` (darker)
- **Borders:** `#1E2633` (stroke), `#2A3441` (lighter)
- **Text:** `#FFFFFF` (primary), `#B8BFC7` (secondary), `#7C8794` (muted)
- **Accent:** `#0EA5E9` (primary blue)
- **Success:** `#34A853` (green)
- **Warning:** `#FBBC04` (yellow)
- **Error:** `#EA4335` (red)

### Typography
- **Titles:** 28-32px, weight 600
- **Subtitles:** 16-18px, weight 400
- **Body:** 14-16px, weight 400
- **Captions:** 12-14px, weight 400

### Spacing
- **Section gaps:** 24-40px
- **Element gaps:** 12-16px
- **Padding:** 16-32px (responsive)

### Animations
- **Entrance:** 500ms ease-out
- **Exit:** 300ms ease-in
- **Hover:** 180ms ease-out
- **Spinner:** 1s linear infinite

## Accessibility

### Keyboard Navigation
All overlays support full keyboard navigation:
- Tab through interactive elements
- ESC to close overlays
- Enter to activate buttons
- Arrow keys for navigation (where applicable)

### Screen Reader Support
- ARIA labels on all interactive elements
- Live regions for state announcements
- Semantic HTML structure
- Role attributes (dialog, status, alert)

### Reduced Motion
All animations are disabled when `prefers-reduced-motion` is set:
```css
@media (prefers-reduced-motion: reduce) {
  .section-overlay.entering .section-overlay__container {
    animation: none;
  }
}
```

## Responsive Design

### Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### Mobile Optimizations
- Full-width overlays (95%)
- Reduced padding
- Stacked layouts
- Hidden navigation hints
- Larger touch targets

## State Management

All overlays integrate with the Zustand navigation store:

```typescript
import { 
  useFocusedBodyId, 
  useCurrentView, 
  useIsTransitioning 
} from '../../store/navigationStore';

// Determine which overlay to show
const focusedBodyId = useFocusedBodyId();

// Check if in overview or focused view
const currentView = useCurrentView();

// Show loading states during transitions
const isTransitioning = useIsTransitioning();
```

## Testing

### Manual Testing Checklist
- [ ] Click on each navigation node
- [ ] Verify animations are smooth
- [ ] Test ESC key to close
- [ ] Test backdrop click to close
- [ ] Upload a file
- [ ] View training history
- [ ] Read information
- [ ] Toggle keyboard shortcuts
- [ ] Test on mobile
- [ ] Test with keyboard only
- [ ] Test with screen reader

### Accessibility Testing
- [ ] Run axe DevTools audit
- [ ] Test with NVDA/JAWS
- [ ] Verify keyboard navigation
- [ ] Check color contrast (WCAG AA)
- [ ] Test focus indicators

## Performance

### Optimizations
- Conditional rendering (mount only when visible)
- CSS animations (GPU-accelerated)
- Efficient re-render prevention
- Lazy loading of session details

### Bundle Size
- Total CSS: ~8KB (minified)
- Total JS: ~15KB (minified)
- No additional dependencies

## Browser Support
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support

## Future Enhancements
1. Training progress visualization
2. Data particle animation on upload
3. Connection path visualization
4. Training completion animation
5. Model download functionality
6. Session filtering/sorting
7. Search functionality
8. Pagination for large lists
