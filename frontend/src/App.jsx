import React, { useState } from 'react';
import { LayoutDashboard, Calendar, Clock, BarChart3, Settings, Sun, Moon, LogOut, Shield } from 'lucide-react';
import { useTheme } from './contexts/ThemeContext';
import { useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import TaskDashboard from './components/TaskDashboard';
import ScheduleView from './components/ScheduleView';
import TimerView from './components/TimerView';
import AnalyticsView from './components/AnalyticsView';
import AdminView from './components/AdminView';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const [activeTab, setActiveTab] = useState('tasks');
  const { isDark, toggleTheme } = useTheme();
  const { user, logout, loading } = useAuth();

  // Show login page if not authenticated
  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${
        isDark ? 'bg-black' : 'bg-slate-50'
      }`}>
        <LoadingSpinner message="Loading..." />
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  const renderTab = () => {
    switch (activeTab) {
      case 'tasks': return <TaskDashboard />;
      case 'schedule': return <ScheduleView />;
      case 'timer': return <TimerView />;
      case 'analytics': return <AnalyticsView />;
      case 'admin': return user.is_admin ? <AdminView /> : <div>Access Denied</div>;
      default: return <TaskDashboard />;
    }
  };

  const NavItem = ({ id, label, icon: Icon, adminOnly = false }) => {
    if (adminOnly && !user.is_admin) return null;
    
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
            <LayoutDashboard className="text-white" size={20} />
          </div>
          <div className="flex-1">
            <h1 className={`text-xl font-bold ${
              isDark ? 'gradient-text-dark' : 'gradient-text-light'
            }`}>
              Productivity
            </h1>
            <p className={`text-xs ${
              isDark ? 'text-neutral-500' : 'text-slate-400'
            }`}>
              {user.username}
            </p>
          </div>
        </div>

        <nav className="space-y-2 flex-1">
          <NavItem id="tasks" label="My Tasks" icon={LayoutDashboard} />
          <NavItem id="schedule" label="Schedule" icon={Calendar} />
          <NavItem id="timer" label="Timer" icon={Clock} />
          <NavItem id="analytics" label="Analytics" icon={BarChart3} />
          <NavItem id="admin" label="Admin" icon={Shield} adminOnly={true} />
        </nav>

        {/* User Info & Actions */}
        <div className={`border-t pt-4 space-y-2 ${
          isDark ? 'border-neutral-800' : 'border-slate-200'
        }`}>
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className={`flex items-center justify-center space-x-2 w-full p-3 rounded-lg mb-2 transition-all duration-300 ${
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

          {/* Logout */}
          <button
            onClick={logout}
            className={`flex items-center justify-center space-x-2 w-full p-3 rounded-lg transition-all duration-300 ${
              isDark
                ? 'bg-neutral-900 hover:bg-neutral-800 text-neutral-300 border border-neutral-800'
                : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
            }`}
          >
            <LogOut size={18} />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>

        <div className={`text-xs px-2 text-center mt-4 ${
          isDark ? 'text-neutral-600' : 'text-slate-400'
        }`}>
          v3.0.0 • ML-Powered
        </div>
      </aside>

      {/* Main Content */}
      <main className={`flex-1 overflow-auto relative theme-transition ${
        isDark ? 'bg-black' : 'bg-slate-50'
      }`}>
        <div className={`absolute inset-0 pointer-events-none ${
          isDark 
            ? 'bg-gradient-to-br from-purple-950/10 via-transparent to-pink-950/10' 
            : 'bg-gradient-to-br from-emerald-50/30 via-transparent to-violet-50/30'
        }`} />
        
        <div className="max-w-7xl mx-auto min-h-full relative z-10 p-6">
          {renderTab()}
        </div>
      </main>
    </div>
  );
}

export default App;
