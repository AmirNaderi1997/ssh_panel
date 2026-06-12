import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Database, Plus, Trash2, RefreshCw, AlertTriangle, Play, Download } from 'lucide-react';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';

export const Backups: React.FC = () => {
  const queryClient = useQueryClient();
  const { addToast } = useNotificationStore();

  // Fetch backups list
  const { data: backups = [], isLoading } = useQuery({
    queryKey: ['backups'],
    queryFn: async () => {
      const res = await client.get('/backups');
      return res.data;
    },
  });

  // Create manual backup mutation
  const createBackupMutation = useMutation({
    mutationFn: async () => {
      return await client.post('/backups?notes=Manual panel database backup');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backups'] });
      addToast('Backup created successfully!', 'success');
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Failed to create backup', 'error');
    },
  });

  // Restore database mutation
  const restoreBackupMutation = useMutation({
    mutationFn: async (backupId: string) => {
      return await client.post(`/backups/${backupId}/restore`);
    },
    onSuccess: () => {
      addToast('Database successfully restored! Refreshing page...', 'success');
      setTimeout(() => window.location.reload(), 1500);
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Restoration failed', 'error');
    },
  });

  // Delete backup mutation
  const deleteBackupMutation = useMutation({
    mutationFn: async (backupId: string) => {
      return await client.delete(`/backups/${backupId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backups'] });
      addToast('Backup deleted successfully', 'success');
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Database Backups</h1>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
            Generate and restore compressed configuration dumps.
          </p>
        </div>
        <button
          onClick={() => createBackupMutation.mutate()}
          disabled={createBackupMutation.isPending}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors shadow-lg shadow-primary-600/10"
        >
          {createBackupMutation.isPending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          Generate Backup
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <p className="text-slate-500 text-sm">Loading backup archives...</p>
        </div>
      ) : backups.length === 0 ? (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-12 text-center shadow-sm">
          <Database className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Backups Found</h3>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-2 max-w-sm mx-auto">
            Generate your first backup to prevent configuration data loss.
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-dark-border/40 bg-slate-50/75 dark:bg-dark-input/20 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="px-6 py-4">Filename</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Size</th>
                  <th className="px-6 py-4">Created At</th>
                  <th className="px-6 py-4">Notes</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-dark-border/40 text-sm text-slate-700 dark:text-slate-300">
                {backups.map((b: any) => {
                  const sizeKB = (b.file_size / 1024).toFixed(1);
                  return (
                    <tr key={b.id} className="hover:bg-slate-50/50 dark:hover:bg-dark-input/5">
                      <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white font-mono text-xs">
                        {b.filename}
                      </td>
                      <td className="px-6 py-4">{b.type}</td>
                      <td className="px-6 py-4">{sizeKB} KB</td>
                      <td className="px-6 py-4">{new Date(b.created_at).toLocaleString()}</td>
                      <td className="px-6 py-4 max-w-xs truncate text-slate-500">{b.notes || 'N/A'}</td>
                      <td className="px-6 py-4 text-right space-x-1">
                        <button
                          onClick={() => {
                            if (confirm('RESTORE DATABASE? This will overwrite all current data. This action is destructive!')) {
                              restoreBackupMutation.mutate(b.id);
                            }
                          }}
                          className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 transition-colors"
                          title="Restore database"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm('Delete backup file from disk?')) {
                              deleteBackupMutation.mutate(b.id);
                            }
                          }}
                          className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors"
                          title="Delete archive"
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
    </div>
  );
};
export default Backups;
