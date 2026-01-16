import React, { useState } from 'react';
import { LayoutDashboard, Users, FlaskConical, PlayCircle, Activity } from 'lucide-react';
import UserTab from './components/UserTab';
import PilotTab from './components/PilotTab';
import SimulationTab from './components/SimulationTab';

function App() {
  const [activeTab, setActiveTab] = useState('pilot');

  const renderTab = () => {
    switch (activeTab) {
      case 'users': return <UserTab />;
      case 'pilot': return <PilotTab />;
      case 'simulation': return <SimulationTab />;
      case 'dashboard': return <div className="p-8 text-center text-slate-500">Dashboard Coming Soon</div>;
      default: return <PilotTab />;
    }
  };

  const NavItem = ({ id, label, icon: Icon }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center space-x-3 w-full p-3 rounded-lg transition-colors ${activeTab === id
        ? 'bg-blue-600 text-white shadow-md'
        : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
        }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </button>
  );

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col p-4">
        <div className="flex items-center space-x-3 px-2 mb-8 mt-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
            <Activity className="text-white" size={20} />
          </div>
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
            Mindfulness Prototype
          </h1>
        </div>

        <nav className="space-y-2 flex-1">
          <NavItem id="dashboard" label="Dashboard" icon={LayoutDashboard} />
          <NavItem id="pilot" label="Live Pilot" icon={PlayCircle} />
          <NavItem id="users" label="User Manager" icon={Users} />
          <NavItem id="simulation" label="Simulation Lab" icon={FlaskConical} />
        </nav>

        <div className="text-xs text-slate-600 px-2 text-center">
          v2.0.0 (Web Architecture)
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-slate-900 relative">
        <div className="absolute inset-0 bg-slate-900/50 pointer-events-none" /> {/* Optional overlay */}
        {/* Container */}
        <div className="max-w-7xl mx-auto min-h-full">
          {renderTab()}
        </div>
      </main>
    </div>
  );
}

export default App;
