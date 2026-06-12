import React from 'react';
import { useNotificationStore } from '../../store/notificationStore';
import { AlertCircle, CheckCircle, Info, X, AlertTriangle } from 'lucide-react';

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useNotificationStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full pointer-events-none">
      {toasts.map((toast) => {
        const icon = {
          success: <CheckCircle className="w-5 h-5 text-emerald-500" />,
          error: <AlertCircle className="w-5 h-5 text-rose-500" />,
          info: <Info className="w-5 h-5 text-blue-500" />,
          warning: <AlertTriangle className="w-5 h-5 text-amber-500" />,
        }[toast.type];

        const colors = {
          success: 'border-emerald-500/20 bg-white dark:bg-dark-card border border-emerald-500/30',
          error: 'border-rose-500/20 bg-white dark:bg-dark-card border border-rose-500/30',
          info: 'border-blue-500/20 bg-white dark:bg-dark-card border border-blue-500/30',
          warning: 'border-amber-500/20 bg-white dark:bg-dark-card border border-amber-500/30',
        }[toast.type];

        return (
          <div
            key={toast.id}
            className={`flex items-center gap-3 p-4 rounded-xl shadow-lg border pointer-events-auto transition-all duration-300 transform translate-y-0 ${colors}`}
          >
            {icon}
            <p className="flex-1 text-sm font-medium text-slate-800 dark:text-slate-200">
              {toast.message}
            </p>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-0.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
