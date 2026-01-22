import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Clock, CheckCircle2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import LoadingSpinner from './LoadingSpinner';

const API_BASE_URL = 'http://localhost:8000';

export default function AnalyticsView() {
  const { isDark } = useTheme();
  const [tasks, setTasks] = useState([]);
  const [timers, setTimers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    totalTime: 0,
    avgAccuracy: 0
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [tasksRes, timersRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/tasks/`),
        axios.get(`${API_BASE_URL}/api/timer/`)
      ]);
      setTasks(tasksRes.data);
      setTimers(timersRes.data);
      
      // Calculate stats
      const completed = tasksRes.data.filter(t => t.status === 'completed');
      const totalTime = completed.reduce((sum, t) => sum + (t.actual_minutes || t.estimated_minutes), 0);
      const accuracies = completed.filter(t => t.completion_accuracy).map(t => t.completion_accuracy);
      const avgAccuracy = accuracies.length > 0 
        ? accuracies.reduce((a, b) => a + b, 0) / accuracies.length 
        : 0;

      setStats({
        totalTasks: tasksRes.data.length,
        completedTasks: completed.length,
        totalTime,
        avgAccuracy: avgAccuracy * 100
      });
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading analytics..." />;
  }

  // Prepare chart data
  const completionData = tasks
    .filter(t => t.completed_at)
    .map(t => ({
      date: new Date(t.completed_at).toLocaleDateString(),
      tasks: 1
    }))
    .reduce((acc, curr) => {
      const existing = acc.find(a => a.date === curr.date);
      if (existing) {
        existing.tasks += 1;
      } else {
        acc.push(curr);
      }
      return acc;
    }, [])
    .slice(-7); // Last 7 days

  const timeData = timers
    .filter(t => t.completed_at)
    .map(t => ({
      date: new Date(t.completed_at).toLocaleDateString(),
      minutes: Math.floor((t.actual_seconds || 0) / 60)
    }))
    .reduce((acc, curr) => {
      const existing = acc.find(a => a.date === curr.date);
      if (existing) {
        existing.minutes += curr.minutes;
      } else {
        acc.push(curr);
      }
      return acc;
    }, [])
    .slice(-7);

  return (
    <div className="space-y-6">
      <div>
        <h1 className={`text-3xl font-bold mb-2 ${
          isDark ? 'text-white' : 'text-slate-900'
        }`}>
          Analytics & Insights
        </h1>
        <p className={`text-sm ${
          isDark ? 'text-neutral-400' : 'text-slate-600'
        }`}>
          Track your productivity and see how you're improving
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Tasks"
          value={stats.totalTasks}
          icon={BarChart3}
          isDark={isDark}
        />
        <StatCard
          title="Completed"
          value={stats.completedTasks}
          icon={CheckCircle2}
          isDark={isDark}
        />
        <StatCard
          title="Total Time"
          value={`${Math.floor(stats.totalTime / 60)}h`}
          icon={Clock}
          isDark={isDark}
        />
        <StatCard
          title="Accuracy"
          value={`${stats.avgAccuracy.toFixed(0)}%`}
          icon={TrendingUp}
          isDark={isDark}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task Completion Chart */}
        <div className={`rounded-xl p-6 border ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <h2 className={`text-lg font-semibold mb-4 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Tasks Completed (Last 7 Days)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={completionData}>
              <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#404040' : '#e2e8f0'} />
              <XAxis dataKey="date" stroke={isDark ? '#a3a3a3' : '#64748b'} />
              <YAxis stroke={isDark ? '#a3a3a3' : '#64748b'} />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#171717' : '#ffffff',
                  border: isDark ? '1px solid #404040' : '1px solid #e2e8f0',
                  color: isDark ? '#ffffff' : '#1e293b'
                }}
              />
              <Bar
                dataKey="tasks"
                fill={isDark ? '#a855f7' : '#10b981'}
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Time Tracking Chart */}
        <div className={`rounded-xl p-6 border ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <h2 className={`text-lg font-semibold mb-4 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Focus Time (Last 7 Days)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeData}>
              <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#404040' : '#e2e8f0'} />
              <XAxis dataKey="date" stroke={isDark ? '#a3a3a3' : '#64748b'} />
              <YAxis stroke={isDark ? '#a3a3a3' : '#64748b'} />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#171717' : '#ffffff',
                  border: isDark ? '1px solid #404040' : '1px solid #e2e8f0',
                  color: isDark ? '#ffffff' : '#1e293b'
                }}
              />
              <Line
                type="monotone"
                dataKey="minutes"
                stroke={isDark ? '#ec4899' : '#14b8a6'}
                strokeWidth={2}
                dot={{ fill: isDark ? '#ec4899' : '#14b8a6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, isDark }) {
  return (
    <div className={`rounded-xl p-6 border ${
      isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
    }`}>
      <div className="flex items-center justify-between mb-2">
        <Icon className={isDark ? 'text-purple-400' : 'text-emerald-600'} size={24} />
      </div>
      <div className={`text-3xl font-bold mb-1 ${
        isDark ? 'text-white' : 'text-slate-900'
      }`}>
        {value}
      </div>
      <div className={`text-sm ${
        isDark ? 'text-neutral-400' : 'text-slate-600'
      }`}>
        {title}
      </div>
    </div>
  );
}
