import React, { createContext, useContext, useState, useCallback } from 'react';
import { Bell, X, CheckCircle2, Clock, AlertCircle, Info } from 'lucide-react';

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [showPanel, setShowPanel] = useState(false);

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: notification.type || 'info', // 'success', 'info', 'warning', 'error'
      title: notification.title || 'Notification',
      message: notification.message || '',
      timestamp: new Date(),
      read: false,
      ...notification
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Auto-dismiss after 5 seconds for non-persistent notifications
    if (!notification.persistent) {
      setTimeout(() => {
        dismissNotification(id);
      }, 5000);
    }

    return id;
  }, []);

  const dismissNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const markAsRead = useCallback((id) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        dismissNotification,
        markAsRead,
        markAllAsRead,
        clearAll,
        showPanel,
        setShowPanel,
        unreadCount
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}
