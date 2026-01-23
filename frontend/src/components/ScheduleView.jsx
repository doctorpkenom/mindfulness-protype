import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Zap, Sparkles } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import axios from 'axios';
import LoadingSpinner from './LoadingSpinner';
import DatePicker from './DatePicker';

const API_BASE_URL = 'http://localhost:8000';

export default function ScheduleView() {
  const { isDark } = useTheme();
  const [tasks, setTasks] = useState([]);
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [workHours, setWorkHours] = useState({ start: '06:00', end: '22:00' });

  useEffect(() => {
    loadTasks();
    loadSchedule();
  }, [selectedDate]);

  const loadTasks = async () => {
    try {
      const token = localStorage.getItem('token');
      // Load all tasks (no filter) so we can optimize both pending and scheduled tasks
      // The backend will filter to only use pending/scheduled tasks when optimizing
      const response = await axios.get(
        `${API_BASE_URL}/api/tasks/`,
        {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        }
      );
      // Filter to only show tasks that can be scheduled (pending or scheduled)
      const schedulableTasks = response.data.filter(
        task => task.status === 'pending' || task.status === 'scheduled'
      );
      setTasks(schedulableTasks);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const loadSchedule = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/schedule/${selectedDate}`,
        {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        }
      );
      setSchedule(response.data);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Failed to load schedule:', error);
      }
    }
  };

  const handleOptimize = async () => {
    // Get all tasks that can be scheduled (pending or scheduled)
    const schedulableTasks = tasks.filter(
      task => task.status === 'pending' || task.status === 'scheduled'
    );

    if (schedulableTasks.length === 0) {
      alert('No tasks available to schedule. Please create some tasks first, or check that you have pending or scheduled tasks.');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Not authenticated. Please log in again.');
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/schedule/optimize`,
        {
          date: selectedDate,
          task_ids: schedulableTasks.map(t => t.id),
          work_hours_start: workHours.start,
          work_hours_end: workHours.end
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      setSchedule(response.data);
      await loadTasks();
      await loadSchedule();
    } catch (error) {
      console.error('Failed to optimize schedule:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        code: error.code,
        stack: error.stack
      });
      
      let errorMsg = 'Failed to optimize schedule. Please try again.';
      
      // Check for network errors first
      if (!error.response) {
        if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
          errorMsg = 'Cannot connect to server. Please make sure the backend is running on port 8000.';
        } else if (error.message) {
          errorMsg = `Network error: ${error.message}`;
        } else {
          errorMsg = 'Network error: Could not reach the server. Please check if the backend is running.';
        }
      } else if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (error.response?.status === 500) {
        errorMsg = 'Server error occurred. Please check the backend logs for details.';
      } else if (error.response?.status === 401) {
        errorMsg = 'Authentication failed. Please log in again.';
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-3xl font-bold mb-2 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Schedule Optimizer
          </h1>
          <p className={`text-sm ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            ML-powered task scheduling for optimal productivity
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className={`rounded-xl p-6 border ${
        isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
      }`}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-neutral-300' : 'text-slate-700'
            }`}>
              Date
            </label>
            <DatePicker
              value={selectedDate}
              onChange={(value) => setSelectedDate(value.split('T')[0])}
              placeholder="Select schedule date"
              showTime={false}
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-neutral-300' : 'text-slate-700'
            }`}>
              Work Start
            </label>
            <input
              type="time"
              value={workHours.start}
              onChange={(e) => setWorkHours({...workHours, start: e.target.value})}
              className={`w-full px-4 py-2 rounded-lg border ${
                isDark
                  ? 'bg-neutral-900 border-neutral-700 text-white'
                  : 'bg-slate-50 border-slate-300 text-slate-900'
              }`}
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-neutral-300' : 'text-slate-700'
            }`}>
              Work End
            </label>
            <input
              type="time"
              value={workHours.end}
              onChange={(e) => setWorkHours({...workHours, end: e.target.value})}
              className={`w-full px-4 py-2 rounded-lg border ${
                isDark
                  ? 'bg-neutral-900 border-neutral-700 text-white'
                  : 'bg-slate-50 border-slate-300 text-slate-900'
              }`}
            />
          </div>
        </div>
        <button
          onClick={handleOptimize}
          disabled={loading || tasks.filter(t => t.status === 'pending' || t.status === 'scheduled').length === 0}
          className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
            isDark
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/30'
              : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg shadow-emerald-500/20'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {loading ? (
            <>
              <LoadingSpinner message="" />
              Optimizing...
            </>
          ) : (
            <>
              <Sparkles size={20} />
              Optimize Schedule with ML
            </>
          )}
        </button>
      </div>

      {/* Schedule Display */}
      {schedule && schedule.items && schedule.items.length > 0 ? (
        <div className={`rounded-xl p-6 border ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <h2 className={`text-xl font-semibold ${
              isDark ? 'text-white' : 'text-slate-900'
            }`}>
              Optimized Schedule
            </h2>
            {schedule.optimization_score && (
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                isDark ? 'bg-purple-500/20 text-purple-400' : 'bg-emerald-100 text-emerald-700'
              }`}>
                Score: {(schedule.optimization_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
          <div className="space-y-3">
            {schedule.items.map((item, index) => (
              <div
                key={item.id}
                className={`p-4 rounded-lg border ${
                  isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-slate-50 border-slate-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`text-sm font-medium ${
                        isDark ? 'text-purple-400' : 'text-emerald-600'
                      }`}>
                        {formatTime(item.start_time)} - {formatTime(item.end_time)}
                      </span>
                    </div>
                    <h3 className={`font-semibold mb-1 ${
                      isDark ? 'text-white' : 'text-slate-900'
                    }`}>
                      {item.task_title}
                    </h3>
                    {item.placement_reason && (
                      <p className={`text-xs ${
                        isDark ? 'text-neutral-400' : 'text-slate-600'
                      }`}>
                        {item.placement_reason}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className={`rounded-xl p-12 border text-center ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <Calendar className={`mx-auto mb-4 ${
            isDark ? 'text-neutral-600' : 'text-slate-400'
          }`} size={48} />
          <p className={`${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            No schedule yet. Click "Optimize Schedule" to create one!
          </p>
        </div>
      )}
    </div>
  );
}
