import React, { useEffect, useState } from 'react';
import { Play, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';
import { userApi, researchApi } from '../api';

const PilotTab = () => {
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

    const ContextButton = ({ type, val, current, set }) => (
        <button
            onClick={() => set(val)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${current === val
                    ? 'bg-blue-600 border-blue-600 text-white shadow-lg'
                    : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-500'
                }`}
        >
            {val.charAt(0).toUpperCase() + val.slice(1)}
        </button>
    );

    return (
        <div className="p-8 h-full flex flex-col">
            <header className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Live Pilot</h2>
                <p className="text-slate-400">Simulate real-time drift events and view the AI's intervention strategy.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">

                {/* Left Control Panel */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
                        <label className="block text-sm font-medium text-slate-400 mb-2">Active Persona</label>
                        <select
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-blue-500"
                            value={selectedUser}
                            onChange={(e) => setSelectedUser(e.target.value)}
                        >
                            {users.map(u => <option key={u.name} value={u.name}>{u.name}</option>)}
                        </select>
                    </div>

                    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg space-y-6">
                        <h3 className="text-lg font-semibold text-white">Context Simulator</h3>

                        <div>
                            <label className="block text-xs uppercase tracking-wider text-slate-500 mb-3">Stress Level</label>
                            <div className="flex gap-2">
                                {['low', 'medium', 'high'].map(v => (
                                    <ContextButton key={v} type="stress" val={v} current={context.stress} set={(val) => setContext({ ...context, stress: val })} />
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs uppercase tracking-wider text-slate-500 mb-3">Energy Level</label>
                            <div className="flex gap-2">
                                {['low', 'medium', 'high'].map(v => (
                                    <ContextButton key={v} type="energy" val={v} current={context.energy} set={(val) => setContext({ ...context, energy: val })} />
                                ))}
                            </div>
                        </div>

                        <div className="pt-4 border-t border-slate-700">
                            <button
                                onClick={handleSimulate}
                                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 rounded-xl shadow-lg transform active:scale-95 transition-all flex items-center justify-center space-x-2"
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
                        <div className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
                            {/* Header */}
                            <div className="bg-slate-900/50 p-6 border-b border-slate-700 flex justify-between items-start">
                                <div>
                                    <div className="flex items-center space-x-2 text-blue-400 mb-1">
                                        <Sparkles size={16} />
                                        <span className="text-xs font-bold uppercase tracking-widest">Intervention Generated</span>
                                    </div>
                                    <h3 className="text-2xl font-bold text-white">{generatedPlan.name}</h3>
                                    <p className="text-slate-400 text-sm mt-1 max-w-xl">{generatedPlan.rationale}</p>
                                </div>
                                {generatedPlan.adaptation_note && (
                                    <div className="bg-amber-500/10 text-amber-400 px-4 py-2 rounded-lg text-xs font-medium border border-amber-500/20 max-w-xs">
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
                                            <div className="absolute left-6 top-12 bottom-[-24px] w-0.5 bg-slate-700 group-hover:bg-slate-600 transition-colors" />
                                        )}

                                        {/* Number Bubble */}
                                        <div className="flex-shrink-0 w-12 h-12 rounded-full bg-slate-700 border-2 border-slate-600 flex items-center justify-center text-white font-bold z-10 group-hover:border-blue-500 group-hover:bg-blue-600 transition-all">
                                            {idx + 1}
                                        </div>

                                        {/* Card */}
                                        <div className="ml-6 flex-1 bg-slate-900/50 p-5 rounded-xl border border-slate-700/50 hover:border-blue-500/30 transition-all">
                                            <div className="flex justify-between items-start mb-2">
                                                <h4 className="text-lg font-semibold text-white">{step.strategy}</h4>
                                                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700">
                                                    {step.phase}
                                                </span>
                                            </div>
                                            <p className="text-slate-300 text-sm leading-relaxed">{step.logic}</p>
                                            {step.source && (
                                                <div className="mt-3 text-xs text-slate-500 flex items-center">
                                                    <div className="h-px bg-slate-700 w-4 mr-2" />
                                                    Src: {step.source}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center p-12 border-2 border-dashed border-slate-800 rounded-2xl text-slate-600">
                            <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
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
