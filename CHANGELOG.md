# Changelog

## [2.0.0] - Modern Theme System Update

### ✨ New Features

#### 🎨 Dual-Theme System
- **Dark Mode (AMOLED Black)**
  - Pure black (#000000) background for AMOLED displays
  - Purple (#a855f7) and Pink (#ec4899) gradient accents
  - Optimized for battery saving and low-light viewing
  - Sophisticated, modern aesthetic

- **Light Mode (Green & Lilac)**
  - Clean white/slate backgrounds
  - Emerald (#10b981) and Teal (#14b8a6) gradient accents
  - Lilac/purple secondary accents
  - Professional, calming design aligned with mindfulness theme

#### 🎯 Theme Features
- Persistent theme preference saved to localStorage
- Smooth 300ms transitions between themes
- Theme toggle button in sidebar
- Context-based architecture for easy theme management
- All components fully theme-aware

#### 🔧 Technical Improvements
- Created `ThemeContext` for centralized theme state
- Updated Tailwind config with custom color palettes
- Added theme-aware styling to all components:
  - PilotTab (Live intervention simulator)
  - UserTab (Persona management)
  - SimulationTab (30-day simulation with themed charts)
  - App shell and navigation
- Custom utility classes for theme transitions
- Gradient text effects for both themes
- Theme-aware chart visualizations (Recharts)

#### 📚 Documentation
- Comprehensive `THEME_SYSTEM.md` documentation
- Updated main README with tech stack and setup instructions
- Color palette reference guide
- Usage examples and best practices
- Development startup script (`start_dev.ps1`)

### 🎨 Design System

#### Dark Mode Colors
- Background: Pure Black (#000000)
- Surface: Neutral-950 (#0a0a0a)
- Primary Accent: Purple (#a855f7)
- Secondary Accent: Pink (#ec4899)
- Text: White with neutral variants

#### Light Mode Colors
- Background: Slate-50 (#f8fafc)
- Surface: White (#ffffff)
- Primary Accent: Emerald (#10b981)
- Secondary Accent: Teal (#14b8a6)
- Text: Slate-900 with lighter variants

### 🚀 Performance
- Optimized CSS transitions (300ms)
- Efficient context-based re-renders
- localStorage for instant theme restoration
- No FOUC (Flash of Unstyled Content)

### 🔄 Migration Notes
- All components now require ThemeProvider wrapper
- App.css simplified (legacy code removed)
- New utility classes in index.css
- Tailwind config extended with custom colors

### 📦 Dependencies
- No new dependencies added
- Uses existing React Context API
- Built with Tailwind CSS utilities
- Recharts gradients for themed visualizations

### 🐛 Bug Fixes
- Improved color contrast ratios for accessibility
- Fixed inconsistent spacing in components
- Standardized shadow effects across themes
- Better focus states for form elements

### 🎯 Next Steps (Future Enhancements)
1. Auto theme scheduling based on time of day
2. Multiple accent color options
3. High contrast accessibility modes
4. Custom theme creator for users
5. Advanced transition animations
6. CSS custom properties migration for better performance

---

## [1.0.0] - Initial Release

### Features
- Research Data Bank with 13 psychological papers
- Strategy Engine with adaptation rules
- ML Ensemble ("Council of Experts")
- Data Pipeline for preprocessing
- FastAPI backend
- React frontend
- User persona simulation
- 30-day longitudinal testing

### Components
- Habit Optimizer (Lally et al.)
- Stress Predictor (Sirois & Bandura)
- Curiosity Tuner (Loewenstein & Kang)
- Flow Manager (Csikszentmihalyi)

---

*For detailed theme documentation, see `frontend/THEME_SYSTEM.md`*
