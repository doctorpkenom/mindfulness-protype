import React, { useState } from 'react';
import { TestTube, CheckCircle2, AlertCircle, Loader } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useNotifications } from '../contexts/NotificationContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function TesterTab() {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTasks, setGeneratedTasks] = useState([]);

  // Realistic test tasks that a user might create
  const testTasks = [
    {
      title: "Review quarterly financial reports",
      description: "Go through Q4 financial statements and prepare summary",
      estimated_minutes: 90,
      priority: 5,
      difficulty: 4,
      energy_required: 0.7,
      focus_required: 0.9,
      category: "work",
      tags: ["urgent", "analysis"]
    },
    {
      title: "Team meeting preparation",
      description: "Prepare agenda and slides for Monday's team meeting",
      estimated_minutes: 45,
      priority: 4,
      difficulty: 2,
      energy_required: 0.5,
      focus_required: 0.6,
      category: "work",
      tags: ["meeting", "preparation"]
    },
    {
      title: "Grocery shopping",
      description: "Buy ingredients for weekly meal prep",
      estimated_minutes: 30,
      priority: 2,
      difficulty: 1,
      energy_required: 0.3,
      focus_required: 0.2,
      category: "personal",
      tags: ["errands"]
    },
    {
      title: "Write blog post draft",
      description: "Draft article about productivity tips",
      estimated_minutes: 120,
      priority: 3,
      difficulty: 3,
      energy_required: 0.6,
      focus_required: 0.8,
      category: "work",
      tags: ["writing", "creative"]
    },
    {
      title: "Exercise - Morning run",
      description: "5K run in the park",
      estimated_minutes: 40,
      priority: 3,
      difficulty: 2,
      energy_required: 0.4,
      focus_required: 0.3,
      category: "health",
      tags: ["exercise", "routine"]
    },
    {
      title: "Client proposal review",
      description: "Review and finalize proposal for new client project",
      estimated_minutes: 60,
      priority: 5,
      difficulty: 4,
      energy_required: 0.8,
      focus_required: 0.9,
      category: "work",
      tags: ["urgent", "client"]
    },
    {
      title: "Read research papers",
      description: "Read 3 papers on machine learning applications",
      estimated_minutes: 90,
      priority: 2,
      difficulty: 3,
      energy_required: 0.6,
      focus_required: 0.7,
      category: "learning",
      tags: ["research", "reading"]
    },
    {
      title: "Update project documentation",
      description: "Update API documentation and user guides",
      estimated_minutes: 75,
      priority: 3,
      difficulty: 2,
      energy_required: 0.5,
      focus_required: 0.6,
      category: "work",
      tags: ["documentation", "maintenance"]
    },
    {
      title: "Plan weekend trip",
      description: "Research hotels and activities for weekend getaway",
      estimated_minutes: 45,
      priority: 2,
      difficulty: 1,
      energy_required: 0.3,
      focus_required: 0.4,
      category: "personal",
      tags: ["planning", "leisure"]
    },
    {
      title: "Code review and refactoring",
      description: "Review pull requests and refactor legacy code",
      estimated_minutes: 120,
      priority: 4,
      difficulty: 4,
      energy_required: 0.7,
      focus_required: 0.85,
      category: "work",
      tags: ["coding", "technical"]
    }
  ];

  const generateTestTasks = async () => {
    setIsGenerating(true);
    setGeneratedTasks([]);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      const createdTasks = [];
      const errors = [];

      // Create tasks one by one
      for (const taskData of testTasks) {
        try {
          const response = await axios.post(
            `${API_BASE_URL}/api/tasks/`,
            taskData,
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

      setGeneratedTasks(createdTasks);

      if (createdTasks.length === testTasks.length) {
        addNotification({
          type: 'success',
          title: 'Test Tasks Created!',
          message: `Successfully created ${createdTasks.length} test tasks. Check the Tasks tab to see them.`,
          persistent: false
        });
      } else if (createdTasks.length > 0) {
        addNotification({
          type: 'warning',
          title: 'Partial Success',
          message: `Created ${createdTasks.length} out of ${testTasks.length} tasks. ${errors.length} failed.`,
          persistent: false
        });
      } else {
        addNotification({
          type: 'error',
          title: 'Failed to Create Tasks',
          message: `Could not create any tasks. Please check your connection and try again.`,
          persistent: false
        });
      }

    } catch (error) {
      console.error('Failed to generate test tasks:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.detail || error.message || 'Failed to generate test tasks',
        persistent: false
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className={`text-2xl font-semibold mb-2 flex items-center gap-2 ${
          isDark ? 'text-white' : 'text-slate-900'
        }`}>
          <TestTube className={isDark ? 'text-purple-400' : 'text-emerald-600'} />
          Scheduler Tester
        </h2>
        <p className={`text-sm ${
          isDark ? 'text-neutral-400' : 'text-slate-600'
        }`}>
          Generate 10 realistic test tasks to test the ML-powered scheduler
        </p>
      </div>

      <div className={`p-6 rounded-lg border ${
        isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-slate-200'
      }`}>
        <div className="mb-4">
          <h3 className={`font-medium mb-2 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Test Tasks Preview
          </h3>
          <p className={`text-sm mb-4 ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            The following tasks will be created with varying priorities, difficulties, and energy requirements:
          </p>
          
          <div className={`space-y-2 max-h-64 overflow-y-auto ${
            isDark ? 'bg-neutral-950' : 'bg-slate-50'
          } p-4 rounded-lg`}>
            {testTasks.map((task, idx) => (
              <div key={idx} className={`text-sm ${
                isDark ? 'text-neutral-300' : 'text-slate-700'
              }`}>
                <span className="font-medium">{idx + 1}. {task.title}</span>
                <span className={`ml-2 text-xs ${
                  isDark ? 'text-neutral-500' : 'text-slate-500'
                }`}>
                  (Priority: {task.priority}, Difficulty: {task.difficulty}, {task.estimated_minutes} min)
                </span>
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={generateTestTasks}
          disabled={isGenerating}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
            isGenerating
              ? isDark
                ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              : isDark
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/30'
              : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg shadow-emerald-500/20'
          }`}
        >
          {isGenerating ? (
            <>
              <Loader className="animate-spin" size={18} />
              <span>Generating Tasks...</span>
            </>
          ) : (
            <>
              <TestTube size={18} />
              <span>Generate 10 Test Tasks</span>
            </>
          )}
        </button>

        {generatedTasks.length > 0 && (
          <div className={`mt-4 p-4 rounded-lg ${
            isDark ? 'bg-emerald-950/20 border border-emerald-800' : 'bg-emerald-50 border border-emerald-200'
          }`}>
            <div className="flex items-start gap-2">
              <CheckCircle2 className={`flex-shrink-0 mt-0.5 ${
                isDark ? 'text-emerald-400' : 'text-emerald-600'
              }`} size={18} />
              <div className="flex-1">
                <p className={`font-medium mb-1 ${
                  isDark ? 'text-emerald-300' : 'text-emerald-900'
                }`}>
                  Successfully Created {generatedTasks.length} Tasks
                </p>
                <p className={`text-sm ${
                  isDark ? 'text-emerald-400' : 'text-emerald-700'
                }`}>
                  Tasks have been automatically scheduled using the ML optimizer. 
                  Go to the <strong>Tasks</strong> tab to view them, or check the <strong>Schedule</strong> tab to see the optimized schedule.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

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
          <li>• Creates 10 diverse tasks with different priorities, difficulties, and energy requirements</li>
          <li>• Automatically triggers the ML scheduler to optimize the schedule</li>
          <li>• Tasks are immediately available in the Tasks tab</li>
          <li>• The Schedule tab will show the ML-optimized schedule</li>
          <li>• Perfect for testing the scheduling algorithm with realistic data</li>
        </ul>
      </div>
    </div>
  );
}
