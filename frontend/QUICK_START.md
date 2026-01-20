# Quick Start Guide - Frontend Development

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

### 3. Open Browser
Navigate to `http://localhost:5173`

---

## 🎨 Theme System Quick Reference

### Using the Theme Hook
```jsx
import { useTheme } from '../contexts/ThemeContext';

function MyComponent() {
  const { isDark, toggleTheme } = useTheme();
  
  return (
    <div className={isDark ? 'bg-black' : 'bg-white'}>
      {/* Your content */}
    </div>
  );
}
```

### Common Patterns

#### Background Colors
```jsx
className={isDark 
  ? 'bg-neutral-950 border-neutral-800' 
  : 'bg-white border-slate-200'}
```

#### Text Colors
```jsx
className={isDark 
  ? 'text-white' 
  : 'text-slate-900'}
```

#### Accent Gradients
```jsx
className={isDark 
  ? 'bg-gradient-to-r from-purple-600 to-pink-600' 
  : 'bg-gradient-to-r from-emerald-500 to-teal-500'}
```

---

## 📁 File Structure

```
src/
├── contexts/
│   └── ThemeContext.jsx       # Theme state & logic
├── components/
│   ├── PilotTab.jsx          # Live intervention simulator
│   ├── UserTab.jsx           # User persona manager
│   └── SimulationTab.jsx     # 30-day simulation runner
├── App.jsx                    # Main app shell
├── main.jsx                   # App entry point
├── index.css                  # Global styles + theme utilities
├── api.js                     # API client configuration
└── assets/                    # Static assets
```

---

## 🎯 Component Checklist

When creating a new component:

- [ ] Import `useTheme` hook
- [ ] Destructure `isDark` from theme
- [ ] Apply conditional styling for both themes
- [ ] Use `theme-transition` class for smooth changes
- [ ] Test in both dark and light modes
- [ ] Verify contrast ratios for accessibility
- [ ] Add proper focus states

---

## 🎨 Color Reference

### Dark Mode
```jsx
// Backgrounds
'bg-black'           // Pure black (#000000)
'bg-neutral-950'     // Near black (#0a0a0a)
'bg-neutral-900'     // Dark gray (#171717)

// Accents
'text-purple-400'    // Primary accent
'text-pink-400'      // Secondary accent
'from-purple-600 to-pink-600'  // Gradient

// Text
'text-white'         // Primary
'text-neutral-300'   // Secondary
'text-neutral-500'   // Muted
```

### Light Mode
```jsx
// Backgrounds
'bg-slate-50'        // Very light gray (#f8fafc)
'bg-white'           // Pure white (#ffffff)
'bg-slate-100'       // Light gray (#f1f5f9)

// Accents
'text-emerald-600'   // Primary accent
'text-teal-500'      // Secondary accent
'from-emerald-500 to-teal-500'  // Gradient

// Text
'text-slate-900'     // Primary
'text-slate-700'     // Secondary
'text-slate-500'     // Muted
```

---

## 🛠️ Utility Classes

```css
.theme-transition       /* Smooth color transitions (300ms) */
.glass-dark            /* Dark glassmorphism effect */
.glass-light           /* Light glassmorphism effect */
.gradient-text-dark    /* Purple/pink gradient text */
.gradient-text-light   /* Emerald/teal gradient text */
```

---

## 📦 Available Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint
```

---

## 🔌 API Configuration

Backend API endpoint configured in `src/api.js`:
```javascript
const API_BASE = 'http://localhost:8000/api';
```

### Available Endpoints

**Users:**
- `GET /users` - List all users
- `POST /users` - Create new user
- `GET /users/{name}` - Get specific user

**Research:**
- `GET /research/strategies` - List all strategies
- `GET /research/strategies?tag={tag}` - Filter by tag
- `POST /research/plan/composite` - Generate intervention plan

**Simulation:**
- `POST /simulation/run` - Run 30-day simulation

---

## 🎯 Common Tasks

### Adding a New Component

1. Create file in `src/components/`
2. Import `useTheme` hook
3. Implement dual-theme styling
4. Export and import in `App.jsx`

```jsx
import { useTheme } from '../contexts/ThemeContext';

export default function NewComponent() {
  const { isDark } = useTheme();
  
  return (
    <div className={`p-6 ${isDark ? 'bg-neutral-950' : 'bg-white'}`}>
      {/* Component content */}
    </div>
  );
}
```

### Adding a New Color

1. Update `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      'custom-color': {
        500: '#hexcode',
      }
    }
  }
}
```

2. Use in components with theme conditions

### Debugging Theme Issues

1. Check if component has `useTheme` hook
2. Verify conditional classes syntax
3. Check Tailwind config for color definitions
4. Test localStorage for theme persistence
5. Inspect element in DevTools for applied classes

---

## 🐛 Troubleshooting

**Theme not switching:**
- Ensure ThemeProvider wraps app in `main.jsx`
- Check browser console for errors
- Verify localStorage permissions

**Colors not appearing:**
- Check Tailwind config
- Run `npm run build` to regenerate CSS
- Clear browser cache

**API not connecting:**
- Verify backend is running on port 8000
- Check CORS settings in backend
- Inspect Network tab in DevTools

---

## 📚 Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Context API](https://react.dev/reference/react/useContext)
- [Recharts Docs](https://recharts.org/en-US)
- [Lucide Icons](https://lucide.dev/)

---

## 💡 Pro Tips

1. **Use Theme Transition**: Add `theme-transition` to elements that change colors
2. **Test Both Modes**: Always verify your component in both themes
3. **Consistent Patterns**: Follow existing conditional styling patterns
4. **Accessibility First**: Ensure sufficient contrast ratios
5. **Performance**: Avoid unnecessary re-renders by destructuring only needed theme values

---

## ✅ Development Checklist

Before committing:

- [ ] Component works in both themes
- [ ] No console errors or warnings
- [ ] ESLint passes (`npm run lint`)
- [ ] Transitions are smooth
- [ ] Colors match design system
- [ ] Accessibility standards met
- [ ] API calls handle errors
- [ ] Mobile responsive design tested

---

Happy coding! 🚀

For detailed theme documentation, see `THEME_SYSTEM.md`
For visual examples, see `THEME_VISUAL_GUIDE.md`
