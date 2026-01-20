# Theme Visual Guide

## 🎨 Color Palette Comparison

### 🌙 Dark Mode (AMOLED Black)

```
┌─────────────────────────────────────────┐
│  AMOLED BLACK THEME                     │
│  Purple & Pink Accents                  │
├─────────────────────────────────────────┤
│                                         │
│  Background Colors:                     │
│  ████ Primary:   #000000 (Pure Black)  │
│  ████ Secondary: #0a0a0a (Neutral-950) │
│  ████ Tertiary:  #171717 (Neutral-900) │
│                                         │
│  Accent Colors:                         │
│  ████ Purple:    #a855f7               │
│  ████ Pink:      #ec4899               │
│  ████ Gradient:  Purple → Pink         │
│                                         │
│  Text Colors:                           │
│  ████ Primary:   #ffffff (White)       │
│  ████ Secondary: #d4d4d4 (Neutral-300) │
│  ████ Muted:     #737373 (Neutral-500) │
│                                         │
│  Border Colors:                         │
│  ████ Default:   #262626 (Neutral-800) │
│  ████ Hover:     #404040 (Neutral-700) │
│                                         │
└─────────────────────────────────────────┘
```

**Use Cases:**
- ⚡ AMOLED displays (battery saving)
- 🌙 Night/low-light environments
- 🎮 Immersive, focused experiences
- 🎨 Modern, sophisticated aesthetic

---

### ☀️ Light Mode (Green & Lilac)

```
┌─────────────────────────────────────────┐
│  LIGHT THEME                            │
│  Green & Lilac Accents                  │
├─────────────────────────────────────────┤
│                                         │
│  Background Colors:                     │
│  ░░░░ Primary:   #f8fafc (Slate-50)    │
│  ░░░░ Secondary: #ffffff (White)       │
│  ░░░░ Tertiary:  #f1f5f9 (Slate-100)   │
│                                         │
│  Accent Colors:                         │
│  ████ Emerald:   #10b981               │
│  ████ Teal:      #14b8a6               │
│  ████ Lilac:     #c084fc               │
│  ████ Gradient:  Emerald → Teal        │
│                                         │
│  Text Colors:                           │
│  ████ Primary:   #0f172a (Slate-900)   │
│  ████ Secondary: #334155 (Slate-700)   │
│  ████ Muted:     #64748b (Slate-500)   │
│                                         │
│  Border Colors:                         │
│  ░░░░ Default:   #e2e8f0 (Slate-200)   │
│  ░░░░ Hover:     #cbd5e1 (Slate-300)   │
│                                         │
└─────────────────────────────────────────┘
```

**Use Cases:**
- ☀️ Bright environments/daylight
- 📖 Reading-focused tasks
- 🧘 Calming, mindfulness-aligned design
- 💼 Professional presentations

---

## 🎯 Component Examples

### Navigation Sidebar

**Dark Mode:**
```
┌────────────────────┐
│ 🌸 Mindfulness     │ ← Purple/Pink gradient
├────────────────────┤
│ 📊 Dashboard       │ ← Neutral-400 text
│ ▶️  Live Pilot     │ ← Active: Purple/Pink gradient bg
│ 👤 User Manager    │
│ 🧪 Simulation Lab  │
├────────────────────┤
│ ☀️  Light Mode     │ ← Toggle button
├────────────────────┤
│ v2.0.0            │ ← Neutral-600 text
└────────────────────┘
Background: #0a0a0a (Neutral-950)
Border: #262626 (Neutral-800)
```

**Light Mode:**
```
┌────────────────────┐
│ 🌿 Mindfulness     │ ← Emerald/Teal gradient
├────────────────────┤
│ 📊 Dashboard       │ ← Slate-600 text
│ ▶️  Live Pilot     │ ← Active: Emerald/Teal gradient bg
│ 👤 User Manager    │
│ 🧪 Simulation Lab  │
├────────────────────┤
│ 🌙 Dark Mode       │ ← Toggle button
├────────────────────┤
│ v2.0.0            │ ← Slate-400 text
└────────────────────┘
Background: #ffffff (White)
Border: #e2e8f0 (Slate-200)
```

---

### Button States

**Dark Mode Buttons:**
```
Normal:   ┌──────────────┐
          │ Trigger Drift│  ← Purple/Pink gradient
          └──────────────┘  Shadow: Purple-500/30
          
Hover:    ┌──────────────┐
          │ Trigger Drift│  ← Lighter gradient
          └──────────────┘  Shadow: Purple-500/40

Disabled: ┌──────────────┐
          │ Loading...   │  ← 50% opacity
          └──────────────┘
```

**Light Mode Buttons:**
```
Normal:   ┌──────────────┐
          │ Trigger Drift│  ← Emerald/Teal gradient
          └──────────────┘  Shadow: Emerald-500/20
          
Hover:    ┌──────────────┐
          │ Trigger Drift│  ← Lighter gradient
          └──────────────┘  Shadow: Emerald-500/30

Disabled: ┌──────────────┐
          │ Loading...   │  ← 50% opacity
          └──────────────┘
```

---

### Cards & Panels

**Dark Mode Card:**
```
┌─────────────────────────────────┐
│ 🆕 New Persona                 │ ← Purple-400 icon
├─────────────────────────────────┤
│                                 │
│ Name: [____________]            │ ← Neutral-900 input bg
│                                 │
│ Stress:  ▓▓▓▓▓░░░░░ 50%       │ ← Pink-500 bar
│ Energy:  ▓▓▓▓▓▓▓░░░ 70%       │ ← Purple-500 bar
│                                 │
│ [  Create User  ]              │ ← Purple/Pink gradient
└─────────────────────────────────┘
Background: #0a0a0a (Neutral-950/50)
Border: #262626 (Neutral-800)
```

**Light Mode Card:**
```
┌─────────────────────────────────┐
│ 🆕 New Persona                 │ ← Emerald-600 icon
├─────────────────────────────────┤
│                                 │
│ Name: [____________]            │ ← Slate-50 input bg
│                                 │
│ Stress:  ▓▓▓▓▓░░░░░ 50%       │ ← Rose-500 bar
│ Energy:  ▓▓▓▓▓▓▓░░░ 70%       │ ← Amber-500 bar
│                                 │
│ [  Create User  ]              │ ← Emerald/Teal gradient
└─────────────────────────────────┘
Background: #ffffff (White)
Border: #e2e8f0 (Slate-200)
Shadow: Subtle elevation
```

---

### Charts & Visualizations

**Dark Mode Chart:**
```
Daily Completion Rate
│
100% ┤     ▓▓▓
     │   ▓▓▓▓▓▓▓  ▓▓▓
 75% ┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
     │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 50% ┼─────────────────── (Reference line: #525252)
     │
  0% └───────────────────
      1    15    30 (days)

Bars: Purple → Pink gradient
Grid: #262626
Axis: #737373
Background: #0a0a0a
```

**Light Mode Chart:**
```
Daily Completion Rate
│
100% ┤     ▓▓▓
     │   ▓▓▓▓▓▓▓  ▓▓▓
 75% ┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
     │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 50% ┼─────────────────── (Reference line: #94a3b8)
     │
  0% └───────────────────
      1    15    30 (days)

Bars: Emerald → Teal gradient
Grid: #e2e8f0
Axis: #94a3b8
Background: #ffffff
```

---

## 🎭 Transition Effects

### Theme Switch Animation
```
Frame 1 (0ms):     Current theme visible
                   ↓
Frame 2 (150ms):   Colors transitioning (50%)
                   ↓
Frame 3 (300ms):   New theme fully applied
                   ✓ Complete
```

**Transition Properties:**
- Duration: 300ms
- Easing: ease-in-out
- Properties: background-color, color, border-color
- Applied via: `.theme-transition` utility class

---

## 📱 Responsive Behavior

### Mobile (< 768px)
- Full-width cards
- Stacked navigation
- Reduced padding
- Same color schemes

### Tablet (768px - 1024px)
- Two-column grids
- Compact sidebar
- Optimized charts
- Same color schemes

### Desktop (> 1024px)
- Multi-column layouts
- Full sidebar
- Expanded charts
- Same color schemes

---

## ♿ Accessibility

### Contrast Ratios (WCAG AA Compliant)

**Dark Mode:**
- White on Black: 21:1 ✅
- Purple-400 on Black: 8.5:1 ✅
- Neutral-300 on Black: 12.6:1 ✅

**Light Mode:**
- Slate-900 on White: 18.2:1 ✅
- Emerald-600 on White: 4.5:1 ✅
- Slate-700 on White: 10.1:1 ✅

### Focus Indicators
- Dark Mode: Purple-500 ring (2px)
- Light Mode: Emerald-500 ring (2px)

---

## 💡 Usage Tips

1. **Battery Saving**: Use dark mode on mobile devices with AMOLED screens
2. **Eye Comfort**: Switch to light mode in bright environments
3. **Preference**: Theme choice persists across sessions
4. **Accessibility**: Both themes meet WCAG AA standards
5. **Transitions**: Smooth 300ms animations for comfortable switching

---

## 🎨 Design Philosophy

**Dark Mode:**
- **Energy**: Bold, vibrant, energetic (Purple/Pink)
- **Mood**: Focused, immersive, modern
- **Psychology**: Reduces overstimulation, promotes focus

**Light Mode:**
- **Energy**: Calm, balanced, refreshing (Green/Teal)
- **Mood**: Peaceful, mindful, professional
- **Psychology**: Aligns with nature, promotes clarity

Both themes designed to support the mindfulness mission while maintaining modern aesthetics and excellent usability.

---

*For technical implementation details, see `THEME_SYSTEM.md`*
