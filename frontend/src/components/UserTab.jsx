import React, { useEffect, useState } from 'react';
import { UserPlus, User as UserIcon, Loader2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { userApi } from '../api';

const UserTab = () => {
    const { isDark } = useTheme();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [formData, setFormData] = useState({ name: '', stress: 0.5, energy: 0.5 });
    const [creating, setCreating] = useState(false);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const res = await userApi.getAll();
            setUsers(res.data);
        } catch (err) {
            console.error("Failed to fetch users", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setCreating(true);
        try {
            await userApi.create(formData);
            setFormData({ name: '', stress: 0.5, energy: 0.5 });
            fetchUsers(); // Refresh list
        } catch (err) {
            alert("Error creating user: " + err.message);
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="p-8 space-y-8">
            <header>
                <h2 className={`text-3xl font-bold mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    User Management
                </h2>
                <p className={isDark ? 'text-neutral-400' : 'text-slate-600'}>
                    Create and manage simulated personas for testing.
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Create Form */}
                <div className={`p-6 rounded-xl border shadow-lg h-fit theme-transition ${
                    isDark 
                        ? 'bg-neutral-950/50 border-neutral-800' 
                        : 'bg-white border-slate-200'
                }`}>
                    <h3 className={`text-xl font-semibold mb-6 flex items-center ${
                        isDark ? 'text-white' : 'text-slate-900'
                    }`}>
                        <UserPlus className={`mr-2 ${isDark ? 'text-purple-400' : 'text-emerald-600'}`} size={20} />
                        New Persona
                    </h3>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className={`block text-sm font-medium mb-1 ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                            }`}>
                                Name
                            </label>
                            <input
                                type="text"
                                required
                                className={`w-full border rounded-lg p-2.5 outline-none theme-transition ${
                                    isDark
                                        ? 'bg-neutral-900/50 border-neutral-700 text-white focus:ring-2 focus:ring-purple-500'
                                        : 'bg-slate-50 border-slate-200 text-slate-900 focus:ring-2 focus:ring-emerald-500'
                                }`}
                                placeholder="e.g. Busy Exec"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className={`block text-sm font-medium mb-1 ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                            }`}>
                                Base Stress ({formData.stress})
                            </label>
                            <input
                                type="range" min="0" max="1" step="0.1"
                                className={`w-full ${isDark ? 'accent-pink-500' : 'accent-rose-500'}`}
                                value={formData.stress}
                                onChange={(e) => setFormData({ ...formData, stress: parseFloat(e.target.value) })}
                            />
                            <div className={`flex justify-between text-xs ${
                                isDark ? 'text-neutral-500' : 'text-slate-500'
                            }`}>
                                <span>Relaxed</span>
                                <span>Overwhelmed</span>
                            </div>
                        </div>

                        <div>
                            <label className={`block text-sm font-medium mb-1 ${
                                isDark ? 'text-neutral-400' : 'text-slate-600'
                            }`}>
                                Base Energy ({formData.energy})
                            </label>
                            <input
                                type="range" min="0" max="1" step="0.1"
                                className={`w-full ${isDark ? 'accent-purple-500' : 'accent-amber-500'}`}
                                value={formData.energy}
                                onChange={(e) => setFormData({ ...formData, energy: parseFloat(e.target.value) })}
                            />
                            <div className={`flex justify-between text-xs ${
                                isDark ? 'text-neutral-500' : 'text-slate-500'
                            }`}>
                                <span>Lethargic</span>
                                <span>Hyper</span>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={creating}
                            className={`w-full font-medium py-2.5 rounded-lg transition-all flex justify-center items-center ${
                                isDark
                                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-lg shadow-purple-500/20'
                                    : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/10'
                            }`}
                        >
                            {creating ? <Loader2 className="animate-spin" size={20} /> : "Create User"}
                        </button>
                    </form>
                </div>

                {/* User Grid */}
                <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4 content-start">
                    {loading ? (
                        <div className={`col-span-2 text-center py-10 ${
                            isDark ? 'text-neutral-500' : 'text-slate-500'
                        }`}>
                            Loading users...
                        </div>
                    ) : users.length === 0 ? (
                        <div className={`col-span-2 text-center py-10 rounded-xl border-2 border-dashed theme-transition ${
                            isDark 
                                ? 'text-neutral-500 bg-neutral-900/30 border-neutral-800' 
                                : 'text-slate-500 bg-slate-50 border-slate-200'
                        }`}>
                            No users found. Create one to get started.
                        </div>
                    ) : (
                        users.map((user) => (
                            <div key={user.name} className={`p-5 rounded-xl border transition-all theme-transition ${
                                isDark
                                    ? 'bg-neutral-950/50 border-neutral-800 hover:border-neutral-700'
                                    : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-md'
                            }`}>
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                                            isDark
                                                ? 'bg-neutral-900 text-neutral-400'
                                                : 'bg-slate-100 text-slate-600'
                                        }`}>
                                            <UserIcon size={20} />
                                        </div>
                                        <div>
                                            <h4 className={`font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                                {user.name}
                                            </h4>
                                            <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'}`}>
                                                Resilience: {user.resilience}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <div>
                                        <div className={`flex justify-between text-xs mb-1 ${
                                            isDark ? 'text-neutral-400' : 'text-slate-600'
                                        }`}>
                                            <span>Stress Level</span>
                                            <span>{(user.base_stress * 100).toFixed(0)}%</span>
                                        </div>
                                        <div className={`h-1.5 rounded-full overflow-hidden ${
                                            isDark ? 'bg-neutral-900' : 'bg-slate-200'
                                        }`}>
                                            <div className={`h-full ${isDark ? 'bg-pink-500' : 'bg-rose-500'}`} 
                                                 style={{ width: `${user.base_stress * 100}%` }} />
                                        </div>
                                    </div>
                                    <div>
                                        <div className={`flex justify-between text-xs mb-1 ${
                                            isDark ? 'text-neutral-400' : 'text-slate-600'
                                        }`}>
                                            <span>Energy Level</span>
                                            <span>{(user.base_energy * 100).toFixed(0)}%</span>
                                        </div>
                                        <div className={`h-1.5 rounded-full overflow-hidden ${
                                            isDark ? 'bg-neutral-900' : 'bg-slate-200'
                                        }`}>
                                            <div className={`h-full ${isDark ? 'bg-purple-500' : 'bg-amber-500'}`} 
                                                 style={{ width: `${user.base_energy * 100}%` }} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default UserTab;
