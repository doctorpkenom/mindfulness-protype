import React, { useEffect, useState } from 'react';
import { Play, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { userApi, researchApi } from '../api';

const PilotTab = () => {
    const { isDark } = useTheme();
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState('');
    const [context, setContext] = useState({ stress: 'medium', energy: 'medium' });
    const [generatedPlan, setGeneratedPlan] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        userApi.getAll().then(res => {
            setUsers(res.data);
            if (res.data.length > 0) setSelectedUser(res.data[0].name);
        });
    }, []);

    const handleSimulate = async () => {
        setLoading(true);
        try {
            // Simulate context variation
            const plan = await researchApi.generatePlan({
                stress: context.stress,
                energy: context.energy
            });
            setGeneratedPlan(plan.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const ContextButton = ({ type, val, current, set }) => {
        const isSelected = current === val;
        return (
            <button
                onClick={() => set(val)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all duration-200 ${
                    isSelected
                        ? isDark
                            ? 'bg-gradient-to-r from-purple-600 to-pink-600 border-transparent text-white shadow-lg shadow-purple-500/30'
                            : 'bg-gradient-to-r from-emerald-500 to-teal-500 border-transparent text-white shadow-lg shadow-emerald-500/20'
                        : isDark
                        ? 'bg-neutral-900/50 border-neutral-700 text-neutral-400 hover:border-neutral-600 hover:text-neutral-300'
                        : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-900'
                }`}
            >
                {val.charAt(0).toUpperCase() + val.slice(1)}
            </button>
        );
    };

    return (
        <div className="p-8 h-full flex flex-col">
            <header className="mb-8">
                <h2 className={`text-3xl font-bold mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    Live Pilot
                </h2>
                <p className={isDark ? 'text-neutral-400' : 'text-slate-600'}>
                    Simulate real-time drift events and view the AI's intervention strategy.
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">

                {/* Left Control Panel */}
                <div className="lg:col-span-4 space-y-6">
                    <div className={`p-6 rounded-xl border shadow-lg theme-transition ${
                        isDark 
                            ? 'bg-neutral-950/50 border-neutral-800' 
                            : 'bg-white border-slate-200'
                    }`}>
                        <label className={`block text-sm font-medium mb-2 ${
                            isDark ? 'text-neutral-400' : 'text-slate-600'
                        }`}>
                            Active Persona
                        </label>
                        <select
                            className={`w-full border rounded-lg p-3 outline-none theme-transition ${
                                isDark
                                    ? 'bg-neutral-900/50 border-neutral-700 text-white focus:ring-2 focus:ring-purple-500'
                                    : 'bg-slate-50 border-slate-200 text-slate-900 focus:ring-2 focus:ring-emerald-500'
                            }`}
                            value={selectedUser}
                            onChange={(e) => setSelectedUser(e.target.value)}
                        >
                            {users.map(u => <option key={u.name} value={u.name}>{u.name}</option>)}
                        </select>
                    </div>

                    <div className={`p-6 rounded-xl border shadow-lg space-y-6 theme-transition ${
                        isDark 
                            ? 'bg-neutral-950/50 border-neutral-800' 
                            : 'bg-white border-slate-200'
                    }`}>
                        <h3 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            Context Simulator
                        </h3>

                        <div>
                            <label className={`block text-xs uppercase tracking-wider mb-3 ${
                                isDark ? 'text-neutral-500' : 'text-slate-500'
                            }`}>
                                Stress Level
                            </label>
                            <div className="flex gap-2">
                                {['low', 'medium', 'high'].map(v => (
                                    <ContextButton key={v} type="stress" val={v} current={context.stress} set={(val) => setContext({ ...context, stress: val })} />
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className={`block text-xs uppercase tracking-wider mb-3 ${
                                isDark ? 'text-neutral-500' : 'text-slate-500'
                            }`}>
                                Energy Level
                            </label>
                            <div className="flex gap-2">
                                {['low', 'medium', 'high'].map(v => (
                                    <ContextButton key={v} type="energy" val={v} current={context.energy} set={(val) => setContext({ ...context, energy: val })} />
                                ))}
                            </div>
                        </div>

                        <div className={`pt-4 border-t ${isDark ? 'border-neutral-800' : 'border-slate-200'}`}>
                            <button
                                onClick={handleSimulate}
                                className={`w-full font-bold py-4 rounded-xl shadow-lg transform active:scale-95 transition-all flex items-center justify-center space-x-2 ${
                                    isDark
                                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 shadow-purple-500/30 text-white'
                                        : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 shadow-emerald-500/20 text-white'
                                }`}
                            >
                                {loading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" /> : <Sparkles size={20} />}
                                <span>Trigger Drift Event</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Display Panel */}
                <div className="lg:col-span-8">
                    {generatedPlan ? (
                        <div className={`rounded-2xl border overflow-hidden shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500 theme-transition ${
                            isDark 
                                ? 'bg-neutral-950/50 border-neutral-800' 
                                : 'bg-white border-slate-200'
                        }`}>
                            {/* Header */}
                            <div className={`p-6 border-b flex justify-between items-start theme-transition ${
                                isDark 
                                    ? 'bg-neutral-900/50 border-neutral-800' 
                                    : 'bg-slate-50/50 border-slate-200'
                            }`}>
                                <div>
                                    <div className={`flex items-center space-x-2 mb-1 ${
                                        isDark ? 'text-purple-400' : 'text-emerald-600'
                                    }`}>
                                        <Sparkles size={16} />
                                        <span className="text-xs font-bold uppercase tracking-widest">Intervention Generated</span>
                                    </div>
                                    <h3 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                        {generatedPlan.name}
                                    </h3>
                                    <p className={`text-sm mt-1 max-w-xl ${isDark ? 'text-neutral-400' : 'text-slate-600'}`}>
                                        {generatedPlan.rationale}
                                    </p>
                                </div>
                                {generatedPlan.adaptation_note && (
                                    <div className={`px-4 py-2 rounded-lg text-xs font-medium border max-w-xs ${
                                        isDark
                                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                                            : 'bg-amber-50 text-amber-700 border-amber-200'
                                    }`}>
                                        {generatedPlan.adaptation_note}
                                    </div>
                                )}
                            </div>

                            {/* Steps */}
                            <div className="p-6 grid gap-6">
                                {generatedPlan.steps.map((step, idx) => (
                                    <div key={idx} className="relative flex items-start group">
                                        {/* Connector Line */}
                                        {idx !== generatedPlan.steps.length - 1 && (
                                            <div className={`absolute left-6 top-12 bottom-[-24px] w-0.5 transition-colors ${
                                                isDark 
                                                    ? 'bg-neutral-800 group-hover:bg-neutral-700' 
                                                    : 'bg-slate-200 group-hover:bg-slate-300'
                                            }`} />
                                        )}

                                        {/* Number Bubble */}
                                        <div className={`flex-shrink-0 w-12 h-12 rounded-full border-2 flex items-center justify-center font-bold z-10 transition-all theme-transition ${
                                            isDark
                                                ? 'bg-neutral-800 border-neutral-700 text-white group-hover:border-purple-500 group-hover:bg-gradient-to-br group-hover:from-purple-600 group-hover:to-pink-600'
                                                : 'bg-slate-100 border-slate-300 text-slate-700 group-hover:border-emerald-500 group-hover:bg-gradient-to-br group-hover:from-emerald-500 group-hover:to-teal-500 group-hover:text-white'
                                        }`}>
                                            {idx + 1}
                                        </div>

                                        {/* Card */}
                                        <div className={`ml-6 flex-1 p-5 rounded-xl border transition-all theme-transition ${
                                            isDark
                                                ? 'bg-neutral-900/50 border-neutral-800/50 hover:border-purple-500/30'
                                                : 'bg-slate-50/50 border-slate-200/50 hover:border-emerald-500/30'
                                        }`}>
                                            <div className="flex justify-between items-start mb-2">
                                                <h4 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                                    {step.strategy}
                                                </h4>
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                                                    isDark
                                                        ? 'bg-neutral-900 text-neutral-400 border-neutral-800'
                                                        : 'bg-white text-slate-600 border-slate-200'
                                                }`}>
                                                    {step.phase}
                                                </span>
                                            </div>
                                            <p className={`text-sm leading-relaxed ${isDark ? 'text-neutral-300' : 'text-slate-700'}`}>
                                                {step.logic}
                                            </p>
                                            {step.source && (
                                                <div className={`mt-3 text-xs flex items-center ${
                                                    isDark ? 'text-neutral-500' : 'text-slate-500'
                                                }`}>
                                                    <div className={`h-px w-4 mr-2 ${isDark ? 'bg-neutral-700' : 'bg-slate-300'}`} />
                                                    Src: {step.source}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className={`h-full flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-2xl theme-transition ${
                            isDark 
                                ? 'border-neutral-800 text-neutral-600' 
                                : 'border-slate-200 text-slate-400'
                        }`}>
                            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
                                isDark ? 'bg-neutral-900' : 'bg-slate-100'
                            }`}>
                                <Play size={24} className="ml-1" />
                            </div>
                            <p className="text-lg font-medium">Ready for Simulation</p>
                            <p className="text-sm">Configure context and click "Trigger Drift Event"</p>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default PilotTab;
