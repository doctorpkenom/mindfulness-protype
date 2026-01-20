import React, { useState } from 'react';
import { LayoutDashboard, Users, FlaskConical, PlayCircle, Activity, Sun, Moon } from 'lucide-react';
import { useTheme } from './contexts/ThemeContext';
import UserTab from './components/UserTab';
import PilotTab from './components/PilotTab';
import SimulationTab from './components/SimulationTab';

function App() {
  const [activeTab, setActiveTab] = useState('pilot');
  const { isDark, toggleTheme } = useTheme();

  const renderTab = () => {
    switch (activeTab) {
      case 'users': return <UserTab />;
      case 'pilot': return <PilotTab />;
      case 'simulation': return <SimulationTab />;
      case 'dashboard': return (
        <div className={`p-8 text-center ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
          Dashboard Coming Soon
        </div>
      );
      default: return <PilotTab />;
    }
  };

  const NavItem = ({ id, label, icon: Icon }) => {
    const isActive = activeTab === id;
    return (
      <button
        onClick={() => setActiveTab(id)}
        className={`flex items-center space-x-3 w-full p-3 rounded-lg transition-all duration-200 ${
          isActive
            ? isDark
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/30'
              : 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20'
            : isDark
            ? 'text-neutral-400 hover:bg-neutral-900/80 hover:text-neutral-200'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        }`}
      >
        <Icon size={20} />
        <span className="font-medium">{label}</span>
      </button>
    );
  };

  return (
    <div className={`flex h-screen font-sans overflow-hidden theme-transition ${
      isDark ? 'bg-black text-white' : 'bg-slate-50 text-slate-900'
    }`}>
      {/* Sidebar */}
      <aside className={`w-64 border-r flex flex-col p-4 theme-transition ${
        isDark 
          ? 'bg-neutral-950 border-neutral-800' 
          : 'bg-white border-slate-200'
      }`}>
        <div className="flex items-center space-x-3 px-2 mb-8 mt-2">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center theme-transition ${
            isDark
              ? 'bg-gradient-to-br from-purple-600 to-pink-600'
              : 'bg-gradient-to-br from-emerald-500 to-teal-500'
          }`}>
            <Activity className="text-white" size={20} />
          </div>
          <h1 className={`text-xl font-bold ${
            isDark ? 'gradient-text-dark' : 'gradient-text-light'
          }`}>
            Mindfulness
          </h1>
        </div>

        <nav className="space-y-2 flex-1">
          <NavItem id="dashboard" label="Dashboard" icon={LayoutDashboard} />
          <NavItem id="pilot" label="Live Pilot" icon={PlayCircle} />
          <NavItem id="users" label="User Manager" icon={Users} />
          <NavItem id="simulation" label="Simulation Lab" icon={FlaskConical} />
        </nav>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className={`flex items-center justify-center space-x-2 w-full p-3 rounded-lg mb-4 transition-all duration-300 ${
            isDark
              ? 'bg-neutral-900 hover:bg-neutral-800 text-neutral-300 border border-neutral-800'
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
          }`}
          aria-label="Toggle theme"
        >
          {isDark ? (
            <>
              <Sun size={18} className="text-yellow-400" />
              <span className="text-sm font-medium">Light Mode</span>
            </>
          ) : (
            <>
              <Moon size={18} className="text-purple-600" />
              <span className="text-sm font-medium">Dark Mode</span>
            </>
          )}
        </button>

        <div className={`text-xs px-2 text-center ${
          isDark ? 'text-neutral-600' : 'text-slate-400'
        }`}>
          v2.0.0 • Theme Ready
        </div>
      </aside>

      {/* Main Content */}
      <main className={`flex-1 overflow-auto relative theme-transition ${
        isDark ? 'bg-black' : 'bg-slate-50'
      }`}>
        {/* Optional subtle gradient overlay */}
        <div className={`absolute inset-0 pointer-events-none ${
          isDark 
            ? 'bg-gradient-to-br from-purple-950/10 via-transparent to-pink-950/10' 
            : 'bg-gradient-to-br from-emerald-50/30 via-transparent to-violet-50/30'
        }`} />
        
        <div className="max-w-7xl mx-auto min-h-full relative z-10">
          {renderTab()}
        </div>
      </main>
    </div>
  );
}

export default App;
