import React, { createContext, useContext, useState, useCallback } from 'react';
import { Bell, X, CheckCircle2, Clock, AlertCircle, Info } from 'lucide-react';

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [activeToasts, setActiveToasts] = useState([]);
  const [showPanel, setShowPanel] = useState(false);

  const dismissNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    setActiveToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const dismissToast = useCallback((id) => {
    // Remove from toasts but keep in notifications list
    setActiveToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addNotification = useCallback((notification) => {
    console.log('[NOTIFICATION] Adding notification:', notification);
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: notification.type || 'info', // 'success', 'info', 'warning', 'error', 'timer'
      title: notification.title || 'Notification',
      message: notification.message || '',
      timestamp: new Date(),
      read: false,
      ...notification
    };

    console.log('[NOTIFICATION] Created notification object:', newNotification);

    // Add to notifications list (for the notification center)
    setNotifications(prev => {
      console.log('[NOTIFICATION] Adding to notifications list, current count:', prev.length);
      return [newNotification, ...prev];
    });

    // Show as toast for 5 seconds with countdown
    if (!notification.persistent) {
      console.log('[NOTIFICATION] Adding toast, persistent:', notification.persistent);
      setActiveToasts(prev => {
        console.log('[NOTIFICATION] Current toasts:', prev.length, 'Adding new one');
        return [...prev, { ...newNotification, countdown: 0 }];
      });
      
      // Countdown animation - fills from 0% to 100% (flipped direction)
      const startTime = Date.now();
      const duration = 5000; // 5 seconds
      const interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(100, (elapsed / duration) * 100);
        
        setActiveToasts(prev =>
          prev.map(toast =>
            toast.id === id ? { ...toast, countdown: progress } : toast
          )
        );

        if (progress >= 100) {
          clearInterval(interval);
          console.log('[NOTIFICATION] Toast countdown complete, removing toast');
          // Remove from toasts but keep in notifications list
          setActiveToasts(prev => prev.filter(toast => toast.id !== id));
        }
      }, 50); // Update every 50ms for smooth animation
    } else {
      console.log('[NOTIFICATION] Notification is persistent, not showing toast');
    }

    return id;
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
    setActiveToasts([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        activeToasts,
        addNotification,
        dismissNotification,
        dismissToast,
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
