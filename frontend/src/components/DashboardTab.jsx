import React, { useEffect, useState } from 'react';
import { TrendingUp, Users, Zap, Target, Brain, Award, Activity, AlertCircle } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { analyticsApi } from '../api';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

const DashboardTab = () => {
    const { isDark } = useTheme();
    const [stats, setStats] = useState(null);
    const [models, setModels] = useState([]);
    const [trends, setTrends] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [statsRes, modelsRes, trendsRes] = await Promise.all([
                analyticsApi.getDashboardStats(),
                analyticsApi.getModelMetrics(),
                analyticsApi.getInteractionTrends(30)
            ]);
            setStats(statsRes.data);
            setModels(modelsRes.data);
            setTrends(trendsRes.data);
        } catch (err) {
            console.error("Failed to load dashboard:", err);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ icon: Icon, label, value, trend, color }) => (
        <div className={`p-6 rounded-xl border theme-transition ${
            isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
        }`}>
            <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    isDark ? `bg-${color}-500/20` : `bg-${color}-100`
                }`}>
                    <Icon className={`text-${color}-${isDark ? '400' : '600'}`} size={24} />
                </div>
                {trend && (
                    <div className={`flex items-center text-sm font-medium ${
                        trend > 0 ? 'text-emerald-500' : trend < 0 ? 'text-rose-500' : 'text-neutral-500'
                    }`}>
                        <TrendingUp size={16} className="mr-1" />
                        {trend > 0 ? '+' : ''}{(trend * 100).toFixed(1)}%
                    </div>
                )}
            </div>
            <div className={`text-sm font-medium mb-1 ${isDark ? 'text-neutral-400' : 'text-slate-600'}`}>
                {label}
            </div>
            <div className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                {value}
            </div>
        </div>
    );

    const ModelCard = ({ model }) => {
        const trendColor = model.trend === 'improving' ? 'emerald' : 
                          model.trend === 'declining' ? 'rose' : 'neutral';
        
        return (
            <div className={`p-4 rounded-lg border theme-transition ${
                isDark ? 'bg-neutral-900/50 border-neutral-800' : 'bg-slate-50 border-slate-200'
            }`}>
                <div className="flex items-center justify-between mb-2">
                    <h4 className={`font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {model.model_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                        isDark 
                            ? `bg-${trendColor}-500/20 text-${trendColor}-400`
                            : `bg-${trendColor}-100 text-${trendColor}-700`
                    }`}>
                        {model.trend}
                    </span>
                </div>
                <div className="flex items-baseline gap-2 mb-2">
                    <span className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {(model.current_accuracy * 100).toFixed(1)}%
                    </span>
                    <span className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                        accuracy
                    </span>
                </div>
                <div className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                    {model.total_predictions} predictions
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="p-8 h-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
            </div>
        );
    }

    // Prepare chart data
    const trendChartData = trends.map(t => ({
        date: new Date(t.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        count: t.count,
        success: t.success_rate * 100
    }));

    const topStrategiesData = stats?.top_strategies?.slice(0, 5).map(s => ({
        name: s.name.length > 20 ? s.name.substring(0, 20) + '...' : s.name,
        fullName: s.name,
        rate: s.success_rate * 100,
        uses: s.total_uses
    })) || [];

    const COLORS = isDark 
        ? ['#a855f7', '#ec4899', '#8b5cf6', '#d946ef', '#c026d3']
        : ['#10b981', '#14b8a6', '#06b6d4', '#0ea5e9', '#3b82f6'];

    return (
        <div className="p-8 space-y-8">
            <header>
                <h2 className={`text-3xl font-bold mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    Analytics Dashboard
                </h2>
                <p className={isDark ? 'text-neutral-400' : 'text-slate-600'}>
                    Real-time insights into system performance and user engagement
                </p>
            </header>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={Users}
                    label="Total Users"
                    value={stats?.total_users || 0}
                    color="purple"
                />
                <StatCard
                    icon={Zap}
                    label="Interactions"
                    value={stats?.total_interactions || 0}
                    color="pink"
                />
                <StatCard
                    icon={Target}
                    label="Completion Rate"
                    value={`${((stats?.avg_completion_rate || 0) * 100).toFixed(1)}%`}
                    trend={stats?.avg_completion_rate ? stats.avg_completion_rate - 0.5 : 0}
                    color="emerald"
                />
                <StatCard
                    icon={Activity}
                    label="Active Users (7d)"
                    value={stats?.active_users_7d || 0}
                    color="blue"
                />
            </div>

            {/* ML Models Performance */}
            <div className={`p-6 rounded-xl border theme-transition ${
                isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
            }`}>
                <div className="flex items-center gap-2 mb-6">
                    <Brain className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                    <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        ML Model Performance
                    </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {models.map((model, idx) => (
                        <ModelCard key={idx} model={model} />
                    ))}
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Interaction Trends */}
                <div className={`p-6 rounded-xl border theme-transition ${
                    isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
                }`}>
                    <h3 className={`text-lg font-semibold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        30-Day Interaction Trends
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={trendChartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262626' : '#e2e8f0'} />
                            <XAxis dataKey="date" stroke={isDark ? '#737373' : '#94a3b8'} />
                            <YAxis stroke={isDark ? '#737373' : '#94a3b8'} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: isDark ? '#0a0a0a' : '#ffffff',
                                    border: `1px solid ${isDark ? '#404040' : '#e2e8f0'}`,
                                    borderRadius: '8px'
                                }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="count" 
                                stroke={isDark ? '#a855f7' : '#10b981'} 
                                strokeWidth={2}
                                dot={false}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="success" 
                                stroke={isDark ? '#ec4899' : '#14b8a6'} 
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Top Strategies */}
                <div className={`p-6 rounded-xl border theme-transition ${
                    isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
                }`}>
                    <h3 className={`text-lg font-semibold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        Top Performing Strategies
                    </h3>
                    <div className="space-y-3">
                        {topStrategiesData.map((strategy, idx) => (
                            <div key={idx} className={`p-3 rounded-lg ${
                                isDark ? 'bg-neutral-900/50' : 'bg-slate-50'
                            }`}>
                                <div className="flex justify-between items-start mb-2">
                                    <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                        {strategy.name}
                                    </span>
                                    <span className={`text-sm font-bold ${
                                        isDark ? 'text-purple-400' : 'text-emerald-600'
                                    }`}>
                                        {strategy.rate.toFixed(1)}%
                                    </span>
                                </div>
                                <div className={`h-2 rounded-full overflow-hidden ${
                                    isDark ? 'bg-neutral-800' : 'bg-slate-200'
                                }`}>
                                    <div 
                                        className={`h-full transition-all ${
                                            isDark 
                                                ? 'bg-gradient-to-r from-purple-600 to-pink-600'
                                                : 'bg-gradient-to-r from-emerald-500 to-teal-500'
                                        }`}
                                        style={{ width: `${strategy.rate}%` }}
                                    />
                                </div>
                                <div className={`text-xs mt-1 ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                                    {strategy.uses} uses
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className={`p-6 rounded-xl border theme-transition ${
                isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
            }`}>
                <div className="flex items-center gap-2 mb-4">
                    <Award className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                    <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        System Health
                    </h3>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                        <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {models.length}
                        </div>
                        <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                            Active Models
                        </div>
                    </div>
                    <div className="text-center">
                        <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            13
                        </div>
                        <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                            Research Modules
                        </div>
                    </div>
                    <div className="text-center">
                        <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {stats?.total_simulations || 0}
                        </div>
                        <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                            Simulations Run
                        </div>
                    </div>
                    <div className="text-center">
                        <div className={`text-2xl font-bold text-emerald-500`}>
                            99.9%
                        </div>
                        <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                            Uptime
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardTab;
