import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { KeyRound, User, ShieldCheck } from 'lucide-react';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [show2FA, setShow2FA] = useState(false);

  const { login, error, isLoading, isAuthenticated } = useAuthStore();
  const { addToast } = useNotificationStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      addToast('Please enter username and password', 'error');
      return;
    }

    const success = await login(username, password, totpCode);
    if (success) {
      addToast('Welcome back! Login successful.', 'success');
      navigate('/');
    } else {
      // If error indicates 2FA is required, show the input
      if (error && error.toLowerCase().includes('2fa code required')) {
        setShow2FA(true);
        addToast('Please enter your 2FA verification code', 'warning');
      } else {
        addToast(error || 'Invalid credentials', 'error');
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-dark-bg p-6 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-500/10 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-primary-600/10 blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl shadow-xl p-8 relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-primary-600 flex items-center justify-center text-white font-bold text-2xl mb-4 shadow-lg shadow-primary-600/20">
            S
          </div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
            Welcome to SSH Manager
          </h1>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1 text-center">
            Sign in to manage remote VPN nodes and client accounts
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
              Username
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <User className="w-5 h-5" />
              </span>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
                placeholder="admin"
                className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 dark:focus:border-primary-500 text-sm dark:text-slate-100"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <KeyRound className="w-5 h-5" />
              </span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                placeholder="••••••••••••"
                className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 dark:focus:border-primary-500 text-sm dark:text-slate-100"
              />
            </div>
          </div>

          {show2FA && (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                2FA Authenticator Code
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <ShieldCheck className="w-5 h-5" />
                </span>
                <input
                  type="text"
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value)}
                  disabled={isLoading}
                  placeholder="000000"
                  maxLength={6}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 dark:focus:border-primary-500 text-sm dark:text-slate-100 tracking-[0.25em] font-semibold text-center"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors duration-200 shadow-lg shadow-primary-600/10 flex items-center justify-center gap-2"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};
