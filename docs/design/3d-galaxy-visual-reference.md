# 3D Galaxy Homepage: Visual Reference Guide

## Color Palette & Visual Language

### Space Background
```
Deep Space: #0B0F14 (ink)
Panel: #0F141B
Card: #121925
Subtle: #0D1218
```

### Planet Colors
```
Create Model Planet:
  Base: #38BDF8 (sky-400)
  Core: #0EA5E9 (sky-500)
  Glow: rgba(56, 189, 248, 0.5)

Past Models Planet:
  Base: #F59E0B (amber-500)
  Core: #D97706 (amber-600)
  Glow: rgba(245, 158, 11, 0.5)

Info Planet:
  Base: #6366F1 (indigo-500)
  Core: #4F46E5 (indigo-600)
  Glow: rgba(99, 102, 241, 0.5)
```

### Text Colors
```
Primary: #E6EDF3
Secondary: #B8C2CC
Muted: #7C8794
Accent: #38BDF8
```

### Orbital Trails
```
Create Model Trail: rgba(56, 189, 248, 0.2)
Past Models Trail: rgba(245, 158, 11, 0.2)
Info Trail: rgba(99, 102, 241, 0.2)
```

---

## Scene Layout (Top View)

```
                    [Past Models]
                         ●
                         |
                         |
    [Create Model] ●-----●-----● [Info]
                         |
                         |
                    [Home View]
                    (Camera)
```

### 3D Coordinates

**Create Model Planet:**
- Position: `(-8, 2, 0)`
- Size: 1.5 units
- Orbit: 8 units radius

**Past Models Planet:**
- Position: `(8, 2, 0)`
- Size: 1.2 units
- Orbit: 8 units radius

**Info Planet:**
- Position: `(0, -4, 0)`
- Size: 1.0 units
- Orbit: 4 units radius

**Default Camera:**
- Position: `(0, 0, 15)`
- Target: `(0, 0, 0)`
- FOV: 50 degrees

---

## Camera Positions

### Home View
```
Position: (0, 0, 15)
Target: (0, 0, 0)
FOV: 50°
```

### Create Model Focus
```
Position: (-8, 2, 8)
Target: (-8, 2, 0)
FOV: 50°
```

### Past Models Focus
```
Position: (8, 2, 8)
Target: (8, 2, 0)
FOV: 50°
```

### Info Focus
```
Position: (0, -4, 10)
Target: (0, -4, 0)
FOV: 50°
```

---

## Animation Timings

### Camera Transitions
- **Duration:** 2.5 seconds
- **Easing:** ease-in-out (cubic bezier)
- **Delay:** 0ms

### Planet Rotations
- **Create Model:** 1 rotation per 20 seconds
- **Past Models:** 1 rotation per 15 seconds
- **Info:** 1 rotation per 30 seconds

### Orbital Motion
- **Create Model:** 0.5x speed (slow, majestic)
- **Past Models:** 0.7x speed (slightly faster)
- **Info:** 0.3x speed (slowest, contemplative)

### UI Overlays
- **Fade In:** 0.5 seconds
- **Fade Out:** 0.3 seconds
- **Delay:** 0.2 seconds after camera arrives

### Hover Effects
- **Scale Up:** 1.1x
- **Duration:** 0.2 seconds
- **Easing:** ease-out

### Glow Intensity
- **Default:** 0.2
- **Hover:** 0.4
- **Focused:** 0.5

---

## Post-Processing Settings

### Bloom
```
Intensity: 0.8
Threshold: 0.6
Radius: 4.0
```

### Depth of Field
```
Focus Distance: Based on camera target
Bokeh Size: 2.0
Height: 480px
```

### Vignette
```
Intensity: 0.3
Radius: 0.8
```

### Chromatic Aberration
```
Intensity: 0.1 (very subtle)
```

### Grain
```
Intensity: 0.05 (minimal)
```

---

## Typography Specifications

### Planet Labels
```
Font: Plus Jakarta Sans
Weight: 600
Size: 0.5 units (3D space)
Color: #E6EDF3
Position: 2 units above planet
```

### Descriptions
```
Font: Inter
Weight: 400
Size: 0.3 units (3D space)
Color: rgba(230, 237, 243, 0.7)
Position: Below label
```

### UI Overlay Title
```
Font: Plus Jakarta Sans
Weight: 600
Size: 28px (2D overlay)
Color: #E6EDF3
```

### UI Overlay Description
```
Font: Inter
Weight: 400
Size: 16px (2D overlay)
Color: rgba(230, 237, 243, 0.7)
```

---

## Particle Systems

### Create Model Planet
- **Count:** 50-100 particles
- **Color:** #38BDF8
- **Size:** 0.1-0.2 units
- **Behavior:** Flow toward planet
- **Speed:** 0.5 units/second

### Past Models Planet
- **Count:** 30-50 particles
- **Color:** #F59E0B
- **Size:** 0.1-0.15 units
- **Behavior:** Orbit in rings
- **Speed:** 0.3 units/second

### Info Planet
- **Count:** 20-30 particles
- **Color:** #6366F1
- **Size:** 0.08-0.12 units
- **Behavior:** Gentle cloud around planet
- **Speed:** 0.2 units/second

### Starfield
- **Count:** 200-300 stars
- **Color:** #ffffff
- **Size:** 0.5-2px
- **Opacity:** 0.1-0.3 (depth-based)
- **Twinkle:** 2-4 second cycle

---

## Lighting Setup

### Ambient Light
```
Color: #ffffff
Intensity: 0.3
Direction: Top-left
```

### Point Lights (Per Planet)
```
Create Model:
  Color: #38BDF8
  Intensity: 1.5 (focused), 1.0 (default)
  Distance: 4.5 units (3x planet radius)

Past Models:
  Color: #F59E0B
  Intensity: 1.2 (focused), 0.8 (default)
  Distance: 3.6 units (3x planet radius)

Info:
  Color: #6366F1
  Intensity: 1.0 (focused), 0.6 (default)
  Distance: 3.0 units (3x planet radius)
```

### Rim Lighting
```
Color: Planet color
Intensity: 0.3
Angle: 45° from camera
```

---

## Interaction States

### Default State
- Planets: Normal size, 0.2 glow
- Labels: Visible
- Trails: Dim (0.1 opacity)
- Camera: Home position

### Hover State
- Planet: 1.1x scale, 0.4 glow
- Label: Brighten
- Description: Fade in
- Trail: Brighten (0.3 opacity)

### Focused State
- Planet: Normal size, 0.5 glow, gentle pulse
- Background planets: Fade to 0.3 opacity
- UI Overlay: Fade in
- Camera: Focused on planet

### Transition State
- Camera: Moving along bezier curve
- Previous UI: Fading out
- New UI: Fading in
- Planets: Subtle fade during transition

---

## Performance Targets

### Desktop (High-End)
- **FPS:** 60fps
- **Resolution:** 1920x1080
- **Particles:** 200-300
- **Post-Processing:** Full quality

### Desktop (Mid-Range)
- **FPS:** 45-60fps
- **Resolution:** 1920x1080
- **Particles:** 150-200
- **Post-Processing:** Medium quality

### Mobile (High-End)
- **FPS:** 30-45fps
- **Resolution:** 1080x1920
- **Particles:** 100-150
- **Post-Processing:** Low quality

### Mobile (Mid-Range)
- **FPS:** 30fps minimum
- **Resolution:** 720x1280
- **Particles:** 50-100
- **Post-Processing:** Minimal

---

## Fallback Mode

### 2D Static Image
- **Format:** SVG or high-res PNG
- **Style:** Same color palette
- **Animation:** CSS keyframes for subtle movement
- **Navigation:** Same click interactions
- **Performance:** < 100KB image size

### CSS Animation
- **Planets:** CSS transforms (scale, rotate)
- **Trails:** SVG paths with stroke-dasharray
- **Stars:** CSS background with animation
- **Transitions:** CSS transitions (2.5s ease-in-out)

---

## Accessibility Considerations

### Keyboard Navigation
- **Tab:** Cycle through planets
- **Enter:** Select planet
- **Escape:** Return to home
- **Arrow Keys:** Move camera (optional)

### Screen Reader
- **Labels:** "Create Model planet, click to start training"
- **State:** "Camera focused on Create Model planet"
- **Actions:** "Press Enter to navigate"

### Motion Preferences
- **Reduced Motion:** Disable auto-rotation
- **Static Fallback:** 2D image with CSS
- **No Animations:** Instant transitions

### Color Contrast
- **Labels:** WCAG AA compliant
- **UI Overlays:** High contrast backgrounds
- **Focus Indicators:** Visible borders/outlines

---

## Visual Metaphor Mapping

| Galaxy Element | ML Platform Element | Visual Representation |
|---------------|---------------------|----------------------|
| Galaxy | AI Ecosystem | Entire 3D space |
| Planets | Platform Sections | Celestial bodies |
| Orbital Trails | Data Flow | Connecting lines |
| Stars | Data Points | Twinkling dots |
| Camera Movement | User Journey | Smooth transitions |
| Particle Streams | Data Processing | Flowing particles |
| Planet Glows | Active States | Brightness/intensity |
| Orbital Mechanics | Workflow Connections | Physics-based motion |

---

*This visual reference guide provides specific values and settings for implementing the 3D galaxy homepage experience.*


