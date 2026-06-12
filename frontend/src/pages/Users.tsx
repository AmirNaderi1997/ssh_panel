import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Users as UsersIcon,
  Plus,
  Trash2,
  Lock,
  Unlock,
  KeyRound,
  Layers,
  Calendar,
  Compass,
  FileText,
  Search,
  CheckCircle,
  X,
  Play,
  UserCheck,
  Ban
} from 'lucide-react';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';

export const Users: React.FC = () => {
  const queryClient = useQueryClient();
  const { addToast } = useNotificationStore();
  
  const [showAddModal, setShowAddModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Single User Form State
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [serverId, setServerId] = useState('');
  const [expiryDays, setExpiryDays] = useState(30);
  const [limitGB, setLimitGB] = useState(100);
  const [connLimit, setConnLimit] = useState(1);
  const [notes, setNotes] = useState('');

  // Bulk User Form State
  const [bulkPrefix, setBulkPrefix] = useState('vpn_user');
  const [bulkCount, setBulkCount] = useState(10);
  const [bulkPassword, setBulkPassword] = useState('');

  // Fetch users
  const { data: users = [], isLoading: usersLoading } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await client.get('/users');
      return res.data;
    },
  });

  // Fetch servers to select from
  const { data: servers = [] } = useQuery({
    queryKey: ['servers'],
    queryFn: async () => {
      const res = await client.get('/servers');
      return res.data;
    },
  });

  // Add User mutation
  const addUserMutation = useMutation({
    mutationFn: async (data: any) => {
      return await client.post('/users', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      addToast('User created successfully!', 'success');
      setShowAddModal(false);
      resetUserForm();
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Failed to create user', 'error');
    },
  });

  // Bulk Create mutation
  const bulkCreateMutation = useMutation({
    mutationFn: async (data: any) => {
      return await client.post('/users/bulk', data);
    },
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      addToast(`Bulk created ${res.data.length} accounts!`, 'success');
      setShowBulkModal(false);
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Failed bulk creation', 'error');
    },
  });

  // Suspend mutation
  const suspendMutation = useMutation({
    mutationFn: async (userId: string) => {
      return await client.post(`/users/${userId}/suspend`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      addToast('User account suspended', 'warning');
    },
  });

  // Activate mutation
  const activateMutation = useMutation({
    mutationFn: async (userId: string) => {
      return await client.post(`/users/${userId}/activate`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      addToast('User account activated', 'success');
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (userId: string) => {
      return await client.delete(`/users/${userId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      addToast('User deleted successfully', 'success');
    },
  });

  const resetUserForm = () => {
    setUsername('');
    setPassword('');
    setExpiryDays(30);
    setLimitGB(100);
    setConnLimit(1);
    setNotes('');
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password || !serverId) {
      addToast('Username, password and server are required', 'warning');
      return;
    }

    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + expiryDays);

    addUserMutation.mutate({
      username,
      password,
      server_id: serverId,
      expiration_date: expiryDate.toISOString(),
      traffic_limit_bytes: limitGB * 1024 * 1024 * 1024,
      connection_limit: connLimit,
      notes,
    });
  };

  const handleBulkSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!bulkPrefix || !serverId) {
      addToast('Prefix and server are required', 'warning');
      return;
    }

    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + expiryDays);

    bulkCreateMutation.mutate({
      prefix: bulkPrefix,
      count: bulkCount,
      password: bulkPassword || null,
      server_id: serverId,
      expiration_date: expiryDate.toISOString(),
      traffic_limit_bytes: limitGB * 1024 * 1024 * 1024,
      connection_limit: connLimit,
      notes: notes || 'Bulk created accounts',
    });
  };

  // Filtered list
  const filteredUsers = users.filter((u: any) =>
    u.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">SSH Accounts</h1>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
            Manage SSH VPN user limits, expiration, and traffic records.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              if (servers.length === 0) {
                addToast('Please register a server first!', 'warning');
                return;
              }
              setServerId(servers[0].id);
              setShowAddModal(true);
            }}
            className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors shadow-lg shadow-primary-600/10"
          >
            <Plus className="w-4 h-4" /> Create User
          </button>
          <button
            onClick={() => {
              if (servers.length === 0) {
                addToast('Please register a server first!', 'warning');
                return;
              }
              setServerId(servers[0].id);
              setShowBulkModal(true);
            }}
            className="flex items-center gap-2 px-4 py-2.5 bg-slate-150 hover:bg-slate-200 dark:bg-dark-input dark:hover:bg-dark-input/80 text-slate-700 dark:text-slate-200 rounded-xl font-semibold text-sm transition-colors border border-slate-200/50 dark:border-dark-border/50"
          >
            Bulk Create
          </button>
        </div>
      </div>

      {/* Filter and search bar */}
      <div className="flex items-center bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-4 shadow-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search SSH accounts..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
          />
        </div>
      </div>

      {/* Users table */}
      {usersLoading ? (
        <div className="flex justify-center py-12">
          <p className="text-slate-500 text-sm">Loading user list...</p>
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-12 text-center shadow-sm">
          <UsersIcon className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Users Found</h3>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-2 max-w-sm mx-auto">
            Create user account to deploy to active remote server VPS.
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-dark-border/40 bg-slate-50/75 dark:bg-dark-input/20 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="px-6 py-4">Username</th>
                  <th className="px-6 py-4">Server Node</th>
                  <th className="px-6 py-4">Expiration</th>
                  <th className="px-6 py-4">Traffic used</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-dark-border/40 text-sm text-slate-700 dark:text-slate-300">
                {filteredUsers.map((u: any) => {
                  const srv = servers.find((s: any) => s.id === u.server_id);
                  const srvName = srv ? srv.name : 'Unknown Node';
                  
                  const isExpired = new Date(u.expiration_date).getTime() < Date.now();
                  const statusColors = {
                    ACTIVE: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
                    SUSPENDED: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
                    EXPIRED: 'bg-rose-500/10 text-rose-600 dark:text-rose-400',
                    DISABLED: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
                  }[u.status as 'ACTIVE' | 'SUSPENDED' | 'EXPIRED' | 'DISABLED'] || 'bg-slate-500/10 text-slate-600';

                  const usedGB = (u.traffic_used_bytes / (1024 * 1024 * 1024)).toFixed(2);
                  const limitGBVal = u.traffic_limit_bytes > 0 
                    ? `${(u.traffic_limit_bytes / (1024 * 1024 * 1024)).toFixed(0)} GB`
                    : 'Unlimited';

                  return (
                    <tr key={u.id} className="hover:bg-slate-50/50 dark:hover:bg-dark-input/5">
                      <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">
                        {u.username}
                      </td>
                      <td className="px-6 py-4 font-medium">{srvName}</td>
                      <td className="px-6 py-4">
                        {new Date(u.expiration_date).toLocaleDateString()}
                        {isExpired && (
                          <span className="ml-1.5 px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-500 text-[10px] font-bold">
                            Expired
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {usedGB} GB / <span className="text-slate-400">{limitGBVal}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${statusColors}`}>
                          {u.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right space-x-1">
                        {u.status === 'SUSPENDED' ? (
                          <button
                            onClick={() => activateMutation.mutate(u.id)}
                            className="p-1.5 rounded-lg text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 transition-colors"
                            title="Activate Account"
                          >
                            <Unlock className="w-4 h-4" />
                          </button>
                        ) : (
                          <button
                            onClick={() => suspendMutation.mutate(u.id)}
                            className="p-1.5 rounded-lg text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-500/10 transition-colors"
                            title="Suspend Account"
                            disabled={u.status === 'EXPIRED'}
                          >
                            <Lock className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => {
                            if (confirm('Delete this account permanently?')) {
                              deleteMutation.mutate(u.id);
                            }
                          }}
                          className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors"
                          title="Delete Account"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
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
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Create SSH VPN Account</h2>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input p-1 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="john_vpn"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="securevpnpassword"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                  Assign Server Node
                </label>
                <select
                  value={serverId}
                  onChange={(e) => setServerId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                >
                  {servers.map((s: any) => (
                    <option key={s.id} value={s.id}>{s.name} ({s.ip_address})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Duration (Days)
                  </label>
                  <input
                    type="number"
                    value={expiryDays}
                    onChange={(e) => setExpiryDays(parseInt(e.target.value) || 30)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Bandwidth Quota (GB)
                  </label>
                  <input
                    type="number"
                    value={limitGB}
                    onChange={(e) => setLimitGB(parseInt(e.target.value) || 0)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                  Simultaneous Connections Limit
                </label>
                <input
                  type="number"
                  value={connLimit}
                  onChange={(e) => setConnLimit(parseInt(e.target.value) || 1)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
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
                  disabled={addUserMutation.isPending}
                  className="px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm rounded-xl transition-colors shadow-lg shadow-primary-600/10"
                >
                  {addUserMutation.isPending ? 'Deploying...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk Create Modal */}
      {showBulkModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white dark:bg-dark-card border border-slate-200 dark:border-dark-border rounded-2xl shadow-xl overflow-hidden">
            <div className="p-6 border-b border-slate-200 dark:border-dark-border/60 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Bulk Create Accounts</h2>
              <button onClick={() => setShowBulkModal(false)} className="text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input p-1 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleBulkSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                  Username Prefix
                </label>
                <input
                  type="text"
                  value={bulkPrefix}
                  onChange={(e) => setBulkPrefix(e.target.value)}
                  placeholder="vpn_user"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Accounts Count
                  </label>
                  <input
                    type="number"
                    value={bulkCount}
                    onChange={(e) => setBulkCount(parseInt(e.target.value) || 10)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Common Password (Optional)
                  </label>
                  <input
                    type="text"
                    value={bulkPassword}
                    onChange={(e) => setBulkPassword(e.target.value)}
                    placeholder="Auto generated if empty"
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                  Server Node
                </label>
                <select
                  value={serverId}
                  onChange={(e) => setServerId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                >
                  {servers.map((s: any) => (
                    <option key={s.id} value={s.id}>{s.name} ({s.ip_address})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Duration (Days)
                  </label>
                  <input
                    type="number"
                    value={expiryDays}
                    onChange={(e) => setExpiryDays(parseInt(e.target.value) || 30)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Bandwidth Quota (GB)
                  </label>
                  <input
                    type="number"
                    value={limitGB}
                    onChange={(e) => setLimitGB(parseInt(e.target.value) || 0)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
              </div>

              <div className="flex gap-3 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowBulkModal(false)}
                  className="px-5 py-2.5 bg-slate-100 dark:bg-dark-input hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-semibold text-sm rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={bulkCreateMutation.isPending}
                  className="px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm rounded-xl transition-colors shadow-lg shadow-primary-600/10"
                >
                  {bulkCreateMutation.isPending ? 'Generating...' : 'Start Creation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default Users;
