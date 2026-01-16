import React, { useEffect, useState } from 'react';
import { UserPlus, User as UserIcon, Loader2 } from 'lucide-react';
import { userApi } from '../api';

const UserTab = () => {
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
                <h2 className="text-3xl font-bold text-white mb-2">User Management</h2>
                <p className="text-slate-400">Create and manage simulated personas for testing.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Create Form */}
                <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg h-fit">
                    <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                        <UserPlus className="mr-2 text-blue-400" size={20} />
                        New Persona
                    </h3>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Name</label>
                            <input
                                type="text"
                                required
                                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="e.g. Busy Exec"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Base Stress ({formData.stress})</label>
                            <input
                                type="range" min="0" max="1" step="0.1"
                                className="w-full accent-blue-500"
                                value={formData.stress}
                                onChange={(e) => setFormData({ ...formData, stress: parseFloat(e.target.value) })}
                            />
                            <div className="flex justify-between text-xs text-slate-500">
                                <span>Relaxed</span>
                                <span>Overwhelmed</span>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Base Energy ({formData.energy})</label>
                            <input
                                type="range" min="0" max="1" step="0.1"
                                className="w-full accent-amber-500"
                                value={formData.energy}
                                onChange={(e) => setFormData({ ...formData, energy: parseFloat(e.target.value) })}
                            />
                            <div className="flex justify-between text-xs text-slate-500">
                                <span>Lethargic</span>
                                <span>Hyper</span>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={creating}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors flex justify-center items-center"
                        >
                            {creating ? <Loader2 className="animate-spin" size={20} /> : "Create User"}
                        </button>
                    </form>
                </div>

                {/* User Grid */}
                <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4 content-start">
                    {loading ? (
                        <div className="text-slate-500 col-span-2 text-center py-10">Loading users...</div>
                    ) : users.length === 0 ? (
                        <div className="text-slate-500 col-span-2 text-center py-10 bg-slate-800/50 rounded-xl border border-dahed border-slate-700">
                            No users found. Create one to get started.
                        </div>
                    ) : (
                        users.map((user) => (
                            <div key={user.name} className="bg-slate-800 p-5 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center text-slate-300">
                                            <UserIcon size={20} />
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-white">{user.name}</h4>
                                            <span className="text-xs text-slate-500">Resilience: {user.resilience}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <div>
                                        <div className="flex justify-between text-xs text-slate-400 mb-1">
                                            <span>Stress Level</span>
                                            <span>{(user.base_stress * 100).toFixed(0)}%</span>
                                        </div>
                                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                            <div className="h-full bg-rose-500" style={{ width: `${user.base_stress * 100}%` }} />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-xs text-slate-400 mb-1">
                                            <span>Energy Level</span>
                                            <span>{(user.base_energy * 100).toFixed(0)}%</span>
                                        </div>
                                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                            <div className="h-full bg-amber-500" style={{ width: `${user.base_energy * 100}%` }} />
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
