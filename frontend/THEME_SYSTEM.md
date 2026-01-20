# Theme System Documentation

## Overview

The Mindfulness Prototype now features a beautiful, modern dual-theme system with seamless transitions between light and dark modes.

## Color Schemes

### 🌙 Dark Mode (AMOLED Black Theme)
- **Background**: Pure black (#000000) for AMOLED displays
- **Secondary**: Neutral-950 (#0a0a0a)
- **Accents**: Purple (#a855f7) and Pink (#ec4899) gradients
- **Text**: White with neutral gray variants
- **Shadows**: Purple/pink glows for depth

**Benefits:**
- True black saves battery on AMOLED screens
- Reduces eye strain in low-light environments
- Vibrant purple/pink accents provide excellent contrast
- Modern, sophisticated aesthetic

### ☀️ Light Mode (Green & Lilac Theme)
- **Background**: Slate-50 (#f8fafc) and white
- **Accents**: Emerald (#10b981) and Teal (#14b8a6) gradients
- **Secondary**: Lilac/Purple accents for variety
- **Text**: Slate-900 with lighter variants
- **Shadows**: Subtle emerald glows

**Benefits:**
- Excellent readability in bright environments
- Calming green/teal palette aligned with mindfulness theme
- Professional and clean appearance
- Reduced eye strain in daylight

## Features

### ✨ Key Capabilities

1. **Persistent Preferences**
   - Theme choice saved to `localStorage`
   - Automatically restored on page reload
   - Defaults to dark mode

2. **Smooth Transitions**
   - All color changes use CSS transitions (300ms)
   - No jarring switches between themes
   - Consistent animation timing across components

3. **Context-Based Architecture**
   - Centralized theme management via React Context
   - Single source of truth for theme state
   - Easy to extend with additional themes

4. **Comprehensive Coverage**
   - All UI components are theme-aware
   - Charts and visualizations adapt colors
   - Forms, buttons, cards, and navigation all themed

5. **Accessibility**
   - High contrast ratios in both modes
   - Consistent color semantics (success, error, warning)
   - Proper ARIA labels on theme toggle

## File Structure

```
frontend/src/
├── contexts/
│   └── ThemeContext.jsx          # Theme provider and hook
├── components/
│   ├── PilotTab.jsx              # Theme-aware pilot interface
│   ├── UserTab.jsx               # Theme-aware user management
│   └── SimulationTab.jsx         # Theme-aware simulation lab
├── App.jsx                       # Main app with theme toggle
├── main.jsx                      # ThemeProvider wrapper
├── index.css                     # Global styles + theme utilities
└── tailwind.config.js            # Custom color palette
```

## Usage

### Using the Theme Hook

```jsx
import { useTheme } from '../contexts/ThemeContext';

function MyComponent() {
  const { isDark, toggleTheme } = useTheme();
  
  return (
    <div className={isDark ? 'bg-black text-white' : 'bg-white text-slate-900'}>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </div>
  );
}
```

### Conditional Styling Pattern

```jsx
// Basic pattern
className={isDark ? 'dark-class' : 'light-class'}

// With gradients
className={isDark 
  ? 'bg-gradient-to-r from-purple-600 to-pink-600' 
  : 'bg-gradient-to-r from-emerald-500 to-teal-500'
}

// Complex conditionals
className={`base-classes ${
  isDark 
    ? 'bg-neutral-950 border-neutral-800 text-white' 
    : 'bg-white border-slate-200 text-slate-900'
}`}
```

### Utility Classes

```css
.theme-transition       /* Smooth color transitions */
.glass-dark            /* Dark glassmorphism effect */
.glass-light           /* Light glassmorphism effect */
.gradient-text-dark    /* Purple/pink gradient text */
.gradient-text-light   /* Emerald/teal gradient text */
```

## Color Palette Reference

### Dark Mode Colors
```js
{
  background: 'black (#000000)',
  surface: 'neutral-950 (#0a0a0a)',
  card: 'neutral-900 (#171717)',
  border: 'neutral-800 (#262626)',
  text: {
    primary: 'white (#ffffff)',
    secondary: 'neutral-300 (#d4d4d4)',
    muted: 'neutral-500 (#737373)'
  },
  accent: {
    purple: '#a855f7',
    pink: '#ec4899',
    gradient: 'from-purple-600 to-pink-600'
  }
}
```

### Light Mode Colors
```js
{
  background: 'slate-50 (#f8fafc)',
  surface: 'white (#ffffff)',
  card: 'slate-100 (#f1f5f9)',
  border: 'slate-200 (#e2e8f0)',
  text: {
    primary: 'slate-900 (#0f172a)',
    secondary: 'slate-700 (#334155)',
    muted: 'slate-500 (#64748b)'
  },
  accent: {
    emerald: '#10b981',
    teal: '#14b8a6',
    gradient: 'from-emerald-500 to-teal-500'
  }
}
```

## Extending the Theme

### Adding New Themes

1. Modify `ThemeContext.jsx` to support multiple themes:

```jsx
const [theme, setTheme] = useState('dark'); // 'dark', 'light', 'auto'

const themes = {
  dark: { /* dark theme config */ },
  light: { /* light theme config */ },
  auto: { /* system preference */ }
};
```

2. Update Tailwind config with new color scales

3. Add theme-specific styles to components

### System Preference Detection

To auto-detect user's system preference:

```jsx
useEffect(() => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  setIsDark(mediaQuery.matches);
  
  const handler = (e) => setIsDark(e.matches);
  mediaQuery.addEventListener('change', handler);
  return () => mediaQuery.removeEventListener('change', handler);
}, []);
```

## Performance Considerations

- **CSS Variables**: Consider moving to CSS custom properties for better performance
- **Lazy Loading**: Theme context loads immediately (necessary for initial render)
- **Transition Throttling**: All transitions limited to 300ms to prevent lag
- **LocalStorage**: Synchronous read on mount (fast, no async needed)

## Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Testing Checklist

- [ ] Theme toggle button works
- [ ] Theme persists on page reload
- [ ] All components render correctly in both modes
- [ ] No flash of unstyled content (FOUC)
- [ ] Charts update colors appropriately
- [ ] Forms maintain accessibility in both modes
- [ ] Transitions are smooth (no janky animations)
- [ ] LocalStorage saves/retrieves theme correctly

## Future Enhancements

1. **Auto Theme Scheduling**: Switch themes based on time of day
2. **Multiple Accent Colors**: Let users choose accent palette
3. **Contrast Modes**: High contrast variants for accessibility
4. **Custom Themes**: Allow users to create custom color schemes
5. **Theme Animations**: More sophisticated transition effects
6. **CSS Variables Migration**: Better performance with CSS custom properties

## Troubleshooting

**Theme doesn't persist:**
- Check localStorage permissions
- Verify ThemeProvider wraps entire app
- Check browser console for errors

**Colors not updating:**
- Ensure component imports `useTheme` hook
- Check if component is using conditional classes
- Verify Tailwind classes are not being purged

**Transitions are janky:**
- Reduce transition duration
- Use `will-change` CSS property sparingly
- Check for too many DOM elements updating at once

---

Built with ❤️ for mindfulness and productivity
