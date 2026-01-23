import React, { useState, useEffect } from 'react';
import { Users, Edit, Trash2, Save, X, Shield } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useNotifications } from '../contexts/NotificationContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function UserManagementTab() {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/admin/accounts`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      setAccounts(response.data);
    } catch (error) {
      console.error('Failed to load accounts:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to load accounts',
        persistent: true
      });
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (account) => {
    setEditingId(account.id);
    setEditForm({
      username: account.username,
      email: account.email,
      is_admin: account.is_admin,
      is_active: account.is_active
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  const saveEdit = async (accountId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_BASE_URL}/api/admin/accounts/${accountId}`,
        editForm,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Account updated successfully',
        persistent: false
      });
      setEditingId(null);
      setEditForm({});
      loadAccounts();
    } catch (error) {
      console.error('Failed to update account:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.detail || 'Failed to update account',
        persistent: true
      });
    }
  };

  const deleteAccount = async (accountId, username) => {
    if (!window.confirm(`Are you sure you want to delete account "${username}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${API_BASE_URL}/api/admin/accounts/${accountId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Account deleted successfully',
        persistent: false
      });
      loadAccounts();
    } catch (error) {
      console.error('Failed to delete account:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.detail || 'Failed to delete account',
        persistent: true
      });
    }
  };

  if (loading) {
    return (
      <div className={`p-8 text-center ${isDark ? 'text-white' : 'text-slate-900'}`}>
        Loading accounts...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className={`text-2xl font-bold mb-2 flex items-center gap-2 ${
          isDark ? 'text-white' : 'text-slate-900'
        }`}>
          <Users className={isDark ? 'text-purple-400' : 'text-emerald-600'} />
          User Account Management
        </h2>
        <p className={`text-sm ${
          isDark ? 'text-neutral-400' : 'text-slate-600'
        }`}>
          View, edit, and manage all user accounts in the system
        </p>
      </div>

      <div className={`rounded-xl border ${
        isDark ? 'bg-neutral-950 border-neutral-800' : 'bg-white border-slate-200'
      }`}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className={`border-b ${
                isDark ? 'border-neutral-800' : 'border-slate-200'
              }`}>
                <th className={`px-4 py-3 text-left text-sm font-semibold ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>ID</th>
                <th className={`px-4 py-3 text-left text-sm font-semibold ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>Username</th>
                <th className={`px-4 py-3 text-left text-sm font-semibold ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>Email</th>
                <th className={`px-4 py-3 text-left text-sm font-semibold ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>Admin</th>
                <th className={`px-4 py-3 text-left text-sm font-semibold ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>Active</th>
                <th className={`px-4 py-3 text-left text-sm font-semibold ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>Created</th>
                <th className={`px-4 py-3 text-left text-sm font-semibold ${
                  isDark ? 'text-neutral-300' : 'text-slate-700'
                }`}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {accounts.map((account) => (
                <tr
                  key={account.id}
                  className={`border-b ${
                    isDark ? 'border-neutral-800 hover:bg-neutral-900' : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <td className={`px-4 py-3 text-sm ${
                    isDark ? 'text-neutral-400' : 'text-slate-600'
                  }`}>
                    {account.id}
                  </td>
                  <td className={`px-4 py-3 text-sm ${
                    isDark ? 'text-white' : 'text-slate-900'
                  }`}>
                    {editingId === account.id ? (
                      <input
                        type="text"
                        value={editForm.username}
                        onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                        className={`w-full px-2 py-1 rounded border ${
                          isDark
                            ? 'bg-neutral-900 border-neutral-700 text-white'
                            : 'bg-white border-slate-300 text-slate-900'
                        }`}
                      />
                    ) : (
                      account.username
                    )}
                  </td>
                  <td className={`px-4 py-3 text-sm ${
                    isDark ? 'text-white' : 'text-slate-900'
                  }`}>
                    {editingId === account.id ? (
                      <input
                        type="email"
                        value={editForm.email}
                        onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                        className={`w-full px-2 py-1 rounded border ${
                          isDark
                            ? 'bg-neutral-900 border-neutral-700 text-white'
                            : 'bg-white border-slate-300 text-slate-900'
                        }`}
                      />
                    ) : (
                      account.email
                    )}
                  </td>
                  <td className={`px-4 py-3 text-sm ${
                    isDark ? 'text-white' : 'text-slate-900'
                  }`}>
                    {editingId === account.id ? (
                      <input
                        type="checkbox"
                        checked={editForm.is_admin}
                        onChange={(e) => setEditForm({ ...editForm, is_admin: e.target.checked })}
                        className="w-4 h-4"
                      />
                    ) : (
                      account.is_admin ? (
                        <span className="flex items-center gap-1">
                          <Shield size={16} className={isDark ? 'text-purple-400' : 'text-emerald-600'} />
                          Yes
                        </span>
                      ) : (
                        'No'
                      )
                    )}
                  </td>
                  <td className={`px-4 py-3 text-sm ${
                    isDark ? 'text-white' : 'text-slate-900'
                  }`}>
                    {editingId === account.id ? (
                      <input
                        type="checkbox"
                        checked={editForm.is_active}
                        onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                        className="w-4 h-4"
                      />
                    ) : (
                      account.is_active ? 'Yes' : 'No'
                    )}
                  </td>
                  <td className={`px-4 py-3 text-sm ${
                    isDark ? 'text-neutral-400' : 'text-slate-600'
                  }`}>
                    {new Date(account.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {editingId === account.id ? (
                        <>
                          <button
                            onClick={() => saveEdit(account.id)}
                            className={`p-1 rounded hover:bg-opacity-80 ${
                              isDark ? 'text-green-400 hover:bg-green-400/20' : 'text-green-600 hover:bg-green-100'
                            }`}
                            title="Save"
                          >
                            <Save size={16} />
                          </button>
                          <button
                            onClick={cancelEdit}
                            className={`p-1 rounded hover:bg-opacity-80 ${
                              isDark ? 'text-red-400 hover:bg-red-400/20' : 'text-red-600 hover:bg-red-100'
                            }`}
                            title="Cancel"
                          >
                            <X size={16} />
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => startEdit(account)}
                            className={`p-1 rounded hover:bg-opacity-80 ${
                              isDark ? 'text-blue-400 hover:bg-blue-400/20' : 'text-blue-600 hover:bg-blue-100'
                            }`}
                            title="Edit"
                          >
                            <Edit size={16} />
                          </button>
                          <button
                            onClick={() => deleteAccount(account.id, account.username)}
                            className={`p-1 rounded hover:bg-opacity-80 ${
                              isDark ? 'text-red-400 hover:bg-red-400/20' : 'text-red-600 hover:bg-red-100'
                            }`}
                            title="Delete"
                          >
                            <Trash2 size={16} />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {accounts.length === 0 && (
            <div className={`p-8 text-center ${
              isDark ? 'text-neutral-400' : 'text-slate-600'
            }`}>
              No accounts found
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
