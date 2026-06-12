import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings as SettingsIcon, ShieldCheck, ToggleLeft, ToggleRight, Loader, Lock, Key } from 'lucide-react';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';
import { useAuthStore } from '../store/authStore';

export const Settings: React.FC = () => {
  const queryClient = useQueryClient();
  const { addToast } = useNotificationStore();
  const { profile, fetchProfile } = useAuthStore();
  
  // 2FA Setup Flow State
  const [show2FAFlow, setShow2FAFlow] = useState(false);
  const [totpSecret, setTotpSecret] = useState('');
  const [qrCodeUri, setQrCodeUri] = useState('');
  const [code, setCode] = useState('');

  // Setup 2FA Mutation
  const setup2FAMutation = useMutation({
    mutationFn: async () => {
      const res = await client.post('/auth/2fa/setup');
      return res.data;
    },
    onSuccess: (data) => {
      setTotpSecret(data.secret);
      setQrCodeUri(data.qr_code_uri);
      setShow2FAFlow(true);
      addToast('2FA Secret generated. Verify to complete.', 'info');
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Failed to setup 2FA', 'error');
    },
  });

  // Verify 2FA Mutation
  const verify2FAMutation = useMutation({
    mutationFn: async (verifyCode: string) => {
      return await client.post('/auth/2fa/verify', { code: verifyCode });
    },
    onSuccess: () => {
      addToast('2FA setup complete!', 'success');
      setShow2FAFlow(false);
      setCode('');
      fetchProfile(); // refresh local profile
    },
    onError: (err: any) => {
      addToast(err.response?.data?.detail || 'Verification failed', 'error');
    },
  });

  // Disable 2FA Mutation
  const disable2FAMutation = useMutation({
    mutationFn: async () => {
      return await client.post('/auth/2fa/disable');
    },
    onSuccess: () => {
      addToast('Two-factor authentication disabled', 'warning');
      fetchProfile();
    },
  });

  const handleVerifySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!code) return;
    verify2FAMutation.mutate(code);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
          Adjust security parameters, set up 2FA, and configure global variables.
        </p>
      </div>

      <div className="max-w-3xl space-y-6">
        {/* Security / 2FA Panel */}
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-slate-50 dark:bg-dark-input rounded-xl text-primary-500">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div className="flex-1 space-y-1">
              <h2 className="font-bold text-slate-800 dark:text-white text-base">Two-Factor Authentication</h2>
              <p className="text-xs text-slate-500 dark:text-dark-text-muted leading-relaxed">
                Add an extra layer of security to your admin account by requiring a verification code from your authenticator app.
              </p>
              
              <div className="pt-4">
                {profile?.totp_enabled ? (
                  <button
                    onClick={() => {
                      if (confirm('Disable Two-Factor Authentication?')) {
                        disable2FAMutation.mutate();
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-rose-50 hover:bg-rose-100 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400 text-xs font-bold rounded-xl transition-colors"
                  >
                    Disable 2FA Protection
                  </button>
                ) : (
                  <button
                    onClick={() => setup2FAMutation.mutate()}
                    disabled={setup2FAMutation.isPending}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-xs font-bold rounded-xl transition-colors shadow-md shadow-primary-600/10"
                  >
                    {setup2FAMutation.isPending ? <Loader className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                    Setup 2FA Protection
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 2FA Setup Flow Card */}
        {show2FAFlow && (
          <div className="bg-white dark:bg-dark-card border border-primary-500/30 rounded-2xl p-6 shadow-md space-y-6">
            <h3 className="font-bold text-slate-800 dark:text-white text-sm uppercase tracking-wider">Configure Authenticator</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="space-y-4">
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  1. Scan the QR code or enter the secret key manually into Google Authenticator or Authy.
                </p>
                <div className="bg-slate-50 dark:bg-dark-input/50 p-4 rounded-xl border border-slate-200/50 dark:border-dark-border/50 space-y-1.5">
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Secret Key</span>
                  <code className="text-xs font-mono font-bold select-all break-all block">{totpSecret}</code>
                </div>
              </div>
              <div className="flex justify-center border border-slate-100 dark:border-dark-border/40 p-4 rounded-xl max-w-[200px] mx-auto bg-white">
                {/* Fallback info when QR cannot render */}
                <div className="text-center space-y-1">
                  <Key className="w-8 h-8 text-primary-500 mx-auto" />
                  <p className="text-[10px] font-bold text-slate-500">QR Code</p>
                  <p className="text-[9px] text-slate-400 select-all font-mono break-all">{qrCodeUri}</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleVerifySubmit} className="border-t border-slate-100 dark:border-dark-border/40 pt-6 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  2. Enter 6-digit Authenticator Code to verify
                </label>
                <input
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="000000"
                  maxLength={6}
                  className="w-full max-w-[200px] px-4 py-2.5 bg-slate-50 dark:bg-dark-input border border-slate-200 dark:border-dark-border rounded-xl focus:outline-none focus:border-primary-500 text-sm dark:text-slate-100 tracking-[0.25em] font-semibold text-center"
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={verify2FAMutation.isPending}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm rounded-xl transition-colors"
                >
                  Verify & Enable
                </button>
                <button
                  type="button"
                  onClick={() => setShow2FAFlow(false)}
                  className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm rounded-xl transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
export default Settings;
