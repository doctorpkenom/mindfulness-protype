import { Calendar } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';

export default function DatePicker({ value, onChange, placeholder = "Select date", showTime = false }) {
  const { isDark } = useTheme();
  const [showCalendar, setShowCalendar] = useState(false);
  const [selectedDate, setSelectedDate] = useState(value || '');
  const [selectedTime, setSelectedTime] = useState(value ? value.split('T')[1]?.slice(0, 5) || '' : '');
  const calendarRef = useRef(null);

  useEffect(() => {
    if (value) {
      const datePart = value.split('T')[0];
      setSelectedDate(datePart);
      if (showTime && value.includes('T')) {
        const timePart = value.split('T')[1];
        if (timePart) {
          setSelectedTime(timePart.slice(0, 5));
        }
      }
    } else {
      setSelectedDate('');
      setSelectedTime('');
    }
  }, [value, showTime]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (calendarRef.current && !calendarRef.current.contains(event.target)) {
        setShowCalendar(false);
      }
    };

    if (showCalendar) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showCalendar]);

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    if (showTime) {
      // If time is already selected, combine them
      const time = selectedTime || '00:00';
      onChange(`${date}T${time}:00`);
    } else {
      // Just date, no time
      onChange(date);
      setShowCalendar(false);
    }
  };

  const handleTimeChange = (time) => {
    setSelectedTime(time);
    if (selectedDate) {
      onChange(`${selectedDate}T${time}:00`);
    }
  };

  const getCurrentMonthDays = () => {
    if (!selectedDate) {
      const today = new Date();
      const year = today.getFullYear();
      const month = today.getMonth();
      return { year, month };
    }
    const date = new Date(selectedDate + 'T00:00:00');
    return { year: date.getFullYear(), month: date.getMonth() };
  };

  const [currentMonth, setCurrentMonth] = useState(() => getCurrentMonthDays());

  const daysInMonth = new Date(currentMonth.year, currentMonth.month + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentMonth.year, currentMonth.month, 1).getDay();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const days = [];
  // Empty cells for days before the first day of the month
  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push(null);
  }
  // Days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    days.push(day);
  }

  const navigateMonth = (direction) => {
    setCurrentMonth(prev => {
      const newDate = new Date(prev.year, prev.month + direction, 1);
      return { year: newDate.getFullYear(), month: newDate.getMonth() };
    });
  };

  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const isToday = (day) => {
    if (!day) return false;
    const date = new Date(currentMonth.year, currentMonth.month, day);
    return date.getTime() === today.getTime();
  };

  const isSelected = (day) => {
    if (!day || !selectedDate) return false;
    const date = new Date(currentMonth.year, currentMonth.month, day);
    const selected = new Date(selectedDate + 'T00:00:00');
    return date.getTime() === selected.getTime();
  };

  const formatDisplayValue = () => {
    if (!selectedDate) return placeholder;
    const date = new Date(selectedDate + 'T00:00:00');
    const formatted = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    return showTime && selectedTime ? `${formatted} ${selectedTime}` : formatted;
  };

  return (
    <div className="relative" ref={calendarRef}>
      <div className="relative">
        <input
          type="text"
          value={formatDisplayValue()}
          readOnly
          onClick={() => setShowCalendar(!showCalendar)}
          placeholder={placeholder}
          className={`w-full px-4 py-2 pr-10 rounded-lg border cursor-pointer ${
            isDark
              ? 'bg-neutral-900 border-neutral-700 text-white'
              : 'bg-slate-50 border-slate-300 text-slate-900'
          } focus:outline-none focus:ring-2 ${
            isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
          }`}
        />
        <button
          type="button"
          onClick={() => setShowCalendar(!showCalendar)}
          className={`absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded ${
            isDark ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'
          }`}
        >
          <Calendar size={18} className={isDark ? 'text-neutral-400' : 'text-slate-500'} />
        </button>
      </div>

      {showCalendar && (
        <div className={`absolute z-50 mt-2 rounded-lg border shadow-xl ${
          isDark ? 'bg-neutral-900 border-neutral-700' : 'bg-white border-slate-200'
        }`} style={{ minWidth: '300px' }}>
          {/* Calendar Header */}
          <div className={`p-4 border-b ${
            isDark ? 'border-neutral-700' : 'border-slate-200'
          }`}>
            <div className="flex items-center justify-between mb-2">
              <button
                onClick={() => navigateMonth(-1)}
                className={`p-1 rounded ${
                  isDark ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'
                }`}
              >
                <span className={isDark ? 'text-neutral-300' : 'text-slate-700'}>‹</span>
              </button>
              <h3 className={`font-semibold ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}>
                {monthNames[currentMonth.month]} {currentMonth.year}
              </h3>
              <button
                onClick={() => navigateMonth(1)}
                className={`p-1 rounded ${
                  isDark ? 'hover:bg-neutral-800' : 'hover:bg-slate-100'
                }`}
              >
                <span className={isDark ? 'text-neutral-300' : 'text-slate-700'}>›</span>
              </button>
            </div>
            
            {/* Day Names */}
            <div className="grid grid-cols-7 gap-1 mb-2">
              {dayNames.map(day => (
                <div key={day} className={`text-center text-xs font-medium ${
                  isDark ? 'text-neutral-400' : 'text-slate-500'
                }`}>
                  {day}
                </div>
              ))}
            </div>
          </div>

          {/* Calendar Days */}
          <div className="p-4">
            <div className="grid grid-cols-7 gap-1">
              {days.map((day, index) => (
                <button
                  key={index}
                  onClick={() => day && handleDateSelect(
                    `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
                  )}
                  disabled={!day}
                  className={`h-8 rounded text-sm transition-all ${
                    !day ? 'cursor-default' : 'cursor-pointer'
                  } ${
                    isSelected(day)
                      ? isDark
                        ? 'bg-purple-600 text-white'
                        : 'bg-emerald-500 text-white'
                      : isToday(day)
                      ? isDark
                        ? 'bg-purple-500/20 text-purple-400 border border-purple-500'
                        : 'bg-emerald-100 text-emerald-700 border border-emerald-500'
                      : isDark
                      ? 'hover:bg-neutral-800 text-neutral-300'
                      : 'hover:bg-slate-100 text-slate-700'
                  }`}
                >
                  {day}
                </button>
              ))}
            </div>
          </div>

          {/* Time Picker (if enabled) */}
          {showTime && (
            <div className={`p-4 border-t ${
              isDark ? 'border-neutral-700' : 'border-slate-200'
            }`}>
              <label className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-neutral-300' : 'text-slate-700'
              }`}>
                Time
              </label>
              <input
                type="time"
                value={selectedTime}
                onChange={(e) => handleTimeChange(e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border ${
                  isDark
                    ? 'bg-neutral-800 border-neutral-700 text-white'
                    : 'bg-slate-50 border-slate-300 text-slate-900'
                } focus:outline-none focus:ring-2 ${
                  isDark ? 'focus:ring-purple-500' : 'focus:ring-emerald-500'
                }`}
              />
            </div>
          )}

          {/* Close Button */}
          <div className={`p-2 border-t ${
            isDark ? 'border-neutral-700' : 'border-slate-200'
          } flex justify-end`}>
            <button
              onClick={() => setShowCalendar(false)}
              className={`px-4 py-1 rounded text-sm ${
                isDark
                  ? 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
