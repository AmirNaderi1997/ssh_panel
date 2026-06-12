import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Server,
  Plus,
  Activity,
  Trash2,
  RefreshCw,
  Edit,
  Globe,
  HardDrive,
  Cpu,
  Layers,
  Database,
  MapPin,
  X,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';

export const Servers: React.FC = () => {
  const queryClient = useQueryClient();
  const { addToast } = useNotificationStore();
  const [showAddModal, setShowAddModal] = useState(false);
  
  // Form States
  const [name, setName] = useState('');
  const [hostname, setHostname] = useState('');
  const [ipAddress, setIpAddress] = useState('');
  const [sshPort, setSshPort] = useState(22);
  const [authMethod, setAuthMethod] = useState('PASSWORD');
  const [rootUsername, setRootUsername] = useState('root');
  const [rootPassword, setRootPassword] = useState('');
  const [sshKey, setSshKey] = useState('');
  const [country, setCountry] = useState('US');
  const [provider, setProvider] = useState('');
  const [notes, setNotes] = useState('');

  // Fetch servers list
  const { data: servers = [], isLoading } = useQuery({
    queryKey: ['servers'],
    queryFn: async () => {
      const res = await client.get('/servers');
      return res.data;
    },
  });

  // Add Server mutation
  const addServerMutation = useMutation({
    mutationFn: async (data: any) => {
      return await client.post('/servers', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      addToast('Server successfully registered!', 'success');
      setShowAddModal(false);
      resetForm();
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Failed to add server', 'error');
    },
  });

  // Test Server connection mutation
  const testConnectionMutation = useMutation({
    mutationFn: async (serverId: string) => {
      const res = await client.post(`/servers/${serverId}/test`);
      return res.data;
    },
    onSuccess: (data) => {
      if (data.connected) {
        addToast('Connection test successful! Server is online.', 'success');
      } else {
        addToast('Connection failed! Check credentials and host.', 'error');
      }
      queryClient.invalidateQueries({ queryKey: ['servers'] });
    },
    onError: () => {
      addToast('Connection test error.', 'error');
    },
  });

  // Delete Server mutation
  const deleteServerMutation = useMutation({
    mutationFn: async (serverId: string) => {
      return await client.delete(`/servers/${serverId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      addToast('Server deregistered successfully', 'success');
    },
  });

  const resetForm = () => {
    setName('');
    setHostname('');
    setIpAddress('');
    setSshPort(22);
    setAuthMethod('PASSWORD');
    setRootUsername('root');
    setRootPassword('');
    setSshKey('');
    setCountry('US');
    setProvider('');
    setNotes('');
  };

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !hostname || !ipAddress) {
      addToast('Server name, hostname, and IP are required', 'warning');
      return;
    }

    addServerMutation.mutate({
      name,
      hostname,
      ip_address: ipAddress,
      ssh_port: sshPort,
      auth_method: authMethod,
      root_username: rootUsername,
      root_password: authMethod === 'PASSWORD' ? rootPassword : null,
      ssh_key: authMethod === 'SSH_KEY' ? sshKey : null,
      country,
      provider,
      notes,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Servers</h1>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
            Register and monitor remote Linux nodes for SSH user accounts deployment.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors shadow-lg shadow-primary-600/10"
        >
          <Plus className="w-4 h-4" /> Add Server
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <p className="text-slate-500 dark:text-dark-text-muted text-sm">Loading nodes list...</p>
        </div>
      ) : servers.length === 0 ? (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-12 text-center shadow-sm">
          <Server className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Servers Registered</h3>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-2 max-w-sm mx-auto">
            You need to register at least one Linux node to deploy SSH VPN accounts.
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="mt-6 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-sm font-semibold"
          >
            Register Server
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {servers.map((srv: any) => (
            <div
              key={srv.id}
              className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm flex flex-col justify-between space-y-4 hover:border-slate-300 dark:hover:border-dark-border/80 transition-all duration-200"
            >
              {/* Header */}
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <h3 className="font-bold text-lg text-slate-800 dark:text-white">{srv.name}</h3>
                  <span className="text-xs text-slate-400 font-semibold block">{srv.ip_address}</span>
                </div>
                <div
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                    srv.status === 'ONLINE'
                      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                      : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'
                  }`}
                >
                  {srv.status === 'ONLINE' ? (
                    <>
                      <CheckCircle className="w-3.5 h-3.5" /> Online
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-3.5 h-3.5" /> Offline
                    </>
                  )}
                </div>
              </div>

              {/* Server Details Grid */}
              <div className="grid grid-cols-2 gap-4 text-xs font-semibold py-2 border-y border-slate-100 dark:border-dark-border/50">
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span>Country: {srv.country}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <Layers className="w-4 h-4 text-slate-400" />
                  <span>Port: {srv.ssh_port}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <Database className="w-4 h-4 text-slate-400" />
                  <span>Auth: {srv.auth_method}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <Cpu className="w-4 h-4 text-slate-400" />
                  <span>Provider: {srv.provider || 'VPS'}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => testConnectionMutation.mutate(srv.id)}
                  className="flex-1 py-2 bg-slate-50 hover:bg-slate-100 dark:bg-dark-input dark:hover:bg-dark-input/80 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-colors border border-slate-200/40 dark:border-dark-border/40"
                >
                  <Activity className="w-3.5 h-3.5" /> Ping Test
                </button>
                <button
                  onClick={() => {
                    if (confirm('Are you sure you want to deregister this server?')) {
                      deleteServerMutation.mutate(srv.id);
                    }
                  }}
                  className="px-3 py-2 bg-rose-50 hover:bg-rose-100 dark:bg-rose-500/10 dark:hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 rounded-xl text-xs font-bold transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-2xl bg-white dark:bg-dark-card border border-slate-200 dark:border-dark-border rounded-2xl shadow-xl overflow-hidden max-h-[90vh] flex flex-col">
            <div className="p-6 border-b border-slate-200 dark:border-dark-border/60 flex justify-between items-center shrink-0">
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Register VPS Server</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddSubmit} className="flex-1 p-6 overflow-y-auto space-y-6">
              {/* Core info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Germany Node 1"
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    IP Address / Hostname
                  </label>
                  <input
                    type="text"
                    value={ipAddress}
                    onChange={(e) => {
                      setIpAddress(e.target.value);
                      setHostname(e.target.value);
                    }}
                    placeholder="192.168.1.100"
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
              </div>

              {/* SSH Port & Authentication */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    SSH Port
                  </label>
                  <input
                    type="number"
                    value={sshPort}
                    onChange={(e) => setSshPort(parseInt(e.target.value) || 22)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    SSH Username
                  </label>
                  <input
                    type="text"
                    value={rootUsername}
                    onChange={(e) => setRootUsername(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Auth Method
                  </label>
                  <select
                    value={authMethod}
                    onChange={(e) => setAuthMethod(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  >
                    <option value="PASSWORD">Password</option>
                    <option value="SSH_KEY">SSH Private Key</option>
                  </select>
                </div>
              </div>

              {/* Auth details dynamic */}
              {authMethod === 'PASSWORD' ? (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Root Password
                  </label>
                  <input
                    type="password"
                    value={rootPassword}
                    onChange={(e) => setRootPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    SSH Private Key PEM
                  </label>
                  <textarea
                    value={sshKey}
                    onChange={(e) => setSshKey(e.target.value)}
                    placeholder="-----BEGIN OPENSSH PRIVATE KEY-----"
                    rows={4}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100 font-mono"
                  ></textarea>
                </div>
              )}

              {/* Meta information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Country Code (2 letters)
                  </label>
                  <input
                    type="text"
                    value={country}
                    onChange={(e) => setCountry(e.target.value.toUpperCase())}
                    maxLength={2}
                    placeholder="US"
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                    Hosting Provider
                  </label>
                  <input
                    type="text"
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    placeholder="DigitalOcean"
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-text-muted mb-2">
                  Internal Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Primary tunneling node for vip clients"
                  rows={2}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                ></textarea>
              </div>

              <div className="flex gap-3 justify-end pt-4 shrink-0">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-5 py-2.5 bg-slate-100 hover:bg-slate-250 dark:bg-dark-input text-slate-700 dark:text-slate-300 font-semibold text-sm rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addServerMutation.isPending}
                  className="px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm rounded-xl transition-colors shadow-lg shadow-primary-600/10"
                >
                  {addServerMutation.isPending ? 'Connecting...' : 'Register Node'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default Servers;
