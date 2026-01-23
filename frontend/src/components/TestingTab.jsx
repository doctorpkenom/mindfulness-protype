import React, { useState } from 'react';
import { TestTube, CheckCircle2, AlertCircle, Loader, Home, Briefcase, Heart, Database, RotateCcw } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useNotifications } from '../contexts/NotificationContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function TestingTab() {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [activeTab, setActiveTab] = useState('tasks');
  const [isGenerating, setIsGenerating] = useState({ daily: false, work: false, personal: false });
  const [generatedTasks, setGeneratedTasks] = useState({ daily: [], work: [], personal: [] });
  const [simDataDays, setSimDataDays] = useState(30);
  const [simDataDaysInput, setSimDataDaysInput] = useState('30');
  const [isGeneratingSimData, setIsGeneratingSimData] = useState(false);

  // Daily tasks (chores, cooking) - with daily recurrence and preferred times
  const dailyTasks = [
    {
      title: "Morning coffee and breakfast prep",
      description: "Prepare morning coffee and breakfast",
      estimated_minutes: 15,
      priority: 2,
      difficulty: 1,
      energy_required: 0.2,
      focus_required: 0.1,
      category: "daily",
      tags: ["routine", "cooking", "morning"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "07:00", // Morning routine
      preferred_time_window: "06:00-09:00"
    },
    {
      title: "Dishwashing",
      description: "Wash dishes and clean kitchen",
      estimated_minutes: 20,
      priority: 2,
      difficulty: 1,
      energy_required: 0.3,
      focus_required: 0.2,
      category: "daily",
      tags: ["chores", "cleaning", "evening"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "20:00", // After dinner
      preferred_time_window: "19:00-21:00"
    },
    {
      title: "Laundry - Load washer",
      description: "Sort and load laundry into washing machine",
      estimated_minutes: 10,
      priority: 2,
      difficulty: 1,
      energy_required: 0.2,
      focus_required: 0.1,
      category: "daily",
      tags: ["chores", "laundry", "morning"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "08:00", // Morning chore
      preferred_time_window: "07:00-10:00"
    },
    {
      title: "Take out trash",
      description: "Empty trash bins and take to curb",
      estimated_minutes: 5,
      priority: 2,
      difficulty: 1,
      energy_required: 0.1,
      focus_required: 0.1,
      category: "daily",
      tags: ["chores", "evening"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "21:00", // Evening before bed
      preferred_time_window: "20:00-22:00"
    },
    {
      title: "Dinner preparation",
      description: "Prepare and cook dinner",
      estimated_minutes: 45,
      priority: 3,
      difficulty: 2,
      energy_required: 0.4,
      focus_required: 0.3,
      category: "daily",
      tags: ["cooking", "routine", "evening"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "18:00", // Dinner time
      preferred_time_window: "17:00-19:00"
    },
    {
      title: "Tidy living room",
      description: "Quick cleanup and organization of living space",
      estimated_minutes: 15,
      priority: 2,
      difficulty: 1,
      energy_required: 0.2,
      focus_required: 0.1,
      category: "daily",
      tags: ["cleaning", "chores", "evening"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "19:30", // After dinner
      preferred_time_window: "19:00-21:00"
    }
  ];

  // Work-related tasks - with deadlines and realistic work hours
  const workTasks = [
    {
      title: "Review and respond to emails",
      description: "Go through inbox and respond to urgent emails",
      estimated_minutes: 30,
      priority: 4,
      difficulty: 2,
      energy_required: 0.5,
      focus_required: 0.6,
      category: "work",
      tags: ["communication", "urgent", "morning"],
      has_deadline: true,
      deadline: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      deadline_time: "17:00",
      preferred_time: "09:00", // Start of work day
      preferred_time_window: "08:00-10:00"
    },
    {
      title: "Team standup meeting",
      description: "Daily team sync and progress update",
      estimated_minutes: 30,
      priority: 4,
      difficulty: 1,
      energy_required: 0.4,
      focus_required: 0.7,
      category: "work",
      tags: ["meeting", "communication", "morning"],
      has_deadline: true,
      deadline: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      deadline_time: "10:00",
      preferred_time: "10:00", // Standard standup time
      preferred_time_window: "09:30-10:30"
    },
    {
      title: "Complete project proposal",
      description: "Finalize and submit project proposal document",
      estimated_minutes: 120,
      priority: 5,
      difficulty: 4,
      energy_required: 0.8,
      focus_required: 0.9,
      category: "work",
      tags: ["urgent", "writing", "deadline", "deep-work"],
      has_deadline: true,
      deadline: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      deadline_time: "17:00",
      preferred_time: "14:00", // Afternoon deep work
      preferred_time_window: "13:00-16:00"
    },
    {
      title: "Code review for PR #123",
      description: "Review pull request and provide feedback",
      estimated_minutes: 60,
      priority: 3,
      difficulty: 3,
      energy_required: 0.6,
      focus_required: 0.8,
      category: "work",
      tags: ["technical", "review", "afternoon"],
      has_deadline: true,
      deadline: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      deadline_time: "18:00",
      preferred_time: "15:00", // Mid-afternoon
      preferred_time_window: "14:00-17:00"
    },
    {
      title: "Prepare quarterly report",
      description: "Compile data and create quarterly performance report",
      estimated_minutes: 90,
      priority: 4,
      difficulty: 3,
      energy_required: 0.7,
      focus_required: 0.8,
      category: "work",
      tags: ["analysis", "reporting", "morning"],
      has_deadline: true,
      deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      deadline_time: "17:00",
      preferred_time: "11:00", // Late morning when energy is high
      preferred_time_window: "10:00-13:00"
    },
    {
      title: "Client presentation preparation",
      description: "Create slides and prepare talking points for client meeting",
      estimated_minutes: 120,
      priority: 5,
      difficulty: 4,
      energy_required: 0.8,
      focus_required: 0.9,
      category: "work",
      tags: ["presentation", "urgent", "deep-work"],
      has_deadline: true,
      deadline: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      deadline_time: "14:00",
      preferred_time: "13:00", // Afternoon focus time
      preferred_time_window: "12:00-15:00"
    }
  ];

  // Personal/other tasks - adjustable based on day with preferred times
  const personalTasks = [
    {
      title: "Morning meditation",
      description: "10-minute mindfulness meditation session",
      estimated_minutes: 10,
      priority: 2,
      difficulty: 1,
      energy_required: 0.1,
      focus_required: 0.3,
      category: "health",
      tags: ["wellness", "routine", "morning"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "06:30", // Early morning
      preferred_time_window: "06:00-08:00"
    },
    {
      title: "Evening walk",
      description: "30-minute walk around the neighborhood",
      estimated_minutes: 30,
      priority: 2,
      difficulty: 1,
      energy_required: 0.3,
      focus_required: 0.2,
      category: "health",
      tags: ["exercise", "outdoor", "evening"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "19:00", // Evening
      preferred_time_window: "18:00-20:00"
    },
    {
      title: "Read for 30 minutes",
      description: "Read book or articles for personal development",
      estimated_minutes: 30,
      priority: 2,
      difficulty: 1,
      energy_required: 0.3,
      focus_required: 0.5,
      category: "learning",
      tags: ["reading", "personal", "evening"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "21:00", // Before bed
      preferred_time_window: "20:00-22:00"
    },
    {
      title: "Call family member",
      description: "Check in with family",
      estimated_minutes: 20,
      priority: 3,
      difficulty: 1,
      energy_required: 0.2,
      focus_required: 0.3,
      category: "personal",
      tags: ["social", "family", "evening"],
      recurrence_pattern: "weekly",
      recurrence_never_ends: true,
      preferred_time: "19:30", // Evening
      preferred_time_window: "18:00-21:00"
    },
    {
      title: "Plan weekend activities",
      description: "Research and plan activities for the weekend",
      estimated_minutes: 30,
      priority: 2,
      difficulty: 1,
      energy_required: 0.3,
      focus_required: 0.4,
      category: "personal",
      tags: ["planning", "leisure", "evening"],
      recurrence_pattern: "weekly",
      recurrence_never_ends: true,
      preferred_time: "20:00", // Thursday/Friday evening
      preferred_time_window: "19:00-21:00"
    },
    {
      title: "Journal entry",
      description: "Write daily journal entry",
      estimated_minutes: 15,
      priority: 2,
      difficulty: 1,
      energy_required: 0.2,
      focus_required: 0.4,
      category: "personal",
      tags: ["writing", "reflection", "evening"],
      recurrence_pattern: "daily",
      recurrence_never_ends: true,
      preferred_time: "21:30", // End of day reflection
      preferred_time_window: "21:00-22:00"
    }
  ];

  const generateTasks = async (taskType) => {
    // Prevent multiple simultaneous generations of the same type
    if (isGenerating[taskType]) {
      return;
    }

    setIsGenerating(prev => {
      const newState = { ...prev };
      newState[taskType] = true;
      return newState;
    });
    
    setGeneratedTasks(prev => {
      const newState = { ...prev };
      newState[taskType] = [];
      return newState;
    });
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      const taskList = taskType === 'daily' ? dailyTasks : taskType === 'work' ? workTasks : personalTasks;
      const createdTasks = [];
      const errors = [];

      // Create tasks one by one
      for (const taskData of taskList) {
        try {
          // Convert to backend format
          // Backend expects: priority 1-5, difficulty 1-5, energy_required 0.0-1.0
          const tags = [...(taskData.tags || [])];
          
          // Add preferred time to tags if available (for ML scheduling)
          if (taskData.preferred_time) {
            tags.push(`preferred_time:${taskData.preferred_time}`);
          }
          if (taskData.preferred_time_window) {
            tags.push(`preferred_window:${taskData.preferred_time_window}`);
          }
          
          const backendData = {
            title: taskData.title,
            description: taskData.description,
            estimated_minutes: taskData.estimated_minutes,
            priority: taskData.priority, // Already 1-5 scale
            difficulty: taskData.difficulty, // Already 1-5 scale
            energy_required: taskData.energy_required, // Already 0.0-1.0
            focus_required: taskData.focus_required,
            category: taskData.category,
            tags: tags,
            recurrence_pattern: taskData.recurrence_pattern || null,
            recurrence_end_date: taskData.recurrence_never_ends ? null : (taskData.recurrence_end_date || null),
            deadline: taskData.has_deadline && taskData.deadline && taskData.deadline_time
              ? `${taskData.deadline}T${taskData.deadline_time}:00`
              : null
          };

          // Remove frontend-only fields
          delete backendData.has_deadline;
          delete backendData.deadline_time;
          delete backendData.recurrence_never_ends;

          const response = await axios.post(
            `${API_BASE_URL}/api/tasks/`,
            backendData,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          );
          createdTasks.push(response.data);
          
          // Small delay to avoid overwhelming the server
          await new Promise(resolve => setTimeout(resolve, 100));
        } catch (error) {
          console.error(`Failed to create task "${taskData.title}":`, error);
          errors.push({ task: taskData.title, error: error.response?.data?.detail || error.message });
        }
      }

      setGeneratedTasks(prev => {
        const newState = { ...prev };
        newState[taskType] = createdTasks;
        return newState;
      });

      // Reset generating state immediately so button is clickable again
      setIsGenerating(prev => {
        const newState = { ...prev };
        newState[taskType] = false;
        return newState;
      });

      // Notifications disabled for task generator

    } catch (error) {
      console.error(`Failed to generate ${taskType} tasks:`, error);
      
      // Reset generating state immediately even on error
      setIsGenerating(prev => {
        const newState = { ...prev };
        newState[taskType] = false;
        return newState;
      });

      // Notifications disabled for task generator
    }
  };

  const generateSimulatedData = async () => {
    if (isGeneratingSimData) return;
    
    setIsGeneratingSimData(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/api/admin/generate-simulated-data`,
        { days: simDataDays },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      addNotification({
        type: 'success',
        title: 'Simulated Data Generated',
        message: `Generated ${simDataDays} days of realistic user data for ML training`,
        persistent: false
      });
    } catch (error) {
      console.error('Failed to generate simulated data:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.detail || 'Failed to generate simulated data',
        persistent: true
      });
    } finally {
      setIsGeneratingSimData(false);
    }
  };

  const TaskGeneratorCard = ({ type, title, description, icon: Icon, tasks, color }) => (
    <div className={`p-6 rounded-lg border ${
      isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-slate-200'
    }`}>
      <div className="flex items-start gap-3 mb-4">
        <div className={`p-2 rounded-lg ${
          isDark ? 'bg-neutral-800' : 'bg-slate-100'
        }`}>
          <Icon className={color} size={24} />
        </div>
        <div className="flex-1">
          <h3 className={`font-semibold mb-1 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            {title}
          </h3>
          <p className={`text-sm ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            {description}
          </p>
        </div>
      </div>

      <div className={`mb-4 space-y-2 max-h-48 overflow-y-auto ${
        isDark ? 'bg-neutral-950' : 'bg-slate-50'
      } p-3 rounded-lg`}>
        {tasks.map((task, idx) => (
          <div key={idx} className={`text-sm ${
            isDark ? 'text-neutral-300' : 'text-slate-700'
          }`}>
            <span className="font-medium">{idx + 1}. {task.title}</span>
            <span className={`ml-2 text-xs ${
              isDark ? 'text-neutral-500' : 'text-slate-500'
            }`}>
              ({task.estimated_minutes} min)
            </span>
          </div>
        ))}
      </div>

      <button
        onClick={() => generateTasks(type)}
        disabled={isGenerating[type]}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
          isGenerating[type]
            ? isDark
              ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            : isDark
            ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/30'
            : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/20'
        }`}
      >
        {isGenerating[type] ? (
          <>
            <Loader className="animate-spin" size={18} />
            <span>Generating...</span>
          </>
        ) : (
          <>
            <Icon size={18} />
            <span>Generate {tasks.length} {title} Tasks</span>
          </>
        )}
      </button>

      {generatedTasks[type].length > 0 && (
        <div className={`mt-4 p-3 rounded-lg ${
          isDark ? 'bg-emerald-950/20 border border-emerald-800' : 'bg-emerald-50 border border-emerald-200'
        }`}>
          <div className="flex items-start gap-2">
            <CheckCircle2 className={`flex-shrink-0 mt-0.5 ${
              isDark ? 'text-emerald-400' : 'text-emerald-600'
            }`} size={16} />
            <p className={`text-sm font-medium ${
              isDark ? 'text-emerald-300' : 'text-emerald-900'
            }`}>
              Created {generatedTasks[type].length} tasks
            </p>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className={`text-2xl font-semibold mb-2 flex items-center gap-2 ${
          isDark ? 'text-white' : 'text-slate-900'
        }`}>
          <TestTube className={isDark ? 'text-purple-400' : 'text-emerald-600'} />
          Testing & Data Generation
        </h2>
        <p className={`text-sm ${
          isDark ? 'text-neutral-400' : 'text-slate-600'
        }`}>
          Generate realistic test tasks and simulated user data for ML model training
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => setActiveTab('tasks')}
          className={`px-4 py-2 border-b-2 transition-colors ${
            activeTab === 'tasks'
              ? isDark
                ? 'border-purple-500 text-purple-400'
                : 'border-emerald-500 text-emerald-600'
              : isDark
              ? 'border-transparent text-neutral-400 hover:text-neutral-200'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          Task Generators
        </button>
        <button
          onClick={() => setActiveTab('simdata')}
          className={`px-4 py-2 border-b-2 transition-colors ${
            activeTab === 'simdata'
              ? isDark
                ? 'border-purple-500 text-purple-400'
                : 'border-emerald-500 text-emerald-600'
              : isDark
              ? 'border-transparent text-neutral-400 hover:text-neutral-200'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <Database size={18} className="inline mr-2" />
          Simulated Data
        </button>
      </div>

      {/* Task Generators Tab */}
      {activeTab === 'tasks' && (
        <div className="space-y-6">

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <TaskGeneratorCard
          type="daily"
          title="Daily Tasks"
          description="Chores, cooking, and routine daily tasks with daily recurrence"
          icon={Home}
          tasks={dailyTasks}
          color={isDark ? 'text-blue-400' : 'text-blue-500'}
        />
        <TaskGeneratorCard
          type="work"
          title="Work Tasks"
          description="Work-related tasks with deadlines (you can edit deadlines in Tasks)"
          icon={Briefcase}
          tasks={workTasks}
          color={isDark ? 'text-purple-400' : 'text-purple-500'}
        />
        <TaskGeneratorCard
          type="personal"
          title="Personal Tasks"
          description="Health, learning, and personal tasks adjustable based on day"
          icon={Heart}
          tasks={personalTasks}
          color={isDark ? 'text-pink-400' : 'text-pink-500'}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={`p-4 rounded-lg ${
          isDark ? 'bg-neutral-900 border border-neutral-800' : 'bg-slate-50 border border-slate-200'
        }`}>
          <h4 className={`font-medium mb-2 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            What This Does:
          </h4>
          <ul className={`text-sm space-y-1 ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            <li>• <strong>Daily Tasks:</strong> Creates recurring daily tasks (chores, cooking) that reset every day</li>
            <li>• <strong>Work Tasks:</strong> Creates work-related tasks with deadlines (editable in Tasks tab)</li>
            <li>• <strong>Personal Tasks:</strong> Creates personal/health tasks with flexible scheduling</li>
            <li>• All tasks are automatically scheduled using the ML optimizer</li>
            <li>• Recurring tasks automatically reset from completed to pending based on their pattern</li>
          </ul>
        </div>

        <div className={`p-4 rounded-lg ${
          isDark ? 'bg-neutral-900 border border-neutral-800' : 'bg-slate-50 border border-slate-200'
        }`}>
          <h4 className={`font-medium mb-2 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Recurring Task Reset:
          </h4>
          <p className={`text-sm mb-3 ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            Manually reset recurring tasks from completed to pending. This normally happens automatically at midnight or based on recurrence patterns.
          </p>
          <button
            onClick={async () => {
              try {
                const token = localStorage.getItem('token');
                const response = await axios.post(
                  `${API_BASE_URL}/api/tasks/reset-recurring`,
                  {},
                  {
                    headers: {
                      'Authorization': `Bearer ${token}`,
                      'Content-Type': 'application/json'
                    }
                  }
                );
                addNotification({
                  type: 'success',
                  title: 'Tasks Reset',
                  message: response.data.message || `Reset ${response.data.reset_count} task(s)`,
                  persistent: false
                });
              } catch (error) {
                console.error('Failed to reset recurring tasks:', error);
                addNotification({
                  type: 'error',
                  title: 'Error',
                  message: error.response?.data?.detail || error.message || 'Failed to reset recurring tasks',
                  persistent: false
                });
              }
            }}
            className={`w-full py-2 px-4 rounded-lg font-medium transition-all ${
              isDark
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white'
            }`}
          >
            Reset Recurring Tasks
          </button>
        </div>
      </div>
        </div>
      )}

      {/* Simulated Data Tab */}
      {activeTab === 'simdata' && (
        <div className="space-y-6">
          <div className={`rounded-xl p-6 border ${
            isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
          }`}>
            <h3 className={`text-lg font-semibold mb-4 flex items-center gap-2 ${
              isDark ? 'text-white' : 'text-slate-900'
            }`}>
              <Database className={isDark ? 'text-purple-400' : 'text-emerald-600'} />
              Generate Simulated User Data
            </h3>
            <p className={`text-sm mb-6 ${
              isDark ? 'text-neutral-400' : 'text-slate-600'
            }`}>
              Generate realistic user interaction data over a period of time to train and improve ML models.
              This creates tasks, timer sessions, completions, and schedule data that mimics real user behavior.
            </p>

            <div className="space-y-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>
                  Number of Days
                </label>
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={simDataDaysInput}
                  onChange={(e) => {
                    const value = e.target.value;
                    setSimDataDaysInput(value);
                    // Only update the actual value if it's a valid number
                    const numValue = parseInt(value);
                    if (!isNaN(numValue) && numValue >= 1 && numValue <= 365) {
                      setSimDataDays(numValue);
                    }
                  }}
                  onBlur={(e) => {
                    // On blur, ensure we have a valid value
                    const numValue = parseInt(e.target.value);
                    if (isNaN(numValue) || numValue < 1) {
                      setSimDataDaysInput('30');
                      setSimDataDays(30);
                    } else if (numValue > 365) {
                      setSimDataDaysInput('365');
                      setSimDataDays(365);
                    } else {
                      setSimDataDaysInput(String(numValue));
                      setSimDataDays(numValue);
                    }
                  }}
                  className={`w-full px-4 py-2 rounded-lg border ${
                    isDark
                      ? 'bg-neutral-900 border-neutral-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  }`}
                />
                <p className={`text-xs mt-1 ${
                  isDark ? 'text-neutral-500' : 'text-slate-500'
                }`}>
                  Generate data for the past {simDataDays} days
                </p>
              </div>

              <button
                onClick={generateSimulatedData}
                disabled={isGeneratingSimData}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  isGeneratingSimData
                    ? isDark
                      ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
                      : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    : isDark
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/30'
                    : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/20'
                }`}
              >
                {isGeneratingSimData ? (
                  <>
                    <Loader className="animate-spin" size={18} />
                    <span>Generating Data...</span>
                  </>
                ) : (
                  <>
                    <Database size={18} />
                    <span>Generate {simDataDays} Days of Simulated Data</span>
                  </>
                )}
              </button>
            </div>

            <div className={`mt-6 p-4 rounded-lg ${
              isDark ? 'bg-neutral-900 border border-neutral-800' : 'bg-slate-50 border border-slate-200'
            }`}>
              <h4 className={`font-medium mb-2 ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}>
                What Gets Generated:
              </h4>
              <ul className={`text-sm space-y-1 ${
                isDark ? 'text-neutral-400' : 'text-slate-600'
              }`}>
                <li>• Realistic tasks with varying priorities, difficulties, and categories</li>
                <li>• Timer sessions with actual completion times</li>
                <li>• Task completions with time accuracy data</li>
                <li>• Schedule optimizations and placements</li>
                <li>• Energy and stress patterns over time</li>
                <li>• ML model learning data for improved predictions</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
