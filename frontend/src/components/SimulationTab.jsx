import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { FlaskConical, Play, TrendingUp, Calendar, ArrowUpRight } from 'lucide-react';
import { userApi, simulationApi } from '../api';

const SimulationTab = () => {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        userApi.getAll().then(res => {
            setUsers(res.data);
            if (res.data.length > 0) setSelectedUser(res.data[0].name);
        });
    }, []);

    const handleRunSim = async () => {
        if (!selectedUser) return;
        setLoading(true);
        setResults(null);
        try {
            const res = await simulationApi.run(selectedUser);
            setResults(res.data);
        } catch (err) {
            console.error(err);
            alert("Simulation Failed");
        } finally {
            setLoading(false);
        }
    };

    // Transform array of floats to objects for Recharts
    const chartData = results
        ? results.daily_completion_rates.map((rate, idx) => ({ day: idx + 1, rate: rate * 100 }))
        : [];

    return (
        <div className="p-8 h-full flex flex-col">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Simulation Lab</h2>
                    <p className="text-slate-400">Run longitudinal 30-day simulations to test intervention efficacy.</p>
                </div>

                <div className="flex items-center space-x-4 bg-slate-800 p-2 rounded-lg border border-slate-700">
                    <select
                        className="bg-transparent text-white outline-none border-r border-slate-600 px-4 py-2"
                        value={selectedUser}
                        onChange={(e) => setSelectedUser(e.target.value)}
                    >
                        {users.map(u => <option key={u.name} value={u.name}>{u.name}</option>)}
                    </select>
                    <button
                        onClick={handleRunSim}
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    >
                        {loading ? "Running..." : <><Play size={18} className="mr-2" /> Run 30-Day Sim</>}
                    </button>
                </div>
            </header>

            {/* Results Area */}
            {results ? (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">

                    {/* KPI Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                            <div className="text-slate-400 text-sm font-medium mb-1 flex items-center">
                                <Calendar size={16} className="mr-2" /> Week 1 Avg
                            </div>
                            <div className="text-3xl font-bold text-white">{(results.week_1_avg * 100).toFixed(1)}%</div>
                        </div>

                        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                            <div className="text-slate-400 text-sm font-medium mb-1 flex items-center">
                                <Calendar size={16} className="mr-2" /> Week 4 Avg
                            </div>
                            <div className="text-3xl font-bold text-white">{(results.week_4_avg * 100).toFixed(1)}%</div>
                        </div>

                        <div className={`bg-gradient-to-br p-6 rounded-xl border shadow-lg ${results.improvement >= 0 ? 'from-emerald-900 to-emerald-800 border-emerald-700' : 'from-rose-900 to-rose-800 border-rose-700'}`}>
                            <div className="text-emerald-100/70 text-sm font-medium mb-1 flex items-center">
                                <TrendingUp size={16} className="mr-2" /> Total Improvement
                            </div>
                            <div className="text-3xl font-bold text-white flex items-center">
                                {results.improvement >= 0 ? '+' : ''}{(results.improvement * 100).toFixed(1)}%
                                {results.improvement > 0 && <ArrowUpRight className="ml-2 text-emerald-400" />}
                            </div>
                        </div>
                    </div>

                    {/* Chart */}
                    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 h-[400px]">
                        <h3 className="text-lg font-semibold text-white mb-6">Daily Completion Rate</h3>
                        <ResponsiveContainer width="100%" height="90%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis
                                    dataKey="day"
                                    stroke="#94a3b8"
                                    tickLine={false}
                                    axisLine={false}
                                    label={{ value: 'Day', position: 'insideBottom', offset: -5 }}
                                />
                                <YAxis
                                    stroke="#94a3b8"
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(val) => `${val}%`}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                    cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
                                />
                                <ReferenceLine y={50} stroke="#475569" strokeDasharray="3 3" />
                                <Bar
                                    dataKey="rate"
                                    fill="#3b82f6"
                                    radius={[4, 4, 0, 0]}
                                    animationDuration={1500}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            ) : (
                <div className="flex-1 bg-slate-800/50 rounded-xl border-2 border-dashed border-slate-700 flex flex-col items-center justify-center text-slate-500">
                    <FlaskConical size={48} className="mb-4 opacity-50" />
                    <p className="text-lg">Select a user to begin simulation</p>
                </div>
            )}
        </div>
    );
};

export default SimulationTab;
