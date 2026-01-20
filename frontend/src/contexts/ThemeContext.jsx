import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage first, default to dark mode
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });

  useEffect(() => {
    // Persist theme preference
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Update document class for global styling
    if (isDark) {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.add('light');
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const theme = {
    isDark,
    toggleTheme,
    // Color tokens for easy access
    colors: isDark ? {
      bg: {
        primary: 'bg-black',
        secondary: 'bg-neutral-950',
        tertiary: 'bg-neutral-900',
        card: 'bg-neutral-950/50',
        hover: 'bg-neutral-900/80',
      },
      text: {
        primary: 'text-white',
        secondary: 'text-neutral-300',
        muted: 'text-neutral-500',
      },
      border: {
        default: 'border-neutral-800',
        hover: 'border-neutral-700',
        accent: 'border-purple-500/30',
      },
      accent: {
        primary: 'bg-gradient-to-r from-purple-600 to-pink-600',
        secondary: 'bg-gradient-to-r from-fuchsia-600 to-pink-500',
        text: 'text-purple-400',
        glow: 'shadow-purple-500/50',
      }
    } : {
      bg: {
        primary: 'bg-slate-50',
        secondary: 'bg-white',
        tertiary: 'bg-slate-100',
        card: 'bg-white/80',
        hover: 'bg-slate-100',
      },
      text: {
        primary: 'text-slate-900',
        secondary: 'text-slate-700',
        muted: 'text-slate-500',
      },
      border: {
        default: 'border-slate-200',
        hover: 'border-slate-300',
        accent: 'border-emerald-300/50',
      },
      accent: {
        primary: 'bg-gradient-to-r from-emerald-500 to-teal-500',
        secondary: 'bg-gradient-to-r from-violet-400 to-purple-400',
        text: 'text-emerald-600',
        glow: 'shadow-emerald-500/30',
      }
    }
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};
