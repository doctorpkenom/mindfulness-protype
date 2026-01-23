import axios from 'axios';
import { Check, Clock, Edit2, Plus, Trash2, CheckSquare, Square } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import DatePicker from './DatePicker';
import LoadingSpinner from './LoadingSpinner';

const API_BASE_URL = 'http://localhost:8000';

export default function TaskDashboard() {
  const { isDark, colors } = useTheme();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [selectedTasks, setSelectedTasks] = useState(new Set());
  
  // Form state (using percentages for sliders)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    estimated_minutes: 30,
    priority: 50, // 0-100% (0% = Not Urgent, 100% = Urgent)
    difficulty: 50, // 0-100%
    energy_required: 50, // 0-100%
    focus_required: 0.5,
    category: '',
    tags: [],
    deadline: '',
    deadline_time: '',
    has_deadline: false,
    recurrence_pattern: 'none',
    recurrence_end_date: '',
    custom_recurrence_days: '',
    recurrence_never_ends: false
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/tasks/`,
        {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        }
      );
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  // Convert percentage values to backend format
  const convertToBackendFormat = (data) => {
    const result = {
      ...data,
      // Convert priority: 0-100% → 1-5 (0% = 1, 100% = 5)
      priority: Math.round(1 + (data.priority / 100) * 4),
      // Convert difficulty: 0-100% → 1-5 (0% = 1, 100% = 5)
      difficulty: Math.round(1 + (data.difficulty / 100) * 4),
      // Convert energy_required: 0-100% → 0.0-1.0
      energy_required: data.energy_required / 100
    };
    
    // Handle deadline - only include if has_deadline is true
    if (data.has_deadline) {
      if (data.deadline && data.deadline_time) {
        result.deadline = `${data.deadline}T${data.deadline_time}:00`;
      } else if (data.deadline) {
        // If only date is provided, use midnight
        result.deadline = `${data.deadline}T00:00:00`;
      } else {
        delete result.deadline;
      }
    } else {
      delete result.deadline;
    }
    
    // Handle recurrence_end_date - only set if recurrence_never_ends is false
    if (data.recurrence_never_ends) {
      // If never ends, don't set recurrence_end_date
      delete result.recurrence_end_date;
    } else if (data.recurrence_end_date) {
      // Ensure it's a date string, add time if needed
      if (data.recurrence_end_date.includes('T')) {
        result.recurrence_end_date = data.recurrence_end_date;
      } else {
        result.recurrence_end_date = `${data.recurrence_end_date}T00:00:00`;
      }
    } else {
      delete result.recurrence_end_date;
    }
    
    // Remove form-only field
    delete result.recurrence_never_ends;
    
    // Handle custom_recurrence_days - only include if recurrence_pattern is 'custom'
    if (data.recurrence_pattern === 'custom' && data.custom_recurrence_days) {
      result.custom_recurrence_days = data.custom_recurrence_days;
    } else if (data.recurrence_pattern !== 'custom') {
      // Don't send custom_recurrence_days if pattern is not custom
      delete result.custom_recurrence_days;
    }
    
    // Clean up form-only fields
    delete result.deadline_time;
    delete result.has_deadline;
    
    return result;
  };

  // Convert backend format to percentage values
  const convertFromBackendFormat = (task) => {
    return {
      ...task,
      // Convert priority: 1-5 → 0-100% (1 = 0%, 5 = 100%)
      priority: ((task.priority - 1) / 4) * 100,
      // Convert difficulty: 1-5 → 0-100% (1 = 0%, 5 = 100%)
      difficulty: ((task.difficulty - 1) / 4) * 100,
      // Convert energy_required: 0.0-1.0 → 0-100%
      energy_required: task.energy_required * 100
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const backendData = convertToBackendFormat(formData);
      console.log('Sending task data:', backendData); // Debug
      
      if (editingTask) {
        await axios.put(
          `${API_BASE_URL}/api/tasks/${editingTask.id}`,
          backendData,
          {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
          }
        );
      } else {
        await axios.post(
          `${API_BASE_URL}/api/tasks/`,
          backendData,
          {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
          }
        );
      }
      await loadTasks();
      resetForm();
    } catch (error) {
      console.error('Failed to save task:', error);
      console.error('Error response:', error.response?.data); // Debug
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to save task. Please try again.';
      alert(`Failed to save task: ${errorMessage}`);
    }
  };

  const handleDelete = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await axios.delete(`${API_BASE_URL}/api/tasks/${taskId}`);
      await loadTasks();
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const handleToggleComplete = async (task) => {
    try {
      const token = localStorage.getItem('token');
      const newStatus = task.status === 'completed' ? 'pending' : 'completed';
      await axios.put(
        `${API_BASE_URL}/api/tasks/${task.id}`,
        { status: newStatus },
        {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        }
      );
      await loadTasks();
      // Remove from selection if it was selected
      setSelectedTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(task.id);
        return newSet;
      });
    } catch (error) {
      console.error('Failed to toggle task completion:', error);
      alert('Failed to update task status. Please try again.');
    }
  };

  // Bulk operations
  const handleSelectAll = (taskList) => {
    if (selectedTasks.size === taskList.length && taskList.every(t => selectedTasks.has(t.id))) {
      // Deselect all
      setSelectedTasks(new Set());
    } else {
      // Select all
      setSelectedTasks(new Set(taskList.map(t => t.id)));
    }
  };

  const handleToggleSelect = (taskId) => {
    setSelectedTasks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  const handleBulkComplete = async () => {
    if (selectedTasks.size === 0) return;
    
    if (!confirm(`Mark ${selectedTasks.size} task(s) as completed?`)) return;
    
    try {
      const token = localStorage.getItem('token');
      const promises = Array.from(selectedTasks).map(taskId =>
        axios.put(
          `${API_BASE_URL}/api/tasks/${taskId}`,
          { status: 'completed' },
          {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
          }
        )
      );
      await Promise.all(promises);
      await loadTasks();
      setSelectedTasks(new Set());
    } catch (error) {
      console.error('Failed to complete tasks:', error);
      alert('Failed to complete some tasks. Please try again.');
    }
  };

  const handleBulkUncomplete = async () => {
    if (selectedTasks.size === 0) return;
    
    if (!confirm(`Mark ${selectedTasks.size} task(s) as pending?`)) return;
    
    try {
      const token = localStorage.getItem('token');
      const promises = Array.from(selectedTasks).map(taskId =>
        axios.put(
          `${API_BASE_URL}/api/tasks/${taskId}`,
          { status: 'pending' },
          {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
          }
        )
      );
      await Promise.all(promises);
      await loadTasks();
      setSelectedTasks(new Set());
    } catch (error) {
      console.error('Failed to uncomplete tasks:', error);
      alert('Failed to update some tasks. Please try again.');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedTasks.size === 0) return;
    
    if (!confirm(`Delete ${selectedTasks.size} task(s)? This cannot be undone.`)) return;
    
    try {
      const token = localStorage.getItem('token');
      const promises = Array.from(selectedTasks).map(taskId =>
        axios.delete(
          `${API_BASE_URL}/api/tasks/${taskId}`,
          {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
          }
        )
      );
      await Promise.all(promises);
      await loadTasks();
      setSelectedTasks(new Set());
    } catch (error) {
      console.error('Failed to delete tasks:', error);
      alert('Failed to delete some tasks. Please try again.');
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    const convertedTask = convertFromBackendFormat(task);
    
    // Parse deadline if it exists
    let deadline = '';
    let deadline_time = '';
    if (task.deadline) {
      try {
        const deadlineDate = new Date(task.deadline);
        deadline = deadlineDate.toISOString().split('T')[0];
        if (task.deadline.includes('T') && task.deadline.includes(':')) {
          deadline_time = deadlineDate.toTimeString().slice(0, 5); // HH:MM
        }
      } catch (e) {
        console.error('Error parsing deadline:', e);
      }
    }
    
    setFormData({
      title: convertedTask.title,
      description: convertedTask.description || '',
      estimated_minutes: convertedTask.estimated_minutes,
      priority: convertedTask.priority,
      difficulty: convertedTask.difficulty,
      energy_required: convertedTask.energy_required,
      focus_required: convertedTask.focus_required,
      category: convertedTask.category || '',
      tags: convertedTask.tags || [],
      deadline: deadline,
      deadline_time: deadline_time,
      has_deadline: !!task.deadline,
      recurrence_pattern: task.recurrence_pattern || 'none',
      recurrence_end_date: task.recurrence_end_date ? new Date(task.recurrence_end_date).toISOString().split('T')[0] : '',
      custom_recurrence_days: task.custom_recurrence_days || '',
      recurrence_never_ends: !task.recurrence_end_date
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      estimated_minutes: 30,
      priority: 50, // Default to 50% (middle)
      difficulty: 50, // Default to 50% (middle)
      energy_required: 50, // Default to 50% (middle)
      focus_required: 0.5,
      category: '',
      tags: [],
      deadline: '',
      deadline_time: '',
      has_deadline: false,
      recurrence_pattern: 'none',
      recurrence_end_date: '',
      custom_recurrence_days: '',
      recurrence_never_ends: false
    });
    setEditingTask(null);
    setShowForm(false);
  };

  const formatTime = (minutes) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  if (loading) {
    return <LoadingSpinner message="Loading tasks..." />;
  }

  const pendingTasks = tasks.filter(t => t.status === 'pending' || t.status === 'scheduled');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-3xl font-bold mb-2 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            My Tasks
          </h1>
          <p className={`text-sm ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            Add tasks with time estimates for ML-optimized scheduling
          </p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowForm(!showForm);
          }}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
            isDark
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/30'
              : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg shadow-emerald-500/20'
          }`}
        >
          <Plus size={20} />
          {showForm ? 'Cancel' : 'New Task'}
        </button>
      </div>

      {/* Task Form */}
      {showForm && (
        <div className={`rounded-xl p-6 border ${
          isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
        }`}>
          <h2 className={`text-xl font-semibold mb-4 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            {editingTask ? 'Edit Task' : 'Create New Task'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Task Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 ${
                    isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                  }`}
                  required
                />
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Estimated Time (minutes) *
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.estimated_minutes}
                  onChange={(e) => setFormData({...formData, estimated_minutes: parseInt(e.target.value)})}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 ${
                    isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                  }`}
                  required
                />
              </div>
            </div>

            <div>
              <label className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-neutral-300' : 'text-slate-700'
              }`}>
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows={3}
                className={`w-full px-4 py-2 rounded-lg border ${
                  isDark
                    ? 'bg-neutral-900 border-neutral-700 text-white'
                    : 'bg-slate-50 border-slate-300 text-slate-900'
                } focus:outline-none focus:ring-2 ${
                  isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                }`}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Priority Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className={`text-sm font-medium ${
                    isDark ? 'text-neutral-300' : 'text-slate-700'
                  }`}>
                    Priority
                  </label>
                  <span className={`text-sm font-semibold ${
                    isDark ? 'text-purple-400' : 'text-emerald-600'
                  }`}>
                    {Math.round(formData.priority)}%
                  </span>
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                    Not Urgent
                  </span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: parseInt(e.target.value)})}
                    className={`flex-1 h-2 rounded-lg appearance-none cursor-pointer ${
                      isDark
                        ? 'bg-neutral-800 accent-purple-500'
                        : 'bg-slate-200 accent-emerald-500'
                    }`}
                    style={{
                      background: isDark
                        ? `linear-gradient(to right, rgb(168, 85, 247) 0%, rgb(168, 85, 247) ${formData.priority}%, rgb(38, 38, 38) ${formData.priority}%, rgb(38, 38, 38) 100%)`
                        : `linear-gradient(to right, rgb(16, 185, 129) 0%, rgb(16, 185, 129) ${formData.priority}%, rgb(226, 232, 240) ${formData.priority}%, rgb(226, 232, 240) 100%)`
                    }}
                  />
                  <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                    Urgent
                  </span>
                </div>
              </div>

              {/* Difficulty Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className={`text-sm font-medium ${
                    isDark ? 'text-neutral-300' : 'text-slate-700'
                  }`}>
                    Difficulty
                  </label>
                  <span className={`text-sm font-semibold ${
                    isDark ? 'text-purple-400' : 'text-emerald-600'
                  }`}>
                    {Math.round(formData.difficulty)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({...formData, difficulty: parseInt(e.target.value)})}
                  className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${
                    isDark
                      ? 'bg-neutral-800 accent-purple-500'
                      : 'bg-slate-200 accent-emerald-500'
                  }`}
                  style={{
                    background: isDark
                      ? `linear-gradient(to right, rgb(168, 85, 247) 0%, rgb(168, 85, 247) ${formData.difficulty}%, rgb(38, 38, 38) ${formData.difficulty}%, rgb(38, 38, 38) 100%)`
                      : `linear-gradient(to right, rgb(16, 185, 129) 0%, rgb(16, 185, 129) ${formData.difficulty}%, rgb(226, 232, 240) ${formData.difficulty}%, rgb(226, 232, 240) 100%)`
                  }}
                />
                <div className="flex justify-between mt-1">
                  <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                    Easy
                  </span>
                  <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                    Hard
                  </span>
                </div>
              </div>

              {/* Energy Required Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className={`text-sm font-medium ${
                    isDark ? 'text-neutral-300' : 'text-slate-700'
                  }`}>
                    Energy Required
                  </label>
                  <span className={`text-sm font-semibold ${
                    isDark ? 'text-purple-400' : 'text-emerald-600'
                  }`}>
                    {Math.round(formData.energy_required)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={formData.energy_required}
                  onChange={(e) => setFormData({...formData, energy_required: parseInt(e.target.value)})}
                  className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${
                    isDark
                      ? 'bg-neutral-800 accent-purple-500'
                      : 'bg-slate-200 accent-emerald-500'
                  }`}
                  style={{
                    background: isDark
                      ? `linear-gradient(to right, rgb(168, 85, 247) 0%, rgb(168, 85, 247) ${formData.energy_required}%, rgb(38, 38, 38) ${formData.energy_required}%, rgb(38, 38, 38) 100%)`
                      : `linear-gradient(to right, rgb(16, 185, 129) 0%, rgb(16, 185, 129) ${formData.energy_required}%, rgb(226, 232, 240) ${formData.energy_required}%, rgb(226, 232, 240) 100%)`
                  }}
                />
                <div className="flex justify-between mt-1">
                  <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                    0%
                  </span>
                  <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                    100%
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Category
                </label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  placeholder="work, personal, etc."
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 ${
                    isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                  }`}
                />
              </div>
            </div>

            {/* Deadline Toggle and Fields */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className={`text-sm font-medium ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Has Deadline
                </label>
                <button
                  type="button"
                  onClick={() => setFormData({...formData, has_deadline: !formData.has_deadline})}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                    formData.has_deadline
                      ? isDark ? 'bg-purple-600 focus:ring-purple-500' : 'bg-emerald-600 focus:ring-emerald-500'
                      : isDark ? 'bg-neutral-700 focus:ring-neutral-500' : 'bg-slate-300 focus:ring-slate-400'
                  }`}
                  role="switch"
                  aria-checked={formData.has_deadline}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      formData.has_deadline ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {formData.has_deadline && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${
                      isDark ? 'text-neutral-300' : 'text-slate-700'
                    }`}>
                      Deadline Date
                    </label>
                    <DatePicker
                      value={formData.deadline}
                      onChange={(value) => setFormData({...formData, deadline: value})}
                      placeholder="Select deadline date"
                      showTime={false}
                    />
                  </div>
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${
                      isDark ? 'text-neutral-300' : 'text-slate-700'
                    }`}>
                      Deadline Time
                    </label>
                    <input
                      type="time"
                      value={formData.deadline_time}
                      onChange={(e) => setFormData({...formData, deadline_time: e.target.value})}
                      className={`w-full px-4 py-2 rounded-lg border ${
                        isDark
                          ? 'bg-neutral-900 border-neutral-700 text-white'
                          : 'bg-slate-50 border-slate-300 text-slate-900'
                      } focus:outline-none focus:ring-2 ${
                        isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                      }`}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Recurrence */}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Recurrence Pattern
                </label>
                <select
                  value={formData.recurrence_pattern}
                  onChange={(e) => setFormData({...formData, recurrence_pattern: e.target.value})}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 ${
                    isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                  }`}
                >
                  <option value="none">None</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              {formData.recurrence_pattern === 'custom' && (
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDark ? 'text-neutral-300' : 'text-slate-700'
                  }`}>
                    Custom Interval (days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.custom_recurrence_days || ''}
                    onChange={(e) => setFormData({...formData, custom_recurrence_days: parseInt(e.target.value) || ''})}
                    placeholder="e.g., 3 for every 3 days"
                    className={`w-full px-4 py-2 rounded-lg border ${
                      isDark
                        ? 'bg-neutral-900 border-neutral-700 text-white'
                        : 'bg-slate-50 border-slate-300 text-slate-900'
                    } focus:outline-none focus:ring-2 ${
                      isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                    }`}
                  />
                </div>
              )}
            </div>

            {/* Recurrence End Date (shown when recurrence is not 'none') */}
            {formData.recurrence_pattern !== 'none' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDark ? 'text-neutral-300' : 'text-slate-700'
                  }`}>
                    Recurrence End Date
                  </label>
                  {!formData.recurrence_never_ends ? (
                    <DatePicker
                      value={formData.recurrence_end_date}
                      onChange={(value) => setFormData({...formData, recurrence_end_date: value})}
                      placeholder="Select end date"
                      showTime={false}
                    />
                  ) : (
                    <div className={`px-4 py-2 rounded-lg border ${
                      isDark
                        ? 'bg-neutral-800 border-neutral-700 text-neutral-400'
                        : 'bg-slate-100 border-slate-300 text-slate-500'
                    }`}>
                      Never ends
                    </div>
                  )}
                </div>
                <div className="flex items-end">
                  <label className={`flex items-center gap-2 cursor-pointer ${
                    isDark ? 'text-neutral-300' : 'text-slate-700'
                  }`}>
                    <input
                      type="checkbox"
                      checked={formData.recurrence_never_ends}
                      onChange={(e) => {
                        setFormData({
                          ...formData,
                          recurrence_never_ends: e.target.checked,
                          recurrence_end_date: e.target.checked ? '' : formData.recurrence_end_date
                        });
                      }}
                      className={`w-4 h-4 rounded ${
                        isDark
                          ? 'accent-purple-500'
                          : 'accent-emerald-500'
                      }`}
                    />
                    <span className="text-sm">Never ends</span>
                  </label>
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                type="submit"
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  isDark
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                    : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white'
                }`}
              >
                {editingTask ? 'Update Task' : 'Create Task'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className={`px-6 py-2 rounded-lg font-medium border ${
                  isDark
                    ? 'border-neutral-700 text-neutral-300 hover:bg-neutral-900'
                    : 'border-slate-300 text-slate-700 hover:bg-slate-100'
                }`}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Task Lists */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Tasks */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className={`text-xl font-semibold ${
              isDark ? 'text-white' : 'text-slate-900'
            }`}>
              Pending ({pendingTasks.length})
            </h2>
            {pendingTasks.length > 0 && (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleSelectAll(pendingTasks)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
                    isDark
                      ? 'hover:bg-neutral-800 text-neutral-400 hover:text-white'
                      : 'hover:bg-slate-100 text-slate-500 hover:text-slate-900'
                  }`}
                  title="Select All"
                >
                  {selectedTasks.size === pendingTasks.length && pendingTasks.every(t => selectedTasks.has(t.id)) ? (
                    <CheckSquare size={18} />
                  ) : (
                    <Square size={18} />
                  )}
                  <span className="text-sm font-medium">Select All</span>
                </button>
                {selectedTasks.size > 0 && pendingTasks.some(t => selectedTasks.has(t.id)) && (
                  <div className="flex gap-2">
                    <button
                      onClick={handleBulkComplete}
                      className={`px-3 py-1.5 text-sm rounded font-medium transition-colors ${
                        isDark
                          ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                          : 'bg-emerald-500 hover:bg-emerald-600 text-white'
                      }`}
                    >
                      Complete ({Array.from(selectedTasks).filter(id => pendingTasks.some(t => t.id === id)).length})
                    </button>
                    <button
                      onClick={handleBulkDelete}
                      className={`px-3 py-1.5 text-sm rounded font-medium transition-colors ${
                        isDark
                          ? 'bg-rose-600 hover:bg-rose-700 text-white'
                          : 'bg-rose-500 hover:bg-rose-600 text-white'
                      }`}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="space-y-3">
            {pendingTasks.length === 0 ? (
              <p className={`text-sm ${
                isDark ? 'text-neutral-500' : 'text-slate-400'
              }`}>
                No pending tasks. Create one to get started!
              </p>
            ) : (
              pendingTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isSelected={selectedTasks.has(task.id)}
                  onSelect={() => handleToggleSelect(task.id)}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  onToggleComplete={handleToggleComplete}
                  formatTime={formatTime}
                  isDark={isDark}
                />
              ))
            )}
          </div>
        </div>

        {/* Completed Tasks */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className={`text-xl font-semibold ${
              isDark ? 'text-white' : 'text-slate-900'
            }`}>
              Completed ({completedTasks.length})
            </h2>
            {completedTasks.length > 0 && (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleSelectAll(completedTasks)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
                    isDark
                      ? 'hover:bg-neutral-800 text-neutral-400 hover:text-white'
                      : 'hover:bg-slate-100 text-slate-500 hover:text-slate-900'
                  }`}
                  title="Select All"
                >
                  {selectedTasks.size === completedTasks.length && completedTasks.every(t => selectedTasks.has(t.id)) ? (
                    <CheckSquare size={18} />
                  ) : (
                    <Square size={18} />
                  )}
                  <span className="text-sm font-medium">Select All</span>
                </button>
                {selectedTasks.size > 0 && completedTasks.some(t => selectedTasks.has(t.id)) && (
                  <div className="flex gap-2">
                    <button
                      onClick={handleBulkUncomplete}
                      className={`px-3 py-1.5 text-sm rounded font-medium transition-colors ${
                        isDark
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'bg-blue-500 hover:bg-blue-600 text-white'
                      }`}
                    >
                      Uncomplete ({Array.from(selectedTasks).filter(id => completedTasks.some(t => t.id === id)).length})
                    </button>
                    <button
                      onClick={handleBulkDelete}
                      className={`px-3 py-1.5 text-sm rounded font-medium transition-colors ${
                        isDark
                          ? 'bg-rose-600 hover:bg-rose-700 text-white'
                          : 'bg-rose-500 hover:bg-rose-600 text-white'
                      }`}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="space-y-3">
            {completedTasks.length === 0 ? (
              <p className={`text-sm ${
                isDark ? 'text-neutral-500' : 'text-slate-400'
              }`}>
                No completed tasks yet.
              </p>
            ) : (
              completedTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isSelected={selectedTasks.has(task.id)}
                  onSelect={() => handleToggleSelect(task.id)}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  onToggleComplete={handleToggleComplete}
                  formatTime={formatTime}
                  isDark={isDark}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function TaskCard({ task, isSelected, onSelect, onEdit, onDelete, onToggleComplete, formatTime, isDark }) {
  const isCompleted = task.status === 'completed';
  
  return (
    <div className={`rounded-lg p-4 border ${
      isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
    } ${isCompleted ? 'opacity-75' : ''} ${isSelected ? (isDark ? 'ring-2 ring-purple-500 border-purple-500' : 'ring-2 ring-emerald-500 border-emerald-500') : ''}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-start gap-3 flex-1">
          {/* Selection Checkbox */}
          <button
            onClick={onSelect}
            className={`mt-1 flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
              isSelected
                ? isDark
                  ? 'bg-purple-600 border-purple-600'
                  : 'bg-emerald-600 border-emerald-600'
                : isDark
                  ? 'border-neutral-600 hover:border-purple-500'
                  : 'border-slate-300 hover:border-emerald-500'
            }`}
            aria-label={isSelected ? 'Deselect task' : 'Select task'}
          >
            {isSelected && (
              <Check size={14} className="text-white" />
            )}
          </button>
          <div className="flex-1">
            <h3 className={`font-semibold mb-1 ${
              isDark ? 'text-white' : 'text-slate-900'
            } ${isCompleted ? 'line-through' : ''}`}>
              {task.title}
            </h3>
          {task.description && (
            <p className={`text-sm mb-2 ${
              isDark ? 'text-neutral-400' : 'text-slate-600'
            }`}>
              {task.description}
            </p>
          )}
          <div className="flex items-center gap-4 text-xs">
            <span className={`flex items-center gap-1 ${
              isDark ? 'text-neutral-500' : 'text-slate-500'
            }`}>
              <Clock size={14} />
              {formatTime(task.estimated_minutes)}
            </span>
            <span className={`${
              isDark ? 'text-neutral-500' : 'text-slate-500'
            }`}>
              Priority: {task.priority}/5
            </span>
            <span className={`${
              isDark ? 'text-neutral-500' : 'text-slate-500'
            }`}>
              Energy: {Math.round((task.energy_required || 0) * 100)}%
            </span>
            {task.category && (
              <span className={`px-2 py-1 rounded ${
                isDark ? 'bg-neutral-900 text-neutral-400' : 'bg-slate-100 text-slate-600'
              }`}>
                {task.category}
              </span>
            )}
          </div>
          </div>
        </div>
        <div className="flex gap-2 ml-2">
          <button
            onClick={() => onEdit(task)}
            className={`p-2 rounded hover:bg-opacity-20 ${
              isDark ? 'hover:bg-purple-500' : 'hover:bg-emerald-500'
            }`}
          >
            <Edit2 size={16} className={isDark ? 'text-purple-400' : 'text-emerald-600'} />
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className={`p-2 rounded hover:bg-opacity-20 hover:bg-rose-500`}
          >
            <Trash2 size={16} className="text-rose-500" />
          </button>
        </div>
      </div>
    </div>
  );
}
