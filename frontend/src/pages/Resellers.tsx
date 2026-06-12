import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Award, Plus, Trash2, ArrowUpRight, DollarSign, UserCheck, ShieldAlert, X } from 'lucide-react';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';

export const Resellers: React.FC = () => {
  const queryClient = useQueryClient();
  const { addToast } = useNotificationStore();
  const [showAllocateModal, setShowAllocateModal] = useState(false);
  const [selectedResellerId, setSelectedResellerId] = useState<string | null>(null);
  
  // Allocate Form
  const [amount, setAmount] = useState(100);
  const [desc, setDesc] = useState('Top up reseller balance');

  // Fetch resellers
  const { data: resellers = [], isLoading } = useQuery({
    queryKey: ['resellers'],
    queryFn: async () => {
      const res = await client.get('/resellers');
      return res.data;
    },
  });

  // Allocate mutation
  const allocateMutation = useMutation({
    mutationFn: async ({ id, amt, description }: { id: string; amt: number; description: string }) => {
      const res = await client.post(`/resellers/${id}/allocate?amount=${amt}&description=${description}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resellers'] });
      addToast('Credits successfully allocated!', 'success');
      setShowAllocateModal(false);
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Allocation failed', 'error');
    },
  });

  const handleAllocateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedResellerId || amount <= 0) return;
    allocateMutation.mutate({ id: selectedResellerId, amt: amount, description: desc });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Resellers</h1>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
            Manage reseller profiles, allocate credits, and set user limits.
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <p className="text-slate-500 text-sm">Loading reseller profiles...</p>
        </div>
      ) : resellers.length === 0 ? (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-12 text-center shadow-sm">
          <Award className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Resellers Profiled</h3>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-2 max-w-sm mx-auto">
            Resellers can be added by creating admin users and mapping profiles to them.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resellers.map((r: any) => (
            <div
              key={r.id}
              className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm flex flex-col justify-between space-y-4 hover:border-slate-300 dark:hover:border-dark-border/80 transition-all duration-200"
            >
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <h3 className="font-bold text-lg text-slate-800 dark:text-white">Reseller Node</h3>
                  <span className="text-xs text-slate-400 font-semibold block">ID: {r.id.substring(0, 8)}</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-600">
                  {r.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs font-semibold py-2 border-y border-slate-100 dark:border-dark-border/50">
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <DollarSign className="w-4 h-4 text-slate-400" />
                  <span>Credits: {r.credits}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <UserCheck className="w-4 h-4 text-slate-400" />
                  <span>Max Users: {r.max_users}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setSelectedResellerId(r.id);
                    setShowAllocateModal(true);
                  }}
                  className="flex-1 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
                >
                  <ArrowUpRight className="w-4 h-4" /> Top Up Credits
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Top Up Modal */}
      {showAllocateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white dark:bg-dark-card border border-slate-200 dark:border-dark-border rounded-2xl shadow-xl overflow-hidden">
            <div className="p-6 border-b border-slate-200 dark:border-dark-border/60 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Allocate Reseller Credits</h2>
              <button
                onClick={() => setShowAllocateModal(false)}
                className="text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAllocateSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Credits Amount
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(parseInt(e.target.value) || 0)}
                  placeholder="100"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Remarks / Description
                </label>
                <input
                  type="text"
                  value={desc}
                  onChange={(e) => setDesc(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                />
              </div>

              <div className="flex gap-3 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowAllocateModal(false)}
                  className="px-5 py-2.5 bg-slate-100 dark:bg-dark-input hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-semibold text-sm rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={allocateMutation.isPending}
                  className="px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm rounded-xl transition-colors shadow-lg shadow-primary-600/10"
                >
                  {allocateMutation.isPending ? 'Allocating...' : 'Allocate Credits'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default Resellers;
