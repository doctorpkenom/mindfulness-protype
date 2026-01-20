import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { FlaskConical, Play, TrendingUp, Calendar, ArrowUpRight } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { userApi, simulationApi } from '../api';

const SimulationTab = () => {
    const { isDark } = useTheme();
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
                    <h2 className={`text-3xl font-bold mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        Simulation Lab
                    </h2>
                    <p className={isDark ? 'text-neutral-400' : 'text-slate-600'}>
                        Run longitudinal 30-day simulations to test intervention efficacy.
                    </p>
                </div>

                <div className={`flex items-center space-x-4 p-2 rounded-lg border theme-transition ${
                    isDark 
                        ? 'bg-neutral-950/50 border-neutral-800' 
                        : 'bg-white border-slate-200'
                }`}>
                    <select
                        className={`bg-transparent outline-none border-r px-4 py-2 theme-transition ${
                            isDark 
                                ? 'text-white border-neutral-700' 
                                : 'text-slate-900 border-slate-300'
                        }`}
                        value={selectedUser}
                        onChange={(e) => setSelectedUser(e.target.value)}
                    >
                        {users.map(u => <option key={u.name} value={u.name}>{u.name}</option>)}
                    </select>
                    <button
                        onClick={handleRunSim}
                        disabled={loading}
                        className={`font-bold py-2 px-6 rounded-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center ${
                            isDark
                                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-lg shadow-purple-500/20'
                                : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/10'
                        }`}
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
                        <div className={`p-6 rounded-xl border theme-transition ${
                            isDark 
                                ? 'bg-neutral-950/50 border-neutral-800' 
                                : 'bg-white border-slate-200 shadow-md'
                        }`}>
                            <div className={`text-sm font-medium mb-1 flex items-center ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                            }`}>
                                <Calendar size={16} className="mr-2" /> Week 1 Avg
                            </div>
                            <div className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                {(results.week_1_avg * 100).toFixed(1)}%
                            </div>
                        </div>

                        <div className={`p-6 rounded-xl border theme-transition ${
                            isDark 
                                ? 'bg-neutral-950/50 border-neutral-800' 
                                : 'bg-white border-slate-200 shadow-md'
                        }`}>
                            <div className={`text-sm font-medium mb-1 flex items-center ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                            }`}>
                                <Calendar size={16} className="mr-2" /> Week 4 Avg
                            </div>
                            <div className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                {(results.week_4_avg * 100).toFixed(1)}%
                            </div>
                        </div>

                        <div className={`bg-gradient-to-br p-6 rounded-xl border shadow-lg ${
                            results.improvement >= 0 
                                ? isDark
                                    ? 'from-emerald-950 to-emerald-900 border-emerald-800'
                                    : 'from-emerald-500 to-emerald-600 border-emerald-400'
                                : isDark
                                ? 'from-rose-950 to-rose-900 border-rose-800'
                                : 'from-rose-500 to-rose-600 border-rose-400'
                        }`}>
                            <div className={`text-sm font-medium mb-1 flex items-center ${
                                results.improvement >= 0 
                                    ? 'text-emerald-100/70' 
                                    : 'text-rose-100/70'
                            }`}>
                                <TrendingUp size={16} className="mr-2" /> Total Improvement
                            </div>
                            <div className="text-3xl font-bold text-white flex items-center">
                                {results.improvement >= 0 ? '+' : ''}{(results.improvement * 100).toFixed(1)}%
                                {results.improvement > 0 && <ArrowUpRight className="ml-2 text-emerald-300" />}
                            </div>
                        </div>
                    </div>

                    {/* Chart */}
                    <div className={`p-6 rounded-xl border h-[400px] theme-transition ${
                        isDark 
                            ? 'bg-neutral-950/50 border-neutral-800' 
                            : 'bg-white border-slate-200 shadow-md'
                    }`}>
                        <h3 className={`text-lg font-semibold mb-6 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            Daily Completion Rate
                        </h3>
                        <ResponsiveContainer width="100%" height="90%">
                            <BarChart data={chartData}>
                                <CartesianGrid 
                                    strokeDasharray="3 3" 
                                    stroke={isDark ? '#262626' : '#e2e8f0'} 
                                    vertical={false} 
                                />
                                <XAxis
                                    dataKey="day"
                                    stroke={isDark ? '#737373' : '#94a3b8'}
                                    tickLine={false}
                                    axisLine={false}
                                    label={{ value: 'Day', position: 'insideBottom', offset: -5 }}
                                />
                                <YAxis
                                    stroke={isDark ? '#737373' : '#94a3b8'}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(val) => `${val}%`}
                                />
                                <Tooltip
                                    contentStyle={{ 
                                        backgroundColor: isDark ? '#0a0a0a' : '#ffffff',
                                        border: `1px solid ${isDark ? '#404040' : '#e2e8f0'}`,
                                        borderRadius: '8px',
                                        color: isDark ? '#fff' : '#0f172a'
                                    }}
                                    itemStyle={{ color: isDark ? '#fff' : '#0f172a' }}
                                    cursor={{ fill: isDark ? 'rgba(168, 85, 247, 0.1)' : 'rgba(16, 185, 129, 0.1)' }}
                                />
                                <ReferenceLine 
                                    y={50} 
                                    stroke={isDark ? '#525252' : '#94a3b8'} 
                                    strokeDasharray="3 3" 
                                />
                                <Bar
                                    dataKey="rate"
                                    fill={isDark ? 'url(#darkGradient)' : 'url(#lightGradient)'}
                                    radius={[4, 4, 0, 0]}
                                    animationDuration={1500}
                                />
                                <defs>
                                    <linearGradient id="darkGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#a855f7" stopOpacity={0.8}/>
                                        <stop offset="100%" stopColor="#ec4899" stopOpacity={0.8}/>
                                    </linearGradient>
                                    <linearGradient id="lightGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#10b981" stopOpacity={0.8}/>
                                        <stop offset="100%" stopColor="#14b8a6" stopOpacity={0.8}/>
                                    </linearGradient>
                                </defs>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            ) : (
                <div className={`flex-1 rounded-xl border-2 border-dashed flex flex-col items-center justify-center theme-transition ${
                    isDark 
                        ? 'bg-neutral-900/30 border-neutral-800 text-neutral-600' 
                        : 'bg-slate-50 border-slate-200 text-slate-400'
                }`}>
                    <FlaskConical size={48} className="mb-4 opacity-50" />
                    <p className="text-lg">Select a user to begin simulation</p>
                </div>
            )}
        </div>
    );
};

export default SimulationTab;
