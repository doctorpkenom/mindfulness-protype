import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Square, Clock, Plus } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function TimerView() {
  const { isDark } = useTheme();
  const [activeTimers, setActiveTimers] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState({});
  const [timerHours, setTimerHours] = useState(0);
  const [timerMinutes, setTimerMinutes] = useState(25);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [tasks, setTasks] = useState([]);
  const [showNewTimerForm, setShowNewTimerForm] = useState(false);
  const intervalRef = useRef(null);

  const handleTimerComplete = async (timerId) => {
    // Automatically stop timer when it reaches zero
    try {
      const timer = activeTimers.find(t => t.id === timerId);
      await axios.post(`${API_BASE_URL}/api/timer/${timerId}/stop`);
      await loadActiveTimers();
      // Show notification or alert
      if (timer) {
        const task = timer.task_id ? tasks.find(t => t.id === timer.task_id) : null;
        const message = task 
          ? `Timer completed! "${task.title}" finished.`
          : 'Focus session complete!';
        alert(message);
      }
    } catch (error) {
      console.error('Failed to complete timer:', error);
    }
  };

  // Load timers and tasks on mount
  useEffect(() => {
    loadActiveTimers();
    loadTasks();
  }, []);

  // Real-time countdown for all active timers
  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // Set up interval to update every second
    intervalRef.current = setInterval(() => {
      setActiveTimers(prevTimers => {
        prevTimers.forEach(timer => {
          if (timer.status === 'active') {
            const now = new Date();
            // Parse started_at - handle both ISO string and Date object
            const startedAt = timer.started_at instanceof Date 
              ? timer.started_at 
              : new Date(timer.started_at);
            
            if (!isNaN(startedAt.getTime()) && timer.duration_seconds) {
              const elapsed = Math.floor((now - startedAt) / 1000);
              const remaining = Math.max(0, timer.duration_seconds - elapsed);
              
              // Update time remaining state
              setTimeRemaining(prev => ({
                ...prev,
                [timer.id]: remaining
              }));

              // If timer reached zero, mark as completed
              if (remaining === 0) {
                handleTimerComplete(timer.id);
              }
            }
          } else if (timer.status === 'paused') {
            // For paused timers, use the stored remaining time
            const remaining = timer.actual_seconds || timer.duration_seconds;
            setTimeRemaining(prev => ({
              ...prev,
              [timer.id]: remaining
            }));
          }
        });
        return prevTimers;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [activeTimers.length, tasks]);

  const loadActiveTimers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/timer/active`);
      const timers = response.data || [];
      setActiveTimers(timers);
      
      // Calculate initial time remaining for each timer
      const newTimeRemaining = {};
      timers.forEach(timer => {
        if (timer.status === 'active') {
          // Parse started_at - handle both ISO string and Date object
          const startedAt = timer.started_at instanceof Date 
            ? timer.started_at 
            : new Date(timer.started_at);
          
          // Ensure we have valid dates
          if (isNaN(startedAt.getTime())) {
            console.error('Invalid started_at date:', timer.started_at);
            newTimeRemaining[timer.id] = timer.duration_seconds;
          } else {
            const now = new Date();
            const elapsed = Math.floor((now - startedAt) / 1000);
            const remaining = Math.max(0, timer.duration_seconds - elapsed);
            newTimeRemaining[timer.id] = remaining;
            console.log(`Timer ${timer.id}: duration=${timer.duration_seconds}s, elapsed=${elapsed}s, remaining=${remaining}s`);
          }
        } else if (timer.status === 'paused') {
          // For paused timers, use stored remaining time from actual_seconds
          newTimeRemaining[timer.id] = timer.actual_seconds || timer.duration_seconds;
        }
      });
      setTimeRemaining(newTimeRemaining);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Failed to load timers:', error);
      }
      setActiveTimers([]);
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

  const handleStart = async (taskId = null, customDuration = null) => {
    try {
      let durationSeconds;
      
      if (customDuration !== null) {
        // If custom duration provided (from task), use it in minutes
        durationSeconds = customDuration * 60;
      } else {
        // Calculate from hours, minutes, seconds
        durationSeconds = (timerHours * 3600) + (timerMinutes * 60) + timerSeconds;
      }
      
      console.log(`Starting timer: ${timerHours}h ${timerMinutes}m ${timerSeconds}s (${durationSeconds} seconds)`);
      
      if (!durationSeconds || durationSeconds <= 0) {
        alert('Please set a valid duration (at least 1 second)');
        return;
      }
      
      const response = await axios.post(`${API_BASE_URL}/api/timer/start`, {
        task_id: taskId,
        duration_seconds: durationSeconds
      });
      
      console.log('Timer created:', response.data);
      console.log('Timer details:', {
        id: response.data.id,
        duration_seconds: response.data.duration_seconds,
        started_at: response.data.started_at,
        status: response.data.status
      });
      
      // Small delay to ensure backend has saved the timer
      await new Promise(resolve => setTimeout(resolve, 200));
      await loadActiveTimers();
      setShowNewTimerForm(false);
      
      // Reset timer inputs
      setTimerHours(0);
      setTimerMinutes(25);
      setTimerSeconds(0);
      
      // Force immediate update of time remaining for the new timer
      if (response.data) {
        const timer = response.data;
        const startedAt = new Date(timer.started_at);
        const now = new Date();
        const elapsed = Math.floor((now - startedAt) / 1000);
        const remaining = Math.max(0, timer.duration_seconds - elapsed);
        
        setTimeRemaining(prev => ({
          ...prev,
          [timer.id]: remaining
        }));
        
        console.log(`Initial time remaining for timer ${timer.id}: ${remaining}s (${timer.duration_seconds}s - ${elapsed}s elapsed)`);
      }
    } catch (error) {
      console.error('Failed to start timer:', error);
      alert(error.response?.data?.detail || 'Failed to start timer');
    }
  };

  const handlePause = async (timerId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/timer/${timerId}/pause`);
      await loadActiveTimers();
    } catch (error) {
      console.error('Failed to pause timer:', error);
      alert(error.response?.data?.detail || 'Failed to pause timer');
    }
  };

  const handleResume = async (timerId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/timer/${timerId}/resume`);
      await loadActiveTimers();
    } catch (error) {
      console.error('Failed to resume timer:', error);
      alert(error.response?.data?.detail || 'Failed to resume timer');
    }
  };

  const handleStop = async (timerId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/timer/${timerId}/stop`);
      await loadActiveTimers();
      setTimeRemaining(prev => {
        const newState = { ...prev };
        delete newState[timerId];
        return newState;
      });
    } catch (error) {
      console.error('Failed to stop timer:', error);
      alert(error.response?.data?.detail || 'Failed to stop timer');
    }
  };

  const formatTime = (seconds) => {
    if (seconds === undefined || seconds === null) return '00:00:00';
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-3xl font-bold mb-2 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Timers
          </h1>
          <p className={`text-sm ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            Run multiple timers simultaneously
          </p>
        </div>
        <button
          onClick={() => setShowNewTimerForm(!showNewTimerForm)}
          className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
            isDark
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
              : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white'
          }`}
        >
          <Plus size={20} />
          New Timer
        </button>
      </div>

      {/* New Timer Form */}
      {showNewTimerForm && (
        <div className={`rounded-xl p-6 border ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <div className="space-y-6">
            <div>
              <label className={`block text-sm font-medium mb-4 text-center ${
                isDark ? 'text-neutral-300' : 'text-slate-700'
              }`}>
                Set Timer Duration
              </label>
              
              {/* Time Picker - Phone Style */}
              <div className="flex items-center justify-center gap-4">
                {/* Hours */}
                <div className="flex flex-col items-center">
                  <label className={`text-xs font-medium mb-2 ${
                    isDark ? 'text-neutral-400' : 'text-slate-500'
                  }`}>
                    Hours
                  </label>
                  <div className="flex flex-col gap-1">
                    <button
                      type="button"
                      onClick={() => setTimerHours(Math.min(23, timerHours + 1))}
                      className={`px-3 py-1 rounded ${
                        isDark 
                          ? 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300' 
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      } transition-colors`}
                    >
                      ↑
                    </button>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={timerHours}
                      onChange={(e) => {
                        const val = parseInt(e.target.value) || 0;
                        setTimerHours(Math.max(0, Math.min(23, val)));
                      }}
                      className={`w-16 px-3 py-2 rounded-lg border text-center text-2xl font-mono font-bold ${
                        isDark
                          ? 'bg-neutral-900 border-neutral-700 text-white'
                          : 'bg-slate-50 border-slate-300 text-slate-900'
                      } focus:outline-none focus:ring-2 ${
                        isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setTimerHours(Math.max(0, timerHours - 1))}
                      className={`px-3 py-1 rounded ${
                        isDark 
                          ? 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300' 
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      } transition-colors`}
                    >
                      ↓
                    </button>
                  </div>
                </div>
                
                <span className={`text-3xl font-bold mt-8 ${
                  isDark ? 'text-neutral-500' : 'text-slate-400'
                }`}>
                  :
                </span>
                
                {/* Minutes */}
                <div className="flex flex-col items-center">
                  <label className={`text-xs font-medium mb-2 ${
                    isDark ? 'text-neutral-400' : 'text-slate-500'
                  }`}>
                    Minutes
                  </label>
                  <div className="flex flex-col gap-1">
                    <button
                      type="button"
                      onClick={() => setTimerMinutes(Math.min(59, timerMinutes + 1))}
                      className={`px-3 py-1 rounded ${
                        isDark 
                          ? 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300' 
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      } transition-colors`}
                    >
                      ↑
                    </button>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={timerMinutes}
                      onChange={(e) => {
                        const val = parseInt(e.target.value) || 0;
                        setTimerMinutes(Math.max(0, Math.min(59, val)));
                      }}
                      className={`w-16 px-3 py-2 rounded-lg border text-center text-2xl font-mono font-bold ${
                        isDark
                          ? 'bg-neutral-900 border-neutral-700 text-white'
                          : 'bg-slate-50 border-slate-300 text-slate-900'
                      } focus:outline-none focus:ring-2 ${
                        isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setTimerMinutes(Math.max(0, timerMinutes - 1))}
                      className={`px-3 py-1 rounded ${
                        isDark 
                          ? 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300' 
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      } transition-colors`}
                    >
                      ↓
                    </button>
                  </div>
                </div>
                
                <span className={`text-3xl font-bold mt-8 ${
                  isDark ? 'text-neutral-500' : 'text-slate-400'
                }`}>
                  :
                </span>
                
                {/* Seconds */}
                <div className="flex flex-col items-center">
                  <label className={`text-xs font-medium mb-2 ${
                    isDark ? 'text-neutral-400' : 'text-slate-500'
                  }`}>
                    Seconds
                  </label>
                  <div className="flex flex-col gap-1">
                    <button
                      type="button"
                      onClick={() => setTimerSeconds(Math.min(59, timerSeconds + 1))}
                      className={`px-3 py-1 rounded ${
                        isDark 
                          ? 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300' 
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      } transition-colors`}
                    >
                      ↑
                    </button>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={timerSeconds}
                      onChange={(e) => {
                        const val = parseInt(e.target.value) || 0;
                        setTimerSeconds(Math.max(0, Math.min(59, val)));
                      }}
                      className={`w-16 px-3 py-2 rounded-lg border text-center text-2xl font-mono font-bold ${
                        isDark
                          ? 'bg-neutral-900 border-neutral-700 text-white'
                          : 'bg-slate-50 border-slate-300 text-slate-900'
                      } focus:outline-none focus:ring-2 ${
                        isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setTimerSeconds(Math.max(0, timerSeconds - 1))}
                      className={`px-3 py-1 rounded ${
                        isDark 
                          ? 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300' 
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      } transition-colors`}
                    >
                      ↓
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Total Duration Display */}
              <div className="text-center mt-4">
                <p className={`text-sm ${
                  isDark ? 'text-neutral-400' : 'text-slate-600'
                }`}>
                  Total: {formatTime((timerHours * 3600) + (timerMinutes * 60) + timerSeconds)}
                </p>
              </div>
            </div>
            
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => handleStart(null)}
                disabled={(timerHours === 0 && timerMinutes === 0 && timerSeconds === 0)}
                className={`px-8 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                  (timerHours === 0 && timerMinutes === 0 && timerSeconds === 0)
                    ? isDark
                      ? 'bg-neutral-800 text-neutral-600 cursor-not-allowed'
                      : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    : isDark
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                      : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white'
                }`}
              >
                <Play size={20} />
                Start Timer
              </button>
              <button
                onClick={() => {
                  setShowNewTimerForm(false);
                  setTimerHours(0);
                  setTimerMinutes(25);
                  setTimerSeconds(0);
                }}
                className={`px-6 py-3 rounded-lg font-medium border ${
                  isDark
                    ? 'border-neutral-700 text-neutral-300 hover:bg-neutral-900'
                    : 'border-slate-300 text-slate-700 hover:bg-slate-100'
                }`}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Active Timers Display */}
      {activeTimers.length > 0 ? (
        <div className="space-y-4">
          {activeTimers.map(timer => {
            // Get remaining time - prefer state, fallback to duration, ensure it's a number
            let remaining = timeRemaining[timer.id];
            if (remaining === undefined || remaining === null) {
              if (timer.status === 'paused') {
                remaining = timer.actual_seconds || timer.duration_seconds || 0;
              } else {
                remaining = timer.duration_seconds || 0;
              }
            }
            remaining = Math.max(0, Math.floor(remaining)); // Ensure it's a valid positive integer
            const isPaused = timer.status === 'paused';
            const task = timer.task_id ? tasks.find(t => t.id === timer.task_id) : null;
            
            return (
              <div key={timer.id} className={`rounded-xl p-6 border ${
                isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
              }`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    {task ? (
                      <h3 className={`font-semibold mb-1 ${
                        isDark ? 'text-white' : 'text-slate-900'
                      }`}>
                        {task.title}
                      </h3>
                    ) : (
                      <h3 className={`font-semibold mb-1 ${
                        isDark ? 'text-neutral-400' : 'text-slate-600'
                      }`}>
                        Focus Timer
                      </h3>
                    )}
                    {task && (
                      <p className={`text-xs ${
                        isDark ? 'text-neutral-500' : 'text-slate-500'
                      }`}>
                        Estimated: {task.estimated_minutes} min
                      </p>
                    )}
                  </div>
                  {isPaused && (
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      isDark ? 'bg-neutral-800 text-neutral-400' : 'bg-slate-100 text-slate-600'
                    }`}>
                      Paused
                    </span>
                  )}
                </div>
                
                <div className={`text-6xl font-mono font-bold mb-6 text-center ${
                  isDark 
                    ? remaining <= 60 ? 'text-rose-400' : 'text-purple-400'
                    : remaining <= 60 ? 'text-rose-500' : 'text-emerald-600'
                }`}>
                  {formatTime(remaining)}
                </div>
                
                <div className="flex gap-3 justify-center">
                  {isPaused ? (
                    <button
                      onClick={() => handleResume(timer.id)}
                      className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                        isDark
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                          : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white'
                      }`}
                    >
                      <Play size={20} />
                      Resume
                    </button>
                  ) : (
                    <button
                      onClick={() => handlePause(timer.id)}
                      className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                        isDark
                          ? 'bg-neutral-800 hover:bg-neutral-700 text-white border border-neutral-700'
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300'
                      }`}
                    >
                      <Pause size={20} />
                      Pause
                    </button>
                  )}
                  <button
                    onClick={() => handleStop(timer.id)}
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
            );
          })}
        </div>
      ) : (
        <div className={`rounded-xl p-12 border text-center ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <Clock size={48} className={`mx-auto mb-4 ${
            isDark ? 'text-neutral-700' : 'text-slate-300'
          }`} />
          <p className={`text-lg ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            No active timers
          </p>
          <p className={`text-sm mt-2 ${
            isDark ? 'text-neutral-500' : 'text-slate-500'
          }`}>
            Click "New Timer" to start a focus session
          </p>
        </div>
      )}

      {/* Quick Start with Task */}
      {tasks.length > 0 && (
        <div className={`rounded-xl p-6 border ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <h2 className={`text-lg font-semibold mb-4 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Quick Start with Task
          </h2>
          <div className="space-y-2">
            {tasks.filter(t => t.status === 'pending' || t.status === 'scheduled').slice(0, 5).map(task => (
              <button
                key={task.id}
                onClick={() => handleStart(task.id, task.estimated_minutes)}
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
                  <div className="flex items-center gap-2">
                    <span className={`text-xs ${
                      isDark ? 'text-neutral-500' : 'text-slate-500'
                    }`}>
                      {task.estimated_minutes} min
                    </span>
                    <Clock size={16} className={isDark ? 'text-neutral-500' : 'text-slate-400'} />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
