import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { LogIn, UserPlus, Loader } from 'lucide-react';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, signup } = useAuth();
  const { isDark, colors } = useTheme();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    let result;
    if (isLogin) {
      result = await login(username || email, password);
    } else {
      if (!email || !username || !password) {
        setError('Please fill in all fields');
        setLoading(false);
        return;
      }
      result = await signup(email, username, password);
    }

    setLoading(false);
    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className={`min-h-screen flex items-center justify-center p-8 theme-transition ${
      isDark ? 'bg-black' : 'bg-slate-50'
    }`}>
      <div className={`w-full max-w-md rounded-2xl shadow-2xl p-8 theme-transition ${
        isDark ? 'bg-neutral-950 border border-neutral-800' : 'bg-white border border-slate-200'
      }`}>
        <div className="text-center mb-8">
          <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center ${
            isDark 
              ? 'bg-gradient-to-br from-purple-600 to-pink-600' 
              : 'bg-gradient-to-br from-emerald-500 to-teal-500'
          }`}>
            <LogIn className="text-white" size={32} />
          </div>
          <h1 className={`text-3xl font-bold mb-2 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Productivity Assistant
          </h1>
          <p className={`text-sm ${
            isDark ? 'text-neutral-400' : 'text-slate-600'
          }`}>
            {isLogin ? 'Sign in to continue' : 'Create your account'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-neutral-300' : 'text-slate-700'
              }`}>
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`w-full px-4 py-3 rounded-lg border transition-colors ${
                  isDark
                    ? 'bg-neutral-900 border-neutral-700 text-white placeholder-neutral-500 focus:border-purple-500'
                    : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 focus:border-emerald-500'
                } focus:outline-none focus:ring-2 ${
                  isDark ? 'focus:ring-purple-500/20' : 'focus:ring-emerald-500/20'
                }`}
                placeholder="you@example.com"
                required={!isLogin}
              />
            </div>
          )}

          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-neutral-300' : 'text-slate-700'
            }`}>
              {isLogin ? 'Username or Email' : 'Username'}
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={`w-full px-4 py-3 rounded-lg border transition-colors ${
                isDark
                  ? 'bg-neutral-900 border-neutral-700 text-white placeholder-neutral-500 focus:border-purple-500'
                  : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 focus:border-emerald-500'
              } focus:outline-none focus:ring-2 ${
                isDark ? 'focus:ring-purple-500/20' : 'focus:ring-emerald-500/20'
              }`}
              placeholder={isLogin ? "username or email" : "choose a username"}
              required
            />
          </div>

          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-neutral-300' : 'text-slate-700'
            }`}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`w-full px-4 py-3 rounded-lg border transition-colors ${
                isDark
                  ? 'bg-neutral-900 border-neutral-700 text-white placeholder-neutral-500 focus:border-purple-500'
                  : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 focus:border-emerald-500'
              } focus:outline-none focus:ring-2 ${
                isDark ? 'focus:ring-purple-500/20' : 'focus:ring-emerald-500/20'
              }`}
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className={`p-3 rounded-lg text-sm ${
              isDark ? 'bg-rose-500/20 text-rose-400' : 'bg-rose-50 text-rose-600'
            }`}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
              isDark
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/30'
                : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg shadow-emerald-500/20'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={18} />
                {isLogin ? 'Signing in...' : 'Creating account...'}
              </>
            ) : (
              <>
                {isLogin ? <LogIn size={18} /> : <UserPlus size={18} />}
                {isLogin ? 'Sign In' : 'Sign Up'}
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className={`text-sm ${
              isDark 
                ? 'text-purple-400 hover:text-purple-300' 
                : 'text-emerald-600 hover:text-emerald-700'
            } transition-colors`}
          >
            {isLogin 
              ? "Don't have an account? Sign up" 
              : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}
