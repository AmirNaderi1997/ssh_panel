import React from 'react';
import { Menu, Moon, Sun, Bell, User } from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';
import { useAuthStore } from '../../store/authStore';

interface HeaderProps {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (val: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  sidebarCollapsed,
  setSidebarCollapsed,
}) => {
  const { darkMode, toggleTheme } = useThemeStore();
  const { profile } = useAuthStore();

  return (
    <header className="fixed top-0 right-0 h-16 bg-white/80 dark:bg-dark-card/80 backdrop-blur-md border-b border-slate-200/60 dark:border-dark-border/60 flex items-center justify-between px-6 z-10 transition-all duration-300 left-0 md:left-auto"
      style={{ left: sidebarCollapsed ? '80px' : '264px' }}
    >
      {/* Sidebar toggle */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input transition-colors duration-200"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Right side controls */}
      <div className="flex items-center gap-4">
        {/* Dark mode toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input transition-colors duration-200"
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* Notifications bell (decorative for now) */}
        <button className="p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input transition-colors duration-200 relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary-500"></span>
        </button>

        {/* Profile info */}
        <div className="flex items-center gap-3 pl-2 border-l border-slate-200/60 dark:border-dark-border/60">
          <div className="w-9 h-9 rounded-xl bg-slate-100 dark:bg-dark-input flex items-center justify-center text-slate-700 dark:text-slate-300">
            <User className="w-5 h-5" />
          </div>
          {profile && (
            <div className="hidden sm:block text-left">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-tight">
                {profile.username}
              </p>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                {profile.role}
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
