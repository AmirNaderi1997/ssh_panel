import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
  LayoutDashboard,
  Server,
  Users,
  Activity,
  Globe,
  ShieldCheck,
  Award,
  Database,
  Settings,
  LogOut,
  ShieldAlert,
  UserCheck,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const { profile, logout } = useAuthStore();

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard className="w-5 h-5" /> },
    { name: 'Servers', path: '/servers', icon: <Server className="w-5 h-5" /> },
    { name: 'Users', path: '/users', icon: <Users className="w-5 h-5" /> },
    { name: 'Online Users', path: '/online', icon: <Activity className="w-5 h-5" /> },
    { name: 'Domains', path: '/domains', icon: <Globe className="w-5 h-5" /> },
    { name: 'SSL Certificates', path: '/ssl', icon: <ShieldCheck className="w-5 h-5" /> },
    { name: 'Resellers', path: '/resellers', icon: <Award className="w-5 h-5" /> },
    { name: 'Admins', path: '/admins', icon: <UserCheck className="w-5 h-5" /> },
    { name: 'Backups', path: '/backups', icon: <Database className="w-5 h-5" /> },
    { name: 'Audit Logs', path: '/audit-logs', icon: <ShieldAlert className="w-5 h-5" /> },
    { name: 'Settings', path: '/settings', icon: <Settings className="w-5 h-5" /> },
  ];


  return (
    <aside
      className={`fixed top-0 left-0 h-screen bg-white dark:bg-dark-card border-r border-slate-200/60 dark:border-dark-border/60 transition-all duration-300 flex flex-col z-20 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand logo */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-200/60 dark:border-dark-border/60">
        <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center text-white font-bold text-lg shrink-0 shadow-md shadow-primary-600/30">
          S
        </div>
        {!collapsed && (
          <span className="font-extrabold text-slate-800 dark:text-white tracking-wider text-base">
            SSH MANAGER
          </span>
        )}
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-4 py-6 overflow-y-auto space-y-1">
        {menuItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 font-medium text-sm group ${
                isActive
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input hover:text-slate-900 dark:hover:text-white'
              }`
            }
          >
            <span className="shrink-0">{item.icon}</span>
            {!collapsed && <span className="truncate">{item.name}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User profile / Logout */}
      <div className="p-4 border-t border-slate-200/60 dark:border-dark-border/60 bg-slate-50/40 dark:bg-dark-input/10">
        {!collapsed && profile && (
          <div className="mb-4 px-2">
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
              {profile.username}
            </p>
            <p className="text-xs text-slate-500 dark:text-dark-text-muted truncate">
              {profile.role}
            </p>
          </div>
        )}
        <button
          onClick={logout}
          className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 font-medium text-sm transition-all duration-200`}
        >
          <LogOut className="w-5 h-5 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
};
