import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, KeyRound, ShieldCheck, User, ShieldAlert, X } from 'lucide-react';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';

export const AdminManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const { addToast } = useNotificationStore();
  const [showAddModal, setShowAddModal] = useState(false);
  
  // Form States
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('ADMIN');

  // Fetch admin profiles
  const { data: admins = [], isLoading } = useQuery({
    queryKey: ['admins'],
    queryFn: async () => {
      const res = await client.get('/admin/admins');
      return res.data;
    },
  });

  // Create admin profile mutation
  const addAdminMutation = useMutation({
    mutationFn: async (data: any) => {
      return await client.post('/admin/admins', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admins'] });
      addToast('Administrator registered successfully!', 'success');
      setShowAddModal(false);
      resetForm();
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Failed to add admin', 'error');
    },
  });

  // Delete admin profile mutation
  const deleteAdminMutation = useMutation({
    mutationFn: async (id: string) => {
      return await client.delete(`/admin/admins/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admins'] });
      addToast('Administrator profile removed', 'success');
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Deregistration failed', 'error');
    },
  });

  const resetForm = () => {
    setUsername('');
    setEmail('');
    setPassword('');
    setRole('ADMIN');
  };

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !email || !password) {
      addToast('All fields are required', 'warning');
      return;
    }
    addAdminMutation.mutate({
      username,
      email,
      password,
      role,
      permissions: [],
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Admin Accounts</h1>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
            Manage administrative logins and assign roles.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors shadow-lg shadow-primary-600/10"
        >
          <Plus className="w-4 h-4" /> Create Admin
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <p className="text-slate-500 text-sm">Loading admin log list...</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-dark-border/40 bg-slate-50/75 dark:bg-dark-input/20 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="px-6 py-4">Username</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4">Role</th>
                  <th className="px-6 py-4">2FA Status</th>
                  <th className="px-6 py-4">Last Login</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-dark-border/40 text-sm text-slate-700 dark:text-slate-300">
                {admins.map((a: any) => (
                  <tr key={a.id} className="hover:bg-slate-50/50 dark:hover:bg-dark-input/5">
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">
                      {a.username}
                    </td>
                    <td className="px-6 py-4">{a.email}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded-lg text-xs font-bold bg-slate-100 dark:bg-dark-input text-slate-700 dark:text-slate-300">
                        {a.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                          a.totp_enabled
                            ? 'bg-emerald-500/10 text-emerald-600'
                            : 'bg-slate-500/10 text-slate-600'
                        }`}
                      >
                        {a.totp_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {a.last_login ? new Date(a.last_login).toLocaleString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => {
                          if (confirm('Deregister admin?')) {
                            deleteAdminMutation.mutate(a.id);
                          }
                        }}
                        className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors"
                        title="Deregister"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white dark:bg-dark-card border border-slate-200 dark:border-dark-border rounded-2xl shadow-xl overflow-hidden">
            <div className="p-6 border-b border-slate-200 dark:border-dark-border/60 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Create Admin Login</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="manager_agent"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="agent@example.com"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Role
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                >
                  <option value="SUPER_ADMIN">Super Admin (All permissions)</option>
                  <option value="ADMIN">Admin (Default operational permissions)</option>
                  <option value="SUPPORT">Support (Read-only / Users management)</option>
                  <option value="RESELLER">Reseller</option>
                </select>
              </div>

              <div className="flex gap-3 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-5 py-2.5 bg-slate-100 dark:bg-dark-input hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-semibold text-sm rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addAdminMutation.isPending}
                  className="px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm rounded-xl transition-colors shadow-lg shadow-primary-600/10"
                >
                  {addAdminMutation.isPending ? 'Saving...' : 'Register Admin'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default AdminManagement;
