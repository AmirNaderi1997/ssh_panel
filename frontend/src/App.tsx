import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './store/authStore';
import { useThemeStore } from './store/themeStore';
import { MainLayout } from './components/layout/MainLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Servers } from './pages/Servers';
import { Users } from './pages/Users';
import { OnlineUsers } from './pages/OnlineUsers';
import { Domains } from './pages/Domains';
import { Resellers } from './pages/Resellers';
import { Backups } from './pages/Backups';
import { AdminManagement } from './pages/AdminManagement';
import { AuditLogs } from './pages/AuditLogs';
import { Settings } from './pages/Settings';
import { ToastContainer } from './components/ui/Toast';

// Initialize query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Guard components
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

// Placeholder components for future pages
const PlaceholderPage: React.FC<{ name: string }> = ({ name }) => (
  <div className="space-y-4">
    <h1 className="text-2xl font-bold text-slate-800 dark:text-white">{name}</h1>
    <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-8 shadow-sm flex items-center justify-center min-h-[300px]">
      <p className="text-slate-500 dark:text-dark-text-muted">
        {name} management interface will be implemented in subsequent phases.
      </p>
    </div>
  </div>
);

export const App: React.FC = () => {
  const { initTheme } = useThemeStore();
  const { fetchProfile, isAuthenticated } = useAuthStore();

  useEffect(() => {
    initTheme();
    if (isAuthenticated) {
      fetchProfile();
    }
  }, [initTheme, fetchProfile, isAuthenticated]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="/servers" element={<Servers />} />
              <Route path="/users" element={<Users />} />
              <Route path="/online" element={<OnlineUsers />} />
              <Route path="/domains" element={<Domains />} />
              <Route path="/ssl" element={<Domains />} />
              <Route path="/resellers" element={<Resellers />} />
              <Route path="/backups" element={<Backups />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/admins" element={<AdminManagement />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </QueryClientProvider>
  );
};

export default App;
