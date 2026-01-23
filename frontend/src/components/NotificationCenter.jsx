import React, { useEffect, useRef } from 'react';
import { Bell, X, CheckCircle2, Clock, AlertCircle, Info, Trash2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useNotifications } from '../contexts/NotificationContext';

export default function NotificationCenter() {
  const { isDark } = useTheme();
  const {
    notifications,
    showPanel,
    setShowPanel,
    dismissNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    unreadCount
  } = useNotifications();

  const panelRef = useRef(null);

  // Close panel when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (panelRef.current && !panelRef.current.contains(event.target)) {
        // Check if click is not on the bell icon
        if (!event.target.closest('.notification-bell')) {
          setShowPanel(false);
        }
      }
    };

    if (showPanel) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showPanel, setShowPanel]);

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 size={18} className="text-emerald-500" />;
      case 'warning':
        return <AlertCircle size={18} className="text-yellow-500" />;
      case 'error':
        return <AlertCircle size={18} className="text-red-500" />;
      case 'timer':
        return <Clock size={18} className="text-purple-500" />;
      default:
        return <Info size={18} className="text-blue-500" />;
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return time.toLocaleDateString();
  };

  return (
    <div className="relative">
      {/* Bell Icon Button */}
      <button
        onClick={() => setShowPanel(!showPanel)}
        className={`notification-bell relative p-2 rounded-lg transition-all duration-200 ${
          isDark
            ? 'hover:bg-neutral-800 text-neutral-300'
            : 'hover:bg-slate-100 text-slate-600'
        }`}
        aria-label="Notifications"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className={`absolute -top-1 -right-1 flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold ${
            isDark
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
              : 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
          }`}>
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {showPanel && (
        <div
          ref={panelRef}
          className={`absolute right-0 top-12 w-80 sm:w-96 max-h-[600px] rounded-xl border shadow-2xl z-50 overflow-hidden ${
            isDark
              ? 'bg-neutral-950 border-neutral-800'
              : 'bg-white border-slate-200'
          }`}
        >
          {/* Header */}
          <div className={`flex items-center justify-between p-4 border-b ${
            isDark ? 'border-neutral-800' : 'border-slate-200'
          }`}>
            <div className="flex items-center gap-2">
              <h3 className={`font-semibold ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}>
                Notifications
              </h3>
              {unreadCount > 0 && (
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  isDark
                    ? 'bg-purple-600 text-white'
                    : 'bg-emerald-500 text-white'
                }`}>
                  {unreadCount} new
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {notifications.length > 0 && (
                <>
                  <button
                    onClick={markAllAsRead}
                    className={`text-xs px-2 py-1 rounded transition-colors ${
                      isDark
                        ? 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    Mark all read
                  </button>
                  <button
                    onClick={clearAll}
                    className={`p-1 rounded transition-colors ${
                      isDark
                        ? 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                    aria-label="Clear all"
                  >
                    <Trash2 size={16} />
                  </button>
                </>
              )}
              <button
                onClick={() => setShowPanel(false)}
                className={`p-1 rounded transition-colors ${
                  isDark
                    ? 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="overflow-y-auto max-h-[500px]">
            {notifications.length === 0 ? (
              <div className={`p-8 text-center ${
                isDark ? 'text-neutral-500' : 'text-slate-500'
              }`}>
                <Bell size={32} className="mx-auto mb-2 opacity-50" />
                <p>No notifications</p>
              </div>
            ) : (
              <div className="divide-y divide-solid">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => markAsRead(notification.id)}
                    className={`p-4 transition-colors cursor-pointer ${
                      notification.read
                        ? isDark
                          ? 'bg-neutral-950'
                          : 'bg-white'
                        : isDark
                        ? 'bg-neutral-900/50'
                        : 'bg-emerald-50/30'
                    } hover:${
                      isDark ? 'bg-neutral-900' : 'bg-slate-50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {getIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <h4 className={`font-medium mb-1 ${
                              isDark ? 'text-white' : 'text-slate-900'
                            }`}>
                              {notification.title}
                            </h4>
                            {notification.message && (
                              <p className={`text-sm ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                              }`}>
                                {notification.message}
                              </p>
                            )}
                            <p className={`text-xs mt-1 ${
                              isDark ? 'text-neutral-600' : 'text-slate-400'
                            }`}>
                              {formatTime(notification.timestamp)}
                            </p>
                          </div>
                          {!notification.read && (
                            <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-2 ${
                              isDark
                                ? 'bg-purple-500'
                                : 'bg-emerald-500'
                            }`} />
                          )}
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          dismissNotification(notification.id);
                        }}
                        className={`flex-shrink-0 p-1 rounded transition-colors ${
                          isDark
                            ? 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-800'
                            : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'
                        }`}
                        aria-label="Dismiss"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
