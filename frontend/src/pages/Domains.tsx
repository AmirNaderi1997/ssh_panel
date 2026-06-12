import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Globe,
  Plus,
  Trash2,
  CheckCircle,
  XCircle,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Loader,
  Server,
  Zap,
  Info,
  X
} from 'lucide-react';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';

export const Domains: React.FC = () => {
  const queryClient = useQueryClient();
  const { addToast } = useNotificationStore();
  const [showWizard, setShowWizard] = useState(false);
  const [wizardStep, setWizardStep] = useState(1);
  
  // Wizard States
  const [domainName, setDomainName] = useState('');
  const [domainType, setDomainType] = useState('ROOT');
  const [serverId, setServerId] = useState('');
  const [selectedDomainId, setSelectedDomainId] = useState<string | null>(null);
  
  // Queries
  const { data: domains = [], isLoading: domainsLoading } = useQuery({
    queryKey: ['domains'],
    queryFn: async () => {
      const res = await client.get('/domains');
      return res.data;
    },
  });

  const { data: servers = [] } = useQuery({
    queryKey: ['servers'],
    queryFn: async () => {
      const res = await client.get('/servers');
      return res.data;
    },
  });

  // Mutations
  const registerDomainMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await client.post('/domains', data);
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      setSelectedDomainId(data.id);
      addToast('Domain registered successfully in database', 'success');
      setWizardStep(2); // Move to DNS check step
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Registration failed', 'error');
    },
  });

  const verifyDNSMutation = useMutation({
    mutationFn: async (domainId: string) => {
      const res = await client.post(`/domains/${domainId}/verify-dns`);
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      if (data.verified) {
        addToast('DNS configuration verified!', 'success');
        setWizardStep(3); // Move to SSL issuance step
      } else {
        addToast('DNS check failed. Please ensure A record points to server IP.', 'error');
      }
    },
  });

  const issueSSLMutation = useMutation({
    mutationFn: async (domainId: string) => {
      const res = await client.post(`/ssl/issue/${domainId}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      addToast('SSL Certificate successfully deployed to Nginx!', 'success');
      setWizardStep(4); // Completed step
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'SSL issuance failed', 'error');
    },
  });

  const deleteDomainMutation = useMutation({
    mutationFn: async (domainId: string) => {
      return await client.delete(`/domains/${domainId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      addToast('Domain deregistered successfully', 'success');
    },
  });

  const startWizard = () => {
    setDomainName('');
    setDomainType('ROOT');
    if (servers.length > 0) {
      setServerId(servers[0].id);
    }
    setSelectedDomainId(null);
    setWizardStep(1);
    setShowWizard(true);
  };

  const closeWizard = () => {
    setShowWizard(false);
    setWizardStep(1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Domain & SSL Management</h1>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
            Map domains to nodes and automate Let's Encrypt ACME SSL certificate renewals.
          </p>
        </div>
        <button
          onClick={startWizard}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors shadow-lg shadow-primary-600/10"
        >
          <Plus className="w-4 h-4" /> SSL Domain Wizard
        </button>
      </div>

      {/* Domains Table */}
      {domainsLoading ? (
        <div className="flex justify-center py-12">
          <p className="text-slate-500 text-sm">Loading domains list...</p>
        </div>
      ) : domains.length === 0 ? (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-12 text-center shadow-sm">
          <Globe className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Domains Mapped</h3>
          <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-2 max-w-sm mx-auto">
            Link domain names to your VPN server nodes to host secure SSL panel logins.
          </p>
          <button
            onClick={startWizard}
            className="mt-6 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-sm font-semibold"
          >
            Launch Wizard
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-dark-border/40 bg-slate-50/75 dark:bg-dark-input/20 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="px-6 py-4">Domain</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Linked Node</th>
                  <th className="px-6 py-4">DNS Status</th>
                  <th className="px-6 py-4">SSL Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-dark-border/40 text-sm text-slate-700 dark:text-slate-300">
                {domains.map((dom: any) => {
                  const srv = servers.find((s: any) => s.id === dom.server_id);
                  const srvName = srv ? srv.name : 'Unknown Node';

                  return (
                    <tr key={dom.id} className="hover:bg-slate-50/50 dark:hover:bg-dark-input/5">
                      <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">
                        {dom.domain}
                      </td>
                      <td className="px-6 py-4">{dom.type}</td>
                      <td className="px-6 py-4">{srvName}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                            dom.dns_status === 'VERIFIED'
                              ? 'bg-emerald-500/10 text-emerald-600'
                              : 'bg-amber-500/10 text-amber-600'
                          }`}
                        >
                          {dom.dns_status === 'VERIFIED' ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                          {dom.dns_status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                            dom.ssl_status === 'ACTIVE'
                              ? 'bg-emerald-500/10 text-emerald-600'
                              : 'bg-rose-500/10 text-rose-600'
                          }`}
                        >
                          {dom.ssl_status === 'ACTIVE' ? <ShieldCheck className="w-3.5 h-3.5" /> : <ShieldAlert className="w-3.5 h-3.5" />}
                          {dom.ssl_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => {
                            if (confirm('Deregister domain?')) {
                              deleteDomainMutation.mutate(dom.id);
                            }
                          }}
                          className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors"
                          title="Deregister"
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

      {/* SSL Wizard Modal */}
      {showWizard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white dark:bg-dark-card border border-slate-200 dark:border-dark-border rounded-2xl shadow-xl overflow-hidden">
            <div className="p-6 border-b border-slate-200 dark:border-dark-border/60 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Domain SSL Setup Wizard</h2>
              <button onClick={closeWizard} className="text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-input p-1 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Steps indicator */}
            <div className="flex border-b border-slate-150 dark:border-dark-border/40 bg-slate-50/50 dark:bg-dark-input/10 py-3 px-6 text-xs font-bold text-slate-400 uppercase justify-around">
              <span className={wizardStep === 1 ? 'text-primary-600' : ''}>1. Link</span>
              <span className={wizardStep === 2 ? 'text-primary-600' : ''}>2. DNS</span>
              <span className={wizardStep === 3 ? 'text-primary-600' : ''}>3. Issue</span>
              <span className={wizardStep === 4 ? 'text-primary-600' : ''}>4. Complete</span>
            </div>

            <div className="p-6">
              {/* Step 1: Form */}
              {wizardStep === 1 && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                      Domain Name
                    </label>
                    <input
                      type="text"
                      value={domainName}
                      onChange={(e) => setDomainName(e.target.value)}
                      placeholder="vpn.mydomain.com"
                      className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                      Target Node
                    </label>
                    <select
                      value={serverId}
                      onChange={(e) => setServerId(e.target.value)}
                      className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100"
                    >
                      {servers.length === 0 && <option>No servers available</option>}
                      {servers.map((s: any) => (
                        <option key={s.id} value={s.id}>{s.name} ({s.ip_address})</option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={() => {
                      if (!domainName || !serverId) {
                        addToast('Domain and server selection required', 'warning');
                        return;
                      }
                      registerDomainMutation.mutate({
                        domain: domainName,
                        type: domainType,
                        server_id: serverId,
                      });
                    }}
                    disabled={registerDomainMutation.isPending}
                    className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2"
                  >
                    {registerDomainMutation.isPending ? <Loader className="w-4 h-4 animate-spin" /> : 'Register & Next'}
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* Step 2: DNS verification */}
              {wizardStep === 2 && selectedDomainId && (
                <div className="space-y-4 text-center">
                  <Globe className="w-12 h-12 text-slate-400 mx-auto" />
                  <h3 className="font-bold text-slate-800 dark:text-white">Verify DNS Record Propagation</h3>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto">
                    Ensure your domain's A-Record points to the selected Server node's IP before verifying.
                  </p>
                  
                  <div className="bg-slate-50 dark:bg-dark-input/50 p-4 rounded-xl border border-slate-200/50 dark:border-dark-border/50 text-left space-y-1.5 text-xs font-semibold">
                    <p className="text-slate-500">Target IP Address:</p>
                    <p className="text-slate-800 dark:text-slate-200 font-mono text-sm">
                      {servers.find((s: any) => s.id === serverId)?.ip_address}
                    </p>
                  </div>

                  <button
                    onClick={() => verifyDNSMutation.mutate(selectedDomainId)}
                    disabled={verifyDNSMutation.isPending}
                    className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2"
                  >
                    {verifyDNSMutation.isPending ? <Loader className="w-4 h-4 animate-spin" /> : 'Check DNS Routing'}
                  </button>
                </div>
              )}

              {/* Step 3: SSL Issuance */}
              {wizardStep === 3 && selectedDomainId && (
                <div className="space-y-4 text-center">
                  <ShieldCheck className="w-12 h-12 text-emerald-500 mx-auto" />
                  <h3 className="font-bold text-slate-800 dark:text-white text-lg">DNS Verified!</h3>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto">
                    Your DNS routing is correct. We can now generate the Let's Encrypt certificate and deploy to Nginx.
                  </p>

                  <button
                    onClick={() => issueSSLMutation.mutate(selectedDomainId)}
                    disabled={issueSSLMutation.isPending}
                    className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2 shadow-lg shadow-primary-600/10"
                  >
                    {issueSSLMutation.isPending ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" /> Requesting Certificate...
                      </>
                    ) : (
                      'Issue & Deploy SSL'
                    )}
                  </button>
                </div>
              )}

              {/* Step 4: Finished */}
              {wizardStep === 4 && (
                <div className="space-y-4 text-center py-4">
                  <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto text-2xl font-bold">
                    ✓
                  </div>
                  <h3 className="font-bold text-slate-800 dark:text-white text-lg">Setup Completed!</h3>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto">
                    Domain SSL certificates are successfully issued, deployed, and Nginx reverse proxy loaded.
                  </p>
                  
                  <button
                    onClick={closeWizard}
                    className="w-full py-3 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-semibold text-sm transition-colors"
                  >
                    Done
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default Domains;
