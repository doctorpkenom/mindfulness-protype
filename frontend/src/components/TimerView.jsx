import React, { useState, useEffect } from 'react';
import { Play, Pause, Square, Clock } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function TimerView() {
  const { isDark } = useTheme();
  const [activeTimer, setActiveTimer] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [duration, setDuration] = useState(1500); // 25 minutes default
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    loadActiveTimer();
    loadTasks();
    const interval = setInterval(() => {
      if (activeTimer && activeTimer.status === 'active') {
        const elapsed = Math.floor((new Date() - new Date(activeTimer.started_at)) / 1000);
        const remaining = Math.max(0, activeTimer.duration_seconds - elapsed);
        setTimeRemaining(remaining);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [activeTimer]);

  const loadActiveTimer = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/timer/active`);
      setActiveTimer(response.data);
      const elapsed = Math.floor((new Date() - new Date(response.data.started_at)) / 1000);
      setTimeRemaining(Math.max(0, response.data.duration_seconds - elapsed));
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Failed to load timer:', error);
      }
    }
  };

  const loadTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/tasks/?status_filter=pending`);
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const handleStart = async (taskId = null) => {
    try {
      await axios.post(`${API_BASE_URL}/api/timer/start`, {
        task_id: taskId,
        duration_seconds: duration
      });
      await loadActiveTimer();
    } catch (error) {
      console.error('Failed to start timer:', error);
      alert(error.response?.data?.detail || 'Failed to start timer');
    }
  };

  const handleStop = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/timer/${activeTimer.id}/stop`);
      await loadActiveTimer();
      setTimeRemaining(0);
    } catch (error) {
      console.error('Failed to stop timer:', error);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className={`text-3xl font-bold mb-2 ${
          isDark ? 'text-white' : 'text-slate-900'
        }`}>
          Focus Timer
        </h1>
        <p className={`text-sm ${
          isDark ? 'text-neutral-400' : 'text-slate-600'
        }`}>
          Track your work sessions and improve focus
        </p>
      </div>

      {/* Timer Display */}
      <div className={`rounded-xl p-12 border text-center ${
        isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
      }`}>
        <div className={`text-7xl font-mono font-bold mb-6 ${
          isDark ? 'text-purple-400' : 'text-emerald-600'
        }`}>
          {formatTime(timeRemaining || duration)}
        </div>

        {!activeTimer ? (
          <div className="space-y-4">
            <div>
              <label className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-neutral-300' : 'text-slate-700'
              }`}>
                Duration (minutes)
              </label>
              <input
                type="number"
                min="1"
                value={Math.floor(duration / 60)}
                onChange={(e) => setDuration(parseInt(e.target.value) * 60)}
                className={`w-full max-w-xs mx-auto px-4 py-2 rounded-lg border ${
                  isDark
                    ? 'bg-neutral-900 border-neutral-700 text-white'
                    : 'bg-slate-50 border-slate-300 text-slate-900'
                }`}
              />
            </div>
            <button
              onClick={() => handleStart()}
              className={`px-8 py-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 mx-auto ${
                isDark
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/30'
                  : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg shadow-emerald-500/20'
              }`}
            >
              <Play size={24} />
              Start Timer
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {activeTimer.task_id && (
              <p className={`text-sm ${
                isDark ? 'text-neutral-400' : 'text-slate-600'
              }`}>
                Task: {tasks.find(t => t.id === activeTimer.task_id)?.title || 'Unknown'}
              </p>
            )}
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleStop}
                className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                  isDark
                    ? 'bg-rose-600 hover:bg-rose-700 text-white'
                    : 'bg-rose-500 hover:bg-rose-600 text-white'
                }`}
              >
                <Square size={20} />
                Stop
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Quick Start with Task */}
      {tasks.length > 0 && !activeTimer && (
        <div className={`rounded-xl p-6 border ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <h2 className={`text-lg font-semibold mb-4 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Start Timer for Task
          </h2>
          <div className="space-y-2">
            {tasks.slice(0, 5).map(task => (
              <button
                key={task.id}
                onClick={() => handleStart(task.id)}
                className={`w-full p-3 rounded-lg border text-left transition-all ${
                  isDark
                    ? 'bg-neutral-900 border-neutral-800 hover:border-purple-500'
                    : 'bg-slate-50 border-slate-200 hover:border-emerald-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={isDark ? 'text-white' : 'text-slate-900'}>
                    {task.title}
                  </span>
                  <Clock size={16} className={isDark ? 'text-neutral-500' : 'text-slate-400'} />
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
