import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldAlert, Terminal, Clock, User } from 'lucide-react';
import client from '../api/client';

export const AuditLogs: React.FC = () => {
  // Fetch audit logs list
  const { data: logs = [], isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async () => {
      const res = await client.get('/admin/audit-logs');
      return res.data;
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Security Audit Logs</h1>
        <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
          Historical log records of administrative actions and config mutations.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <p className="text-slate-500 text-sm">Loading audit logs...</p>
        </div>
      ) : logs.length === 0 ? (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-12 text-center shadow-sm">
          <ShieldAlert className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Logs Found</h3>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-2 max-w-sm mx-auto">
            Audit logs will record database modifications and administrator logins.
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-dark-border/40 bg-slate-50/75 dark:bg-dark-input/20 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="px-6 py-4">Admin ID</th>
                  <th className="px-6 py-4">Action</th>
                  <th className="px-6 py-4">Resource</th>
                  <th className="px-6 py-4">IP Address</th>
                  <th className="px-6 py-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-dark-border/40 text-sm text-slate-700 dark:text-slate-300">
                {logs.map((log: any) => (
                  <tr key={log.id} className="hover:bg-slate-50/50 dark:hover:bg-dark-input/5">
                    <td className="px-6 py-4 font-semibold font-mono text-xs text-slate-500">
                      {log.admin_id ? log.admin_id.substring(0, 8) : 'SYSTEM'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">
                      {log.action}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded-lg text-xs bg-slate-100 dark:bg-dark-input text-slate-600 dark:text-slate-450">
                        {log.resource_type} ({log.resource_id ? log.resource_id.substring(0, 8) : 'N/A'})
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{log.ip_address || '127.0.0.1'}</td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
export default AuditLogs;
