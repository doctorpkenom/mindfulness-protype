import React, { useState, useEffect } from 'react';
import { Bug, Settings, TestTube, Database, FileText, Zap, RefreshCw, Trash2, Play } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { debugApi, analyticsApi } from '../api';

const DebugTab = () => {
    const { isDark } = useTheme();
    const [logs, setLogs] = useState([]);
    const [systemInfo, setSystemInfo] = useState(null);
    const [modelWeights, setModelWeights] = useState(null);
    const [testResult, setTestResult] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const [testParams, setTestParams] = useState({
        model: 'stress_predictor',
        context: { stress: 'high', energy: 'low' }
    });

    useEffect(() => {
        loadSystemInfo();
        loadLogs();
    }, []);

    const loadSystemInfo = async () => {
        try {
            const res = await debugApi.getSystemInfo();
            setSystemInfo(res.data);
        } catch (err) {
            console.error("Failed to load system info:", err);
        }
    };

    const loadLogs = async () => {
        try {
            const res = await debugApi.getLogs(50);
            setLogs(res.data);
        } catch (err) {
            console.error("Failed to load logs:", err);
        }
    };

    const testModel = async () => {
        setLoading(true);
        try {
            const res = await debugApi.testModel({
                model_name: testParams.model,
                context: testParams.context,
                strategies: [
                    { name: "Deep Work Session", tags: ["productivity", "flow"], difficulty: "High" },
                    { name: "Mindful Breathing", tags: ["emotion", "reflection"], difficulty: "Low" },
                    { name: "Micro Task", tags: ["simplicity", "ability"], difficulty: "Very Low" },
                    { name: "Curiosity Quiz", tags: ["curiosity", "engagement"], difficulty: "Medium" }
                ]
            });
            setTestResult(res.data);
        } catch (err) {
            console.error("Model test failed:", err);
            setTestResult({ error: err.message });
        } finally {
            setLoading(false);
        }
    };

    const testResearchEngine = async () => {
        setLoading(true);
        try {
            const res = await debugApi.testResearchEngine();
            alert(`Research Engine Test:\n${res.data.total_modules} modules\n${res.data.total_strategies} strategies`);
        } catch (err) {
            console.error("Research test failed:", err);
            alert(`Test failed: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const loadModelWeights = async (modelName) => {
        try {
            const res = await debugApi.getModelWeights(modelName);
            setModelWeights(res.data);
        } catch (err) {
            console.error("Failed to load weights:", err);
        }
    };

    const LogEntry = ({ log }) => {
        const levelColors = {
            ERROR: isDark ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' : 'bg-rose-100 text-rose-700 border-rose-200',
            WARNING: isDark ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-amber-100 text-amber-700 border-amber-200',
            INFO: isDark ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : 'bg-blue-100 text-blue-700 border-blue-200',
            DEBUG: isDark ? 'bg-neutral-500/20 text-neutral-400 border-neutral-500/30' : 'bg-slate-100 text-slate-700 border-slate-200'
        };

        return (
            <div className={`p-3 rounded-lg border text-sm font-mono ${
                isDark ? 'bg-neutral-900/50 border-neutral-800' : 'bg-white border-slate-200'
            }`}>
                <div className="flex items-start gap-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold border ${levelColors[log.level] || levelColors.DEBUG}`}>
                        {log.level}
                    </span>
                    <div className="flex-1">
                        <div className={`flex items-center gap-2 mb-1 ${isDark ? 'text-neutral-400' : 'text-slate-600'}`}>
                            <span className="font-semibold">{log.component}</span>
                            <span className="text-xs opacity-60">{new Date(log.timestamp).toLocaleString()}</span>
                        </div>
                        <div className={isDark ? 'text-white' : 'text-slate-900'}>
                            {log.message}
                        </div>
                        {log.context && Object.keys(log.context).length > 0 && (
                            <details className="mt-2">
                                <summary className={`cursor-pointer text-xs ${isDark ? 'text-purple-400' : 'text-emerald-600'}`}>
                                    View Context
                                </summary>
                                <pre className={`mt-2 p-2 rounded text-xs overflow-auto ${
                                    isDark ? 'bg-black/50 text-neutral-300' : 'bg-slate-50 text-slate-700'
                                }`}>
                                    {JSON.stringify(log.context, null, 2)}
                                </pre>
                            </details>
                        )}
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="p-8 space-y-8">
            <header>
                <h2 className={`text-3xl font-bold mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    Debug & Testing Console
                </h2>
                <p className={isDark ? 'text-neutral-400' : 'text-slate-600'}>
                    System diagnostics and ML model testing tools
                </p>
            </header>

            {/* System Info */}
            {systemInfo && (
                <div className={`p-6 rounded-xl border theme-transition ${
                    isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
                }`}>
                    <div className="flex items-center gap-2 mb-4">
                        <Database className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                        <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            System Status
                        </h3>
                        <span className={`ml-auto px-3 py-1 rounded-full text-sm font-bold ${
                            isDark ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-100 text-emerald-700'
                        }`}>
                            {systemInfo.status}
                        </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>Users</div>
                            <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                {systemInfo.database?.users || 0}
                            </div>
                        </div>
                        <div>
                            <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>Interactions</div>
                            <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                {systemInfo.database?.interactions || 0}
                            </div>
                        </div>
                        <div>
                            <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>ML Models</div>
                            <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                {systemInfo.ml_models?.length || 0}
                            </div>
                        </div>
                        <div>
                            <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>Research</div>
                            <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                {systemInfo.research_modules || 0}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Model Testing */}
            <div className={`p-6 rounded-xl border theme-transition ${
                isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
            }`}>
                <div className="flex items-center gap-2 mb-6">
                    <TestTube className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                    <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        Model Testing
                    </h3>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Test Configuration */}
                    <div className="space-y-4">
                        <div>
                            <label className={`block text-sm font-medium mb-2 ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                            }`}>
                                Select Model
                            </label>
                            <select
                                className={`w-full p-3 rounded-lg border theme-transition ${
                                    isDark
                                        ? 'bg-neutral-900/50 border-neutral-700 text-white'
                                        : 'bg-white border-slate-200 text-slate-900'
                                }`}
                                value={testParams.model}
                                onChange={(e) => setTestParams({ ...testParams, model: e.target.value })}
                            >
                                <option value="stress_predictor">Stress Predictor</option>
                                <option value="habit_optimizer">Habit Optimizer</option>
                                <option value="curiosity_tuner">Curiosity Tuner</option>
                                <option value="flow_manager">Flow Manager</option>
                                <option value="attention_manager">Attention Manager</option>
                                <option value="motivation_booster">Motivation Booster</option>
                                <option value="zeigarnik_tracker">Zeigarnik Tracker</option>
                            </select>
                        </div>

                        <div>
                            <label className={`block text-sm font-medium mb-2 ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                            }`}>
                                Context (JSON)
                            </label>
                            <textarea
                                className={`w-full p-3 rounded-lg border font-mono text-sm theme-transition ${
                                    isDark
                                        ? 'bg-neutral-900/50 border-neutral-700 text-white'
                                        : 'bg-white border-slate-200 text-slate-900'
                                }`}
                                rows="4"
                                value={JSON.stringify(testParams.context, null, 2)}
                                onChange={(e) => {
                                    try {
                                        setTestParams({ ...testParams, context: JSON.parse(e.target.value) });
                                    } catch (err) {}
                                }}
                            />
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={testModel}
                                disabled={loading}
                                className={`flex-1 py-3 px-4 rounded-lg font-bold transition-all flex items-center justify-center gap-2 ${
                                    isDark
                                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white'
                                        : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white'
                                }`}
                            >
                                {loading ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />}
                                Run Test
                            </button>
                            <button
                                onClick={() => loadModelWeights(testParams.model)}
                                className={`px-4 py-3 rounded-lg border font-medium transition-all ${
                                    isDark
                                        ? 'border-neutral-700 text-neutral-300 hover:bg-neutral-800'
                                        : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                                }`}
                            >
                                View Weights
                            </button>
                        </div>
                    </div>

                    {/* Test Results */}
                    <div className={`p-4 rounded-lg border ${
                        isDark ? 'bg-neutral-900/50 border-neutral-800' : 'bg-slate-50 border-slate-200'
                    }`}>
                        <h4 className={`font-semibold mb-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            Test Results
                        </h4>
                        {testResult ? (
                            <div className="space-y-3">
                                {testResult.error ? (
                                    <div className={`p-3 rounded ${
                                        isDark ? 'bg-rose-500/20 text-rose-400' : 'bg-rose-100 text-rose-700'
                                    }`}>
                                        Error: {testResult.error}
                                    </div>
                                ) : (
                                    <>
                                        <div className={`p-3 rounded ${
                                            isDark ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-100 text-emerald-700'
                                        }`}>
                                            ✓ Best Strategy: {testResult.best_strategy}
                                            <div className="text-sm mt-1">
                                                Confidence: {(testResult.confidence * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <div>
                                            <div className={`text-xs font-semibold mb-2 ${
                                                isDark ? 'text-neutral-400' : 'text-slate-600'
                                            }`}>
                                                All Predictions:
                                            </div>
                                            <div className="space-y-2">
                                                {Object.entries(testResult.predictions || {})
                                                    .sort((a, b) => b[1] - a[1])
                                                    .map(([name, score]) => (
                                                        <div key={name} className="flex items-center gap-2">
                                                            <div className={`flex-1 h-2 rounded-full overflow-hidden ${
                                                                isDark ? 'bg-neutral-800' : 'bg-slate-200'
                                                            }`}>
                                                                <div
                                                                    className={`h-full ${
                                                                        isDark
                                                                            ? 'bg-gradient-to-r from-purple-600 to-pink-600'
                                                                            : 'bg-gradient-to-r from-emerald-500 to-teal-500'
                                                                    }`}
                                                                    style={{ width: `${score * 100}%` }}
                                                                />
                                                            </div>
                                                            <span className={`text-xs ${
                                                                isDark ? 'text-neutral-400' : 'text-slate-600'
                                                            }`}>
                                                                {(score * 100).toFixed(0)}%
                                                            </span>
                                                        </div>
                                                    ))}
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        ) : (
                            <div className={`text-center py-12 ${isDark ? 'text-neutral-500' : 'text-slate-400'}`}>
                                Configure test and click "Run Test"
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                    onClick={testResearchEngine}
                    className={`p-4 rounded-lg border font-medium transition-all text-left ${
                        isDark
                            ? 'bg-neutral-900/50 border-neutral-800 hover:border-neutral-700 text-white'
                            : 'bg-white border-slate-200 hover:border-slate-300 text-slate-900'
                    }`}
                >
                    <FileText className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                    <div className="mt-2 font-semibold">Test Research Engine</div>
                    <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                        Verify module loading
                    </div>
                </button>

                <button
                    onClick={loadLogs}
                    className={`p-4 rounded-lg border font-medium transition-all text-left ${
                        isDark
                            ? 'bg-neutral-900/50 border-neutral-800 hover:border-neutral-700 text-white'
                            : 'bg-white border-slate-200 hover:border-slate-300 text-slate-900'
                    }`}
                >
                    <RefreshCw className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                    <div className="mt-2 font-semibold">Refresh Logs</div>
                    <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                        Load latest system logs
                    </div>
                </button>

                <button
                    onClick={loadSystemInfo}
                    className={`p-4 rounded-lg border font-medium transition-all text-left ${
                        isDark
                            ? 'bg-neutral-900/50 border-neutral-800 hover:border-neutral-700 text-white'
                            : 'bg-white border-slate-200 hover:border-slate-300 text-slate-900'
                    }`}
                >
                    <Zap className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                    <div className="mt-2 font-semibold">System Status</div>
                    <div className={`text-sm ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                        Refresh health check
                    </div>
                </button>
            </div>

            {/* System Logs */}
            <div className={`p-6 rounded-xl border theme-transition ${
                isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
            }`}>
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <Bug className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
                        <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            System Logs
                        </h3>
                    </div>
                    <button
                        onClick={loadLogs}
                        className={`p-2 rounded-lg transition-all ${
                            isDark ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'
                        }`}
                    >
                        <RefreshCw size={18} />
                    </button>
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                    {logs.length > 0 ? (
                        logs.map((log, idx) => <LogEntry key={idx} log={log} />)
                    ) : (
                        <div className={`text-center py-8 ${isDark ? 'text-neutral-500' : 'text-slate-400'}`}>
                            No logs available
                        </div>
                    )}
                </div>
            </div>

            {/* Model Weights Viewer */}
            {modelWeights && (
                <div className={`p-6 rounded-xl border theme-transition ${
                    isDark ? 'bg-neutral-950/50 border-neutral-800' : 'bg-white border-slate-200 shadow-md'
                }`}>
                    <h3 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        Model Weights: {modelWeights.model_name}
                    </h3>
                    <pre className={`p-4 rounded-lg overflow-auto text-sm font-mono ${
                        isDark ? 'bg-black/50 text-neutral-300' : 'bg-slate-50 text-slate-700'
                    }`}>
                        {JSON.stringify(modelWeights.weights, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
};

export default DebugTab;
