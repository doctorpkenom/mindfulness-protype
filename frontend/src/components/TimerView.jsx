import axios from 'axios';
import { Check, Clock, Edit2, Pause, Play, Plus, Square, X } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';

const API_BASE_URL = 'http://localhost:8000';

export default function TimerView() {
  const { isDark } = useTheme();
  const [activeTimers, setActiveTimers] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState({});
  const [timerHours, setTimerHours] = useState(0);
  const [timerMinutes, setTimerMinutes] = useState(25);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [timerName, setTimerName] = useState('');
  const [tasks, setTasks] = useState([]);
  const [showNewTimerForm, setShowNewTimerForm] = useState(false);
  const [focusedInput, setFocusedInput] = useState(null); // Track which input is focused
  const [editingTimerName, setEditingTimerName] = useState(null); // Track which timer name is being edited
  const intervalRef = useRef(null);
  const hoursInputRef = useRef(null);
  const minutesInputRef = useRef(null);
  const secondsInputRef = useRef(null);

  const handleTimerComplete = async (timerId) => {
    // Automatically stop timer when it reaches zero
    try {
      const timer = activeTimers.find(t => t.id === timerId);
      await axios.post(`${API_BASE_URL}/api/timer/${timerId}/stop`);
      await loadActiveTimers();
      // Show notification or alert
      if (timer) {
        const task = timer.task_id ? tasks.find(t => t.id === timer.task_id) : null;
        const timerDisplayName = timer.name || (task ? task.title : 'Timer');
        const message = `Timer "${timerDisplayName}" completed!`;
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
            let startedAt;
            if (timer.started_at instanceof Date) {
              startedAt = timer.started_at;
            } else if (typeof timer.started_at === 'string') {
              // Parse ISO string - if no timezone info, assume UTC
              let dateStr = timer.started_at;
              // If the string doesn't end with Z or timezone, it might be UTC from backend
              if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
                // Assume UTC if no timezone specified (backend uses UTC)
                dateStr = dateStr + 'Z';
              }
              startedAt = new Date(dateStr);
            } else {
              startedAt = new Date(timer.started_at);
            }
            
            if (!isNaN(startedAt.getTime()) && timer.duration_seconds) {
              // Calculate elapsed time in seconds using getTime() for accurate millisecond calculation
              const elapsed = Math.floor((now.getTime() - startedAt.getTime()) / 1000);
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
          let startedAt;
          if (timer.started_at instanceof Date) {
            startedAt = timer.started_at;
          } else if (typeof timer.started_at === 'string') {
            // Parse ISO string - if no timezone info, assume UTC
            let dateStr = timer.started_at;
            // If the string doesn't end with Z or timezone, it might be UTC from backend
            if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
              // Assume UTC if no timezone specified (backend uses UTC)
              dateStr = dateStr + 'Z';
            }
            startedAt = new Date(dateStr);
          } else {
            startedAt = new Date(timer.started_at);
          }
          
          // Ensure we have valid dates
          if (isNaN(startedAt.getTime())) {
            console.error('Invalid started_at date:', timer.started_at);
            newTimeRemaining[timer.id] = timer.duration_seconds;
          } else {
            const now = new Date();
            // Calculate elapsed time in seconds
            const elapsed = Math.floor((now.getTime() - startedAt.getTime()) / 1000);
            const remaining = Math.max(0, timer.duration_seconds - elapsed);
            newTimeRemaining[timer.id] = remaining;
            console.log(`Timer ${timer.id}: duration=${timer.duration_seconds}s, started_at="${timer.started_at}", startedAt_parsed=${startedAt.toISOString()}, now=${now.toISOString()}, elapsed=${elapsed}s, remaining=${remaining}s`);
            console.log(`  Time difference: ${now.getTime()} - ${startedAt.getTime()} = ${now.getTime() - startedAt.getTime()}ms = ${elapsed}s`);
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
        console.log(`Starting timer from task: ${customDuration} minutes (${durationSeconds} seconds)`);
      } else {
        // Read values directly from input refs if they exist, otherwise use state
        // This ensures we get the current value even if input is focused
        let hours = timerHours || 0;
        let minutes = timerMinutes || 0;
        let seconds = timerSeconds || 0;
        
        // If inputs exist, read their current values
        if (hoursInputRef.current) {
          const hoursVal = parseInt(hoursInputRef.current.value) || 0;
          if (!isNaN(hoursVal)) {
            hours = Math.max(0, Math.min(23, hoursVal));
            setTimerHours(hours);
          }
        }
        if (minutesInputRef.current) {
          const minutesVal = parseInt(minutesInputRef.current.value) || 0;
          if (!isNaN(minutesVal)) {
            minutes = Math.max(0, Math.min(59, minutesVal));
            setTimerMinutes(minutes);
          }
        }
        if (secondsInputRef.current) {
          const secondsVal = parseInt(secondsInputRef.current.value) || 0;
          if (!isNaN(secondsVal)) {
            seconds = Math.max(0, Math.min(59, secondsVal));
            setTimerSeconds(seconds);
          }
        }
        
        durationSeconds = (hours * 3600) + (minutes * 60) + seconds;
        
        console.log(`Starting timer from inputs: ${hours}h ${minutes}m ${seconds}s (${durationSeconds} seconds)`);
        console.log(`State values: timerHours=${timerHours}, timerMinutes=${timerMinutes}, timerSeconds=${timerSeconds}`);
        console.log(`Input values: hours=${hours}, minutes=${minutes}, seconds=${seconds}`);
      }
      
      if (!durationSeconds || durationSeconds <= 0) {
        alert('Please set a valid duration (at least 1 second)');
        return;
      }
      
      console.log(`Sending to backend: duration_seconds=${durationSeconds}`);
      
      const response = await axios.post(`${API_BASE_URL}/api/timer/start`, {
        task_id: taskId,
        duration_seconds: durationSeconds,
        name: timerName || null
      });
      
      console.log('Timer created:', response.data);
      console.log('Backend returned duration_seconds:', response.data.duration_seconds);
      console.log('Timer details:', {
        id: response.data.id,
        duration_seconds: response.data.duration_seconds,
        started_at: response.data.started_at,
        status: response.data.status
      });
      
      // Verify the backend received the correct duration
      if (response.data.duration_seconds !== durationSeconds) {
        console.error(`Duration mismatch! Sent: ${durationSeconds}, Received: ${response.data.duration_seconds}`);
        alert(`Warning: Timer duration mismatch. Expected ${durationSeconds}s but got ${response.data.duration_seconds}s`);
      }
      
      // Small delay to ensure backend has saved the timer
      await new Promise(resolve => setTimeout(resolve, 200));
      await loadActiveTimers();
      setShowNewTimerForm(false);
      
      // Reset timer inputs
      setTimerHours(0);
      setTimerMinutes(25);
      setTimerSeconds(0);
      setFocusedInput(null);
      
      // Force immediate update of time remaining for the new timer
      if (response.data) {
        const timer = response.data;
        // Parse started_at - if no timezone info, assume UTC
        let dateStr = timer.started_at;
        if (typeof dateStr === 'string' && !dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
          dateStr = dateStr + 'Z';
        }
        const startedAt = new Date(dateStr);
        const now = new Date();
        // Use getTime() for accurate millisecond calculation
        const elapsed = Math.floor((now.getTime() - startedAt.getTime()) / 1000);
        const remaining = Math.max(0, timer.duration_seconds - elapsed);
        
        setTimeRemaining(prev => ({
          ...prev,
          [timer.id]: remaining
        }));
        
        console.log(`Initial time remaining for timer ${timer.id}: ${remaining}s (${timer.duration_seconds}s - ${elapsed}s elapsed)`);
        console.log(`  started_at: ${timer.started_at}, parsed: ${startedAt.toISOString()}, now: ${now.toISOString()}`);
        console.log(`  Time difference: ${now.getTime()} - ${startedAt.getTime()} = ${now.getTime() - startedAt.getTime()}ms = ${elapsed}s`);
      }
    } catch (error) {
      console.error('Failed to start timer:', error);
      console.error('Error details:', error.response?.data);
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

  const handleUpdateTimerName = async (timerId, newName) => {
    try {
      await axios.put(`${API_BASE_URL}/api/timer/${timerId}`, {
        name: newName || null
      });
      await loadActiveTimers();
      setEditingTimerName(null);
    } catch (error) {
      console.error('Failed to update timer name:', error);
      alert(error.response?.data?.detail || 'Failed to update timer name');
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
              <label className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-neutral-300' : 'text-slate-700'
              }`}>
                Timer Name (Optional)
              </label>
              <input
                type="text"
                value={timerName}
                onChange={(e) => setTimerName(e.target.value)}
                placeholder="e.g., Focus Session, Break Time..."
                className={`w-full px-4 py-2 rounded-lg border ${
                  isDark
                    ? 'bg-neutral-900 border-neutral-700 text-white placeholder-neutral-500'
                    : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400'
                } focus:outline-none focus:ring-2 ${
                  isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                }`}
              />
            </div>
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
                      ref={hoursInputRef}
                      type="text"
                      value={focusedInput === 'hours' ? timerHours.toString() : timerHours.toString().padStart(2, '0')}
                      onChange={(e) => {
                        const inputVal = e.target.value;
                        // Allow empty input while typing
                        if (inputVal === '') {
                          setTimerHours(0);
                          return;
                        }
                        const val = parseInt(inputVal);
                        if (!isNaN(val)) {
                          setTimerHours(Math.max(0, Math.min(23, val)));
                        }
                      }}
                      onFocus={() => setFocusedInput('hours')}
                      onBlur={(e) => {
                        setFocusedInput(null);
                        // Ensure it's formatted and valid on blur
                        const inputVal = e.target.value;
                        const val = inputVal === '' ? 0 : (parseInt(inputVal) || 0);
                        const clampedVal = Math.max(0, Math.min(23, val));
                        setTimerHours(clampedVal);
                        console.log(`Hours input blurred: "${inputVal}" -> ${clampedVal}`);
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
                      ref={minutesInputRef}
                      type="text"
                      value={focusedInput === 'minutes' ? timerMinutes.toString() : timerMinutes.toString().padStart(2, '0')}
                      onChange={(e) => {
                        const inputVal = e.target.value;
                        // Allow empty input while typing
                        if (inputVal === '') {
                          setTimerMinutes(0);
                          return;
                        }
                        const val = parseInt(inputVal);
                        if (!isNaN(val)) {
                          setTimerMinutes(Math.max(0, Math.min(59, val)));
                        }
                      }}
                      onFocus={() => setFocusedInput('minutes')}
                      onBlur={(e) => {
                        setFocusedInput(null);
                        // Ensure it's formatted and valid on blur
                        const inputVal = e.target.value;
                        const val = inputVal === '' ? 0 : (parseInt(inputVal) || 0);
                        const clampedVal = Math.max(0, Math.min(59, val));
                        setTimerMinutes(clampedVal);
                        console.log(`Minutes input blurred: "${inputVal}" -> ${clampedVal}`);
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
                      ref={secondsInputRef}
                      type="text"
                      value={focusedInput === 'seconds' ? timerSeconds.toString() : timerSeconds.toString().padStart(2, '0')}
                      onChange={(e) => {
                        const inputVal = e.target.value;
                        // Allow empty input while typing
                        if (inputVal === '') {
                          setTimerSeconds(0);
                          return;
                        }
                        const val = parseInt(inputVal);
                        if (!isNaN(val)) {
                          setTimerSeconds(Math.max(0, Math.min(59, val)));
                        }
                      }}
                      onFocus={() => setFocusedInput('seconds')}
                      onBlur={(e) => {
                        setFocusedInput(null);
                        // Ensure it's formatted and valid on blur
                        const inputVal = e.target.value;
                        const val = inputVal === '' ? 0 : (parseInt(inputVal) || 0);
                        const clampedVal = Math.max(0, Math.min(59, val));
                        setTimerSeconds(clampedVal);
                        console.log(`Seconds input blurred: "${inputVal}" -> ${clampedVal}`);
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
                onClick={(e) => {
                  // Blur any focused input to ensure values are saved
                  if (focusedInput) {
                    // Trigger blur on the focused input
                    if (focusedInput === 'hours' && hoursInputRef.current) {
                      hoursInputRef.current.blur();
                    } else if (focusedInput === 'minutes' && minutesInputRef.current) {
                      minutesInputRef.current.blur();
                    } else if (focusedInput === 'seconds' && secondsInputRef.current) {
                      secondsInputRef.current.blur();
                    }
                    setFocusedInput(null);
                    // Small delay to ensure state updates from blur handler
                    setTimeout(() => {
                      handleStart(null);
                    }, 100);
                  } else {
                    handleStart(null);
                  }
                }}
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
                  setTimerName('');
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
                    {editingTimerName === timer.id ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          defaultValue={timer.name || ''}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleUpdateTimerName(timer.id, e.target.value);
                            } else if (e.key === 'Escape') {
                              setEditingTimerName(null);
                            }
                          }}
                          autoFocus
                          className={`flex-1 px-2 py-1 rounded border text-sm ${
                            isDark
                              ? 'bg-neutral-900 border-neutral-700 text-white'
                              : 'bg-slate-50 border-slate-300 text-slate-900'
                          } focus:outline-none focus:ring-2 ${
                            isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                          }`}
                        />
                        <button
                          onClick={(e) => {
                            const input = e.target.parentElement.querySelector('input');
                            handleUpdateTimerName(timer.id, input.value);
                          }}
                          className={`p-1 rounded ${
                            isDark
                              ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                              : 'bg-emerald-500 hover:bg-emerald-600 text-white'
                          }`}
                        >
                          <Check size={16} />
                        </button>
                        <button
                          onClick={() => setEditingTimerName(null)}
                          className={`p-1 rounded ${
                            isDark
                              ? 'bg-neutral-700 hover:bg-neutral-600 text-white'
                              : 'bg-slate-300 hover:bg-slate-400 text-slate-700'
                          }`}
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ) : (
                      <>
                        {timer.name ? (
                          <h3 className={`font-semibold mb-1 ${
                            isDark ? 'text-white' : 'text-slate-900'
                          }`}>
                            {timer.name}
                          </h3>
                        ) : task ? (
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
                        <button
                          onClick={() => setEditingTimerName(timer.id)}
                          className={`mt-1 text-xs flex items-center gap-1 ${
                            isDark ? 'text-neutral-500 hover:text-neutral-300' : 'text-slate-500 hover:text-slate-700'
                          }`}
                        >
                          <Edit2 size={12} />
                          {timer.name ? 'Edit name' : 'Add name'}
                        </button>
                      </>
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
