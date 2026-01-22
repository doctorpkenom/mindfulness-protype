import React, { useState, useEffect } from 'react';
import { Plus, Clock, CheckCircle2, Circle, Trash2, Edit2, Save, X } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import axios from 'axios';
import LoadingSpinner from './LoadingSpinner';

const API_BASE_URL = 'http://localhost:8000';

export default function TaskDashboard() {
  const { isDark, colors } = useTheme();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    estimated_minutes: 30,
    priority: 3,
    difficulty: 3,
    energy_required: 0.5,
    focus_required: 0.5,
    category: '',
    tags: []
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/tasks/`);
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTask) {
        await axios.put(`${API_BASE_URL}/api/tasks/${editingTask.id}`, formData);
      } else {
        await axios.post(`${API_BASE_URL}/api/tasks/`, formData);
      }
      await loadTasks();
      resetForm();
    } catch (error) {
      console.error('Failed to save task:', error);
      alert('Failed to save task. Please try again.');
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

  const handleEdit = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      estimated_minutes: task.estimated_minutes,
      priority: task.priority,
      difficulty: task.difficulty,
      energy_required: task.energy_required,
      focus_required: task.focus_required,
      category: task.category || '',
      tags: task.tags || []
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      estimated_minutes: 30,
      priority: 3,
      difficulty: 3,
      energy_required: 0.5,
      focus_required: 0.5,
      category: '',
      tags: []
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

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Priority (1-5)
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={formData.priority}
                  onChange={(e) => setFormData({...formData, priority: parseInt(e.target.value)})}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 ${
                    isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                  }`}
                />
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Difficulty (1-5)
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({...formData, difficulty: parseInt(e.target.value)})}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 ${
                    isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                  }`}
                />
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Energy Required (0-1)
                </label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.energy_required}
                  onChange={(e) => setFormData({...formData, energy_required: parseFloat(e.target.value)})}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 ${
                    isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                  }`}
                />
              </div>

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
          <h2 className={`text-xl font-semibold mb-4 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Pending ({pendingTasks.length})
          </h2>
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
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  formatTime={formatTime}
                  isDark={isDark}
                />
              ))
            )}
          </div>
        </div>

        {/* Completed Tasks */}
        <div>
          <h2 className={`text-xl font-semibold mb-4 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Completed ({completedTasks.length})
          </h2>
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
                  onEdit={handleEdit}
                  onDelete={handleDelete}
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

function TaskCard({ task, onEdit, onDelete, formatTime, isDark }) {
  return (
    <div className={`rounded-lg p-4 border ${
      isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
    }`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3 className={`font-semibold mb-1 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
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
            {task.category && (
              <span className={`px-2 py-1 rounded ${
                isDark ? 'bg-neutral-900 text-neutral-400' : 'bg-slate-100 text-slate-600'
              }`}>
                {task.category}
              </span>
            )}
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
