import React from 'react';
import { Shield, FlaskConical, Settings, TestTube } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import DebugTab from './DebugTab';
import SimulationTab from './SimulationTab';
import TesterTab from './TesterTab';

export default function AdminView() {
  const { isDark } = useTheme();
  const [activeSection, setActiveSection] = React.useState('debug');

  return (
    <div className="space-y-6">
      <div>
        <h1 className={`text-3xl font-bold mb-2 flex items-center gap-3 ${
          isDark ? 'text-white' : 'text-slate-900'
        }`}>
          <Shield className={isDark ? 'text-purple-400' : 'text-emerald-600'} />
          Admin Panel
        </h1>
        <p className={`text-sm ${
          isDark ? 'text-neutral-400' : 'text-slate-600'
        }`}>
          System diagnostics, simulations, and debugging tools
        </p>
      </div>

      {/* Admin Navigation */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => setActiveSection('debug')}
          className={`px-4 py-2 border-b-2 transition-colors ${
            activeSection === 'debug'
              ? isDark
                ? 'border-purple-500 text-purple-400'
                : 'border-emerald-500 text-emerald-600'
              : isDark
              ? 'border-transparent text-neutral-400 hover:text-neutral-200'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <Settings size={18} className="inline mr-2" />
          Debug & Settings
        </button>
        <button
          onClick={() => setActiveSection('simulation')}
          className={`px-4 py-2 border-b-2 transition-colors ${
            activeSection === 'simulation'
              ? isDark
                ? 'border-purple-500 text-purple-400'
                : 'border-emerald-500 text-emerald-600'
              : isDark
              ? 'border-transparent text-neutral-400 hover:text-neutral-200'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <FlaskConical size={18} className="inline mr-2" />
          Simulation Lab
        </button>
        <button
          onClick={() => setActiveSection('tester')}
          className={`px-4 py-2 border-b-2 transition-colors ${
            activeSection === 'tester'
              ? isDark
                ? 'border-purple-500 text-purple-400'
                : 'border-emerald-500 text-emerald-600'
              : isDark
              ? 'border-transparent text-neutral-400 hover:text-neutral-200'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <TestTube size={18} className="inline mr-2" />
          Scheduler Tester
        </button>
      </div>

      {/* Content */}
      <div>
        {activeSection === 'debug' && <DebugTab />}
        {activeSection === 'simulation' && <SimulationTab />}
        {activeSection === 'tester' && <TesterTab />}
      </div>
    </div>
  );
}
